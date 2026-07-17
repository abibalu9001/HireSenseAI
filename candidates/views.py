from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Candidate
from .forms import ResumeUploadForm
from jobs.models import JobDescription
from core.parser import extract_text, parse_resume
from core.nlp import extract_skills


@login_required
def candidate_list(request):
    query = request.GET.get('q', '')
    sort = request.GET.get('sort', '-created_at')
    candidates = Candidate.objects.all()

    if query:
        from django.db.models import Q
        candidates = candidates.filter(
            Q(name__icontains=query) |
            Q(email__icontains=query) |
            Q(skills_raw__icontains=query)
        )

    valid_sorts = ['name', '-name', 'created_at', '-created_at', 'email']
    if sort in valid_sorts:
        candidates = candidates.order_by(sort)

    return render(request, 'candidates/list.html', {
        'candidates': candidates,
        'query': query,
        'sort': sort,
    })


@login_required
def candidate_upload(request):
    jobs = JobDescription.objects.filter(is_active=True).order_by('-created_at')
    if request.method == 'POST':
        form = ResumeUploadForm(request.POST, request.FILES)
        if form.is_valid():
            resume_file = request.FILES['resume_file']

            # Extract and parse
            raw_text = extract_text(resume_file)
            resume_file.seek(0)  # reset for saving

            parsed = parse_resume(raw_text)
            skills = extract_skills(raw_text)

            # Detect fraud
            from core.parser import detect_resume_fraud
            fraud_score, fraud_flags = detect_resume_fraud(raw_text, parsed.get('experience_text', ''))

            candidate = Candidate.objects.create(
                name=parsed.get('name', ''),
                email=parsed.get('email', ''),
                phone=parsed.get('phone', ''),
                resume_file=resume_file,
                raw_text=raw_text,
                skills_raw=', '.join(skills),
                education_raw=parsed.get('education_text', ''),
                experience_raw=parsed.get('experience_text', ''),
                projects_raw=parsed.get('projects_text', ''),
                fraud_score=fraud_score,
                fraud_flags_raw='|'.join(fraud_flags),
            )

            messages.success(request, f'Resume uploaded! Candidate: {candidate.name or "Unknown"}')

            # Auto-run analysis if job is selected
            job_id = form.cleaned_data.get('job')
            if job_id:
                return redirect('run_analysis', candidate_id=candidate.pk, job_id=job_id)
            return redirect('candidate_detail', pk=candidate.pk)
    else:
        form = ResumeUploadForm()

    return render(request, 'candidates/upload.html', {'form': form, 'jobs': jobs})


@login_required
def candidate_detail(request, pk):
    candidate = get_object_or_404(Candidate, pk=pk)
    analyses = candidate.analyses.select_related('job').order_by('-total_score')
    return render(request, 'candidates/detail.html', {
        'candidate': candidate,
        'analyses': analyses,
        'skills': candidate.get_skills(),
    })


@login_required
def candidate_delete(request, pk):
    candidate = get_object_or_404(Candidate, pk=pk)
    if request.method == 'POST':
        name = candidate.name
        candidate.delete()
        messages.success(request, f'Candidate "{name}" deleted.')
        return redirect('candidate_list')
    return render(request, 'candidates/confirm_delete.html', {'candidate': candidate})
