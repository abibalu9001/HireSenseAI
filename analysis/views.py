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
    tier_label, tier_class = get_tier(analysis.total_score)

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
