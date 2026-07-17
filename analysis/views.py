from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import ResumeAnalysis, InterviewQuestion
from candidates.models import Candidate
from jobs.models import JobDescription
from core.matching import compute_score
from core.nlp import extract_skills
from core.interview import generate_questions
from core.resume_improvement import get_suggestions
from core.ranking import get_tier, rank_candidates


@login_required
def run_analysis(request, candidate_id, job_id):
    """Run AI analysis for a candidate against a job description."""
    candidate = get_object_or_404(Candidate, pk=candidate_id)
    job = get_object_or_404(JobDescription, pk=job_id)

    # Re-run fraud detection if not already analyzed
    if candidate.fraud_score == 0 and not candidate.fraud_flags_raw:
        from core.parser import detect_resume_fraud
        fraud_score, fraud_flags = detect_resume_fraud(candidate.raw_text, candidate.experience_raw)
        candidate.fraud_score = fraud_score
        candidate.fraud_flags_raw = '|'.join(fraud_flags)
        candidate.save()


    # Prepare data dicts
    resume_data = {
        'raw_text': candidate.raw_text,
        'skills': candidate.get_skills(),
        'skills_text': candidate.skills_raw,
        'education_text': candidate.education_raw,
        'experience_text': candidate.experience_raw,
        'projects_text': candidate.projects_raw,
    }
    jd_data = {
        'raw_text': job.description,
        'required_skills': job.get_required_skills(),
        'experience_years': job.experience_years,
        'education_level': job.education_level,
    }

    # Compute scores
    scores = compute_score(resume_data, jd_data)

    # Build suggestions
    score_breakdown = {
        'Skills Match': scores['skills_score'],
        'Semantic Similarity': scores['similarity_score'],
        'Experience': scores['experience_score'],
        'Education': scores['education_score'],
        'Projects': scores['projects_score'],
    }
    suggestions = get_suggestions(
        missing_skills=scores['missing_skills'],
        score_breakdown=score_breakdown,
        education_score=scores['education_score'],
        projects_score=scores['projects_score'],
    )

    # Save/update analysis
    analysis, created = ResumeAnalysis.objects.update_or_create(
        candidate=candidate,
        job=job,
        defaults={
            'total_score':       scores['total_score'],
            'similarity_score':  scores['similarity_score'],
            'skills_score':      scores['skills_score'],
            'experience_score':  scores['experience_score'],
            'education_score':   scores['education_score'],
            'projects_score':    scores['projects_score'],
            'matched_skills_raw': ', '.join(scores['matched_skills']),
            'missing_skills_raw': ', '.join(scores['missing_skills']),
            'suggestions':        '\n'.join(suggestions),
        }
    )

    # Generate and save interview questions
    analysis.questions.all().delete()
    questions = generate_questions(
        matched_skills=scores['matched_skills'],
        missing_skills=scores['missing_skills'],
    )
    InterviewQuestion.objects.bulk_create([
        InterviewQuestion(
            analysis=analysis,
            question=q['question'],
            category=q['category'],
            difficulty=q['difficulty'],
            skill_tag=q['skill_tag'],
        ) for q in questions
    ])

    action = 'created' if created else 'updated'
    messages.success(request, f'Analysis {action} — Score: {scores["total_score"]:.1f}%')
    return redirect('analysis_detail', pk=analysis.pk)


@login_required
def analysis_detail(request, pk):
    analysis = get_object_or_404(
        ResumeAnalysis.objects.select_related('candidate', 'job'), pk=pk
    )
    questions = analysis.questions.all()
    tier_label, tier_class = get_tier(analysis.final_score)


    # All analyses for the same job (for ranking/percentile)
    job_analyses = ResumeAnalysis.objects.filter(job=analysis.job)
    ranked = rank_candidates(job_analyses)
    rank = next((r for r, a in ranked if a.pk == analysis.pk), None)

    score_breakdown = analysis.get_score_breakdown()
    context = {
        'analysis': analysis,
        'questions': questions,
        'matched_skills': analysis.get_matched_skills(),
        'missing_skills': analysis.get_missing_skills(),
        'suggestions': analysis.get_suggestions_list(),
        'score_breakdown': score_breakdown,
        'score_labels': list(score_breakdown.keys()),
        'score_values': list(score_breakdown.values()),
        'tier_label': tier_label,
        'tier_class': tier_class,
        'rank': rank,
        'total_for_job': job_analyses.count(),
    }
    return render(request, 'analysis/detail.html', context)


