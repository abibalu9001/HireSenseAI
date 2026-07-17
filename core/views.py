from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from candidates.models import Candidate
from jobs.models import JobDescription
from analysis.models import ResumeAnalysis


def landing(request):
    """Public landing page."""
    return render(request, 'landing.html')


@login_required
def dashboard(request):
    """Main dashboard with KPI stats and chart data."""
    total_candidates = Candidate.objects.count()
    total_jobs = JobDescription.objects.filter(is_active=True).count()
    total_analyses = ResumeAnalysis.objects.count()

    # Recent analyses for the table
    recent_analyses = ResumeAnalysis.objects.select_related(
        'candidate', 'job'
    ).order_by('-created_at')[:10]

    # Score distribution for chart
    analyses = ResumeAnalysis.objects.all()
    score_bins = {'0-20': 0, '21-40': 0, '41-60': 0, '61-80': 0, '81-100': 0}
    for a in analyses:
        s = a.total_score
        if s <= 20:   score_bins['0-20'] += 1
        elif s <= 40: score_bins['21-40'] += 1
        elif s <= 60: score_bins['41-60'] += 1
        elif s <= 80: score_bins['61-80'] += 1
        else:         score_bins['81-100'] += 1

    avg_score = (
        sum(a.total_score for a in analyses) / len(analyses)
        if analyses else 0
    )

    # Top jobs by candidate count
    top_jobs = JobDescription.objects.filter(is_active=True).order_by('-created_at')[:5]

    context = {
        'total_candidates': total_candidates,
        'total_jobs': total_jobs,
        'total_analyses': total_analyses,
        'avg_score': round(avg_score, 1),
        'recent_analyses': recent_analyses,
        'score_bins': score_bins,
        'top_jobs': top_jobs,
    }
    return render(request, 'dashboard.html', context)
