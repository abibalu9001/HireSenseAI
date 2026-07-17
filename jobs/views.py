from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import JobDescription
from .forms import JobDescriptionForm
from core.parser import extract_text, parse_job_description
from core.nlp import extract_skills


@login_required
def job_list(request):
    jobs = JobDescription.objects.filter(is_active=True).order_by('-created_at')
    return render(request, 'jobs/list.html', {'jobs': jobs})


@login_required
def job_create(request):
    if request.method == 'POST':
        form = JobDescriptionForm(request.POST, request.FILES)
        if form.is_valid():
            job = form.save(commit=False)
            job.uploaded_by = request.user

            # Extract text and skills from JD
            jd_text = job.description
            if job.jd_file:
                file_text = extract_text(job.jd_file)
                if file_text:
                    jd_text = file_text
                    job.description = file_text

            # Auto-extract required skills
            parsed = parse_job_description(jd_text)
            skills_text = parsed.get('skills_text', '') or jd_text
            extracted_skills = extract_skills(skills_text)
            job.set_required_skills(extracted_skills)

            job.save()
            messages.success(request, f'Job "{job.title}" created successfully!')
            return redirect('job_detail', pk=job.pk)
    else:
        form = JobDescriptionForm()
    return render(request, 'jobs/create.html', {'form': form})


@login_required
def job_detail(request, pk):
    job = get_object_or_404(JobDescription, pk=pk)
    analyses = job.analyses.select_related('candidate').order_by('-total_score')
    return render(request, 'jobs/detail.html', {
        'job': job,
        'analyses': analyses,
        'required_skills': job.get_required_skills(),
    })


@login_required
def job_delete(request, pk):
    job = get_object_or_404(JobDescription, pk=pk)
    if request.method == 'POST':
        title = job.title
        job.is_active = False
        job.save()
        messages.success(request, f'Job "{title}" has been archived.')
        return redirect('job_list')
    return render(request, 'jobs/confirm_delete.html', {'job': job})