@login_required
def compare_analyses(request):
    a1_id = request.GET.get('a1')
    a2_id = request.GET.get('a2')
    
    analysis1 = get_object_or_404(ResumeAnalysis.objects.select_related('candidate', 'job'), pk=a1_id)
    analysis2 = get_object_or_404(ResumeAnalysis.objects.select_related('candidate', 'job'), pk=a2_id)
    
    # Heuristic AI Verdict Comparison
    recs = []
    if abs(analysis1.final_score - analysis2.final_score) < 3:
        winner = None
        verdict = f"Both candidates are extremely close in overall matching score ({analysis1.final_score:.1f}% vs {analysis2.final_score:.1f}%). "
    else:
        winner = analysis1 if analysis1.final_score > analysis2.final_score else analysis2
        loser = analysis2 if analysis1.final_score > analysis2.final_score else analysis1
        verdict = f"**{winner.candidate.name}** is the stronger candidate overall with a match score of **{winner.final_score:.1f}%** compared to **{loser.candidate.name}** ({loser.final_score:.1f}%). "


    # Check key factors
    # 1. Skills
    skills_diff = len(analysis1.get_matched_skills()) - len(analysis2.get_matched_skills())
    if skills_diff > 0:
        recs.append(f"• **{analysis1.candidate.name}** matches more required skills ({len(analysis1.get_matched_skills())} vs {len(analysis2.get_matched_skills())}), notably: *{', '.join(analysis1.get_matched_skills()[:3])}*.")
    elif skills_diff < 0:
        recs.append(f"• **{analysis2.candidate.name}** matches more required skills ({len(analysis2.get_matched_skills())} vs {len(analysis1.get_matched_skills())}), notably: *{', '.join(analysis2.get_matched_skills()[:3])}*.")

    # 2. Experience
    exp_diff = analysis1.experience_score - analysis2.experience_score
    if exp_diff > 15:
        recs.append(f"• **{analysis1.candidate.name}** has a stronger experience record matching the job criteria.")
    elif exp_diff < -15:
        recs.append(f"• **{analysis2.candidate.name}** has a stronger experience record matching the job criteria.")

    # 3. Projects
    proj_diff = analysis1.projects_score - analysis2.projects_score
    if proj_diff > 20:
        recs.append(f"• **{analysis1.candidate.name}**'s projects section shows significantly greater detail and complexity.")
    elif proj_diff < -20:
        recs.append(f"• **{analysis2.candidate.name}**'s projects section shows significantly greater detail and complexity.")

    # Summary verdict
    if recs:
        verdict += "\n\nKey highlights:\n\n" + '\n'.join(recs)
    else:
        verdict += "Both candidates show similar performance across skills, experience, and projects."

    context = {
        'a1': analysis1,
        'a2': analysis2,
        'verdict': verdict,
        'job': analysis1.job,
    }
    return render(request, 'analysis/compare.html', context)


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import re

