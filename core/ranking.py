"""Candidate ranking — sorts analyses by total score, highest first."""


def rank_candidates(analyses_queryset):
    """
    Sort a queryset or list of ResumeAnalysis objects by final_score descending.
    Returns a list of (rank, analysis) tuples.
    """
    sorted_analyses = sorted(analyses_queryset, key=lambda a: a.final_score, reverse=True)
    return [(idx + 1, analysis) for idx, analysis in enumerate(sorted_analyses)]


def get_percentile(analysis, all_analyses):
    """
    Compute what percentile this candidate's score falls in (within the same job).
    Returns 0-100 float.
    """
    scores = [a.final_score for a in all_analyses]
    if not scores:
        return 0
    below = sum(1 for s in scores if s < analysis.final_score)
    return round((below / len(scores)) * 100, 1)



def get_tier(score):
    """Classify score into a tier label."""
    if score >= 80:
        return ('Excellent', 'success')
    elif score >= 65:
        return ('Good', 'info')
    elif score >= 50:
        return ('Average', 'warning')
    elif score >= 35:
        return ('Below Average', 'danger')
    else:
        return ('Poor', 'secondary')