@csrf_exempt
@login_required
def copilot_chat(request, job_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=400)
    
    try:
        data = json.loads(request.body)
        query = data.get('message', '').strip()
    except Exception:
        query = request.POST.get('message', '').strip()
        
    if not query:
        return JsonResponse({'reply': 'Please type a question!'})

    job = get_object_or_404(JobDescription, pk=job_id)
    analyses = ResumeAnalysis.objects.filter(job=job).select_related('candidate').order_by('-total_score')
    
    query_lower = query.lower()
    reply = ""

    # Heuristic intent parser
    # 1. Intent: Recommendation
    if any(k in query_lower for k in ['recommend', 'top candidate', 'best candidate', 'who is the best', 'shortlist']):
        top_3 = list(analyses[:3])
        if not top_3:
            reply = "There are no evaluated candidates for this job yet. Please upload resumes and analyze them."
        else:
            reply = f"Here are the top candidates recommended for **{job.title}**:\n\n"
            for i, a in enumerate(top_3, 1):
                name = f"Candidate #{a.candidate.pk}" if request.session.get('anonymous_mode') else a.candidate.name
                reply += f"{i}. **{name}** — **{a.final_score:.1f}%** match (Status: *{a.status.title()}*). " \
                         f"Matches {len(a.get_matched_skills())} required skills.\n"
            reply += "\nI suggest inviting them for interviews."

    # 2. Intent: Candidate search by skills
    elif any(k in query_lower for k in ['who has', 'who knows', 'show candidates with', 'search skill', 'experience with']):
        # Find which skills are mentioned in the query
        from core.skills_data import SKILLS_LIST
        mentioned_skills = []
        for skill in SKILLS_LIST:
            if re.search(r'\b' + re.escape(skill.lower()) + r'\b', query_lower):
                mentioned_skills.append(skill)
        
        if not mentioned_skills:
            reply = "I couldn't identify specific technical skills in your query. Try asking: *'Who has Python and Docker experience?'*"
        else:
            results = []
            for a in analyses:
                c_skills = [s.lower() for s in a.candidate.get_skills()]
                matched = [s for s in mentioned_skills if s.lower() in c_skills]
                if len(matched) == len(mentioned_skills):
                    name = f"Candidate #{a.candidate.pk}" if request.session.get('anonymous_mode') else a.candidate.name
                    results.append(f"• **{name}** ({a.final_score:.1f}% Match) — Matched: {', '.join(matched)}")
            
            if results:
                reply = f"Found **{len(results)}** candidate(s) matching your skill criteria (*{', '.join(mentioned_skills)}*):\n\n" + '\n'.join(results)
            else:
                reply = f"No candidates currently match all requested skills: *{', '.join(mentioned_skills)}*."

    # 3. Intent: Comparison / "Why is X ranked below Y"
    elif 'instead of' in query_lower or 'ranked' in query_lower or 'why is' in query_lower:
        # Try to extract names
        matched_cand = []
        for a in analyses:
            if not request.session.get('anonymous_mode') and a.candidate.name and a.candidate.name.lower() in query_lower:
                matched_cand.append(a)
            elif f"candidate #{a.candidate.pk}" in query_lower or f"candidate #{a.candidate.pk}" == query_lower:
                matched_cand.append(a)
        
        if len(matched_cand) >= 2:
            a1, a2 = matched_cand[0], matched_cand[1]
            if a1.final_score < a2.final_score:
                a1, a2 = a2, a1 # a1 is higher
            
            name1 = f"Candidate #{a1.candidate.pk}" if request.session.get('anonymous_mode') else a1.candidate.name
            name2 = f"Candidate #{a2.candidate.pk}" if request.session.get('anonymous_mode') else a2.candidate.name
            
            diff_score = a1.final_score - a2.final_score
            reply = f"**{name1}** is ranked higher than **{name2}** by **{diff_score:.1f}%** due to:\n"
            
            # Key factors
            recs = []
            if len(a1.get_matched_skills()) > len(a2.get_matched_skills()):
                recs.append(f"• Matching more critical skills ({len(a1.get_matched_skills())} vs {len(a2.get_matched_skills())})")
            if a1.experience_score > a2.experience_score:
                recs.append("• More relevant years of work experience matching the criteria")
            if a1.projects_score > a2.projects_score:
                recs.append("• A more detailed and comprehensive projects section in their resume")
            
            if recs:
                reply += '\n'.join(recs)
            else:
                reply += "• Slightly higher semantic text match and profile alignment."
        elif len(matched_cand) == 1:
            a = matched_cand[0]
            # Compare to #1 rank
            top_a = analyses[0]
            if a.pk == top_a.pk:
                name = f"Candidate #{a.candidate.pk}" if request.session.get('anonymous_mode') else a.candidate.name
                reply = f"**{name}** is already the #1 ranked candidate for this job description!"
            else:
                name = f"Candidate #{a.candidate.pk}" if request.session.get('anonymous_mode') else a.candidate.name
                top_name = f"Candidate #{top_a.candidate.pk}" if request.session.get('anonymous_mode') else top_a.candidate.name
                diff_score = top_a.final_score - a.final_score
                
                reply = f"**{name}** is ranked below **{top_name}** (by **{diff_score:.1f}%**) because:\n"
                recs = []
                missing_in_lower = [s for s in top_a.get_matched_skills() if s not in a.get_matched_skills()]
                if missing_in_lower:
                    recs.append(f"• Lacks critical skills matched by {top_name}: *{', '.join(missing_in_lower[:3])}*")
                if top_a.experience_score > a.experience_score:
                    recs.append(f"• Lacks the matching years of experience compared to {top_name}")
                if top_a.projects_score > a.projects_score:
                    recs.append(f"• Has a lower projects section evaluation score")
                
                if recs:
                    reply += '\n'.join(recs)
                else:
                    reply += "• Slightly lower semantic text alignment score."
        else:
            reply = "I couldn't identify specific candidates in your ranking question. " \
                    "Try asking: *'Why is candidate #3 ranked below candidate #1?'* or *'Why is [Name] ranked #2 instead of #1?'*"

    # 4. Intent: Check individual candidate details
    else:
        # Check if query matches candidate detail query
        candidate_found = None
        for item in analyses:
            if not request.session.get('anonymous_mode') and item.candidate.name and item.candidate.name.lower() in query_lower:
                candidate_found = item
                break
            elif f"candidate #{item.candidate.pk}" in query_lower:
                candidate_found = item
                break
        
        if candidate_found:
            name = f"Candidate #{candidate_found.candidate.pk}" if request.session.get('anonymous_mode') else candidate_found.candidate.name
            if 'experience' in query_lower or 'work' in query_lower:
                reply = f"**{name}** has an Experience score of **{candidate_found.experience_score:.0f}/100**."
            elif 'skill' in query_lower:
                reply = f"**{name}** matches these required skills: *{', '.join(candidate_found.get_matched_skills())}*.\n\n" \
                        f"They lack: *{', '.join(candidate_found.get_missing_skills())}*."
            else:
                reply = f"**{name}** evaluation summary:\n" \
                        f"• **Overall Match**: {candidate_found.final_score:.1f}%\n" \
                        f"• **Skills**: {candidate_found.skills_score:.0f}%\n" \
                        f"• **Experience**: {candidate_found.experience_score:.0f}%\n" \
                        f"• **Projects**: {candidate_found.projects_score:.0f}%\n" \
                        f"• **Hiring Status**: {candidate_found.status.title()}"

    # 5. Default fallback
    if not reply:
        reply = "Hello! I am your AI Recruiter Copilot. I can help you evaluate candidates for this job description. You can ask me:\n\n" \
                "• *'Recommend the top candidates'* \n" \
                "• *'Who has Python and React experience?'* \n" \
                "• *'Why is Candidate #2 ranked below Candidate #1?'* \n" \
                "• *'Show candidates with AWS'* \n" \
                "• *'Compare Candidate #1 and Candidate #2'*"
                
    return JsonResponse({'reply': reply})



@login_required
def update_analysis_feedback(request, pk):
    if request.method != 'POST':
        return redirect('analysis_detail', pk=pk)
        
    analysis = get_object_or_404(ResumeAnalysis, pk=pk)
    
    status = request.POST.get('status', 'applied')
    override_score_str = request.POST.get('manual_score_override', '').strip()
    recruiter_notes = request.POST.get('recruiter_notes', '').strip()
    
    analysis.status = status
    analysis.recruiter_notes = recruiter_notes
    
    if override_score_str:
        try:
            override_score = float(override_score_str)
            if 0 <= override_score <= 100:
                analysis.manual_score_override = override_score
            else:
                messages.error(request, "Override score must be between 0 and 100.")
        except ValueError:
            messages.error(request, "Invalid override score format.")
    else:
        analysis.manual_score_override = None
        
    analysis.save()
    messages.success(request, "Candidate pipeline and recruiter overrides updated!")
    return redirect('analysis_detail', pk=pk)


