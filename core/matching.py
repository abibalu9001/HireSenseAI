"""
Semantic matching module — Sentence Transformers cosine similarity
+ explainable scoring algorithm.
"""

import logging
from core.nlp import extract_skills, extract_years_of_experience, extract_education_level, EDUCATION_RANK

logger = logging.getLogger(__name__)

# Lazy-load sentence transformer
_model = None


def get_model():
    global _model
    if _model is None:
        try:
            from sentence_transformers import SentenceTransformer
            _model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("Sentence Transformer loaded successfully")
        except Exception as e:
            logger.warning(f"Could not load Sentence Transformer: {e}")
            _model = False
    return _model


def compute_semantic_similarity(text1, text2):
    """
    Compute cosine similarity between two texts using Sentence Transformers.
    Returns a score between 0 and 100.
    """
    if not text1 or not text2:
        return 0.0

    model = get_model()
    if not model:
        # Fallback: keyword overlap ratio
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        if not words1 or not words2:
            return 0.0
        overlap = len(words1 & words2) / len(words1 | words2)
        return round(overlap * 100, 2)

    try:
        from sklearn.metrics.pairwise import cosine_similarity
        import numpy as np
        emb1 = model.encode([text1])
        emb2 = model.encode([text2])
        score = cosine_similarity(emb1, emb2)[0][0]
        return round(float(score) * 100, 2)
    except Exception as e:
        logger.error(f"Similarity computation failed: {e}")
        return 0.0


def compute_skills_score(candidate_skills, required_skills):
    """
    Compute skills match score.
    Returns: score (0-100), matched_skills list, missing_skills list
    """
    if not required_skills:
        return 50.0, list(candidate_skills), []

    candidate_lower = {s.lower() for s in candidate_skills}
    required_lower = {s.lower() for s in required_skills}

    matched = [s for s in required_skills if s.lower() in candidate_lower]
    missing = [s for s in required_skills if s.lower() not in candidate_lower]

    score = (len(matched) / len(required_skills)) * 100
    return round(score, 2), matched, missing


def compute_experience_score(candidate_text, required_years):
    """Score candidate experience vs JD requirement."""
    if required_years == 0:
        return 80.0  # No requirement = decent score

    candidate_years = extract_years_of_experience(candidate_text)

    if candidate_years >= required_years:
        # Bonus for extra experience, capped at 100
        bonus = min((candidate_years - required_years) * 5, 20)
        return min(100.0, 80.0 + bonus)
    else:
        # Proportional score
        ratio = candidate_years / required_years
        return round(ratio * 80, 2)


def compute_education_score(candidate_edu_text, required_edu_level):
    """Score candidate education vs JD requirement."""
    candidate_level = extract_education_level(candidate_edu_text)
    required_rank = EDUCATION_RANK.get(required_edu_level, 0)
    candidate_rank = EDUCATION_RANK.get(candidate_level, 0)

    if candidate_rank >= required_rank:
        bonus = min((candidate_rank - required_rank) * 10, 20)
        return min(100.0, 80.0 + bonus)
    else:
        ratio = candidate_rank / max(required_rank, 1)
        return round(ratio * 80, 2)


def compute_projects_score(projects_text):
    """Score based on presence and richness of projects section."""
    if not projects_text or len(projects_text.strip()) < 50:
        return 10.0
    words = len(projects_text.split())
    if words > 300:
        return 100.0
    elif words > 150:
        return 80.0
    elif words > 80:
        return 60.0
    elif words > 30:
        return 40.0
    return 20.0


def compute_score(resume_data, jd_data):
    """
    Compute full explainable score for a candidate against a job description.

    Args:
        resume_data: dict with keys: raw_text, skills_text, education_text,
                     experience_text, projects_text, skills (list)
        jd_data: dict with keys: raw_text, required_skills (list),
                 experience_years (int), education_level (str)

    Returns:
        dict: total_score, similarity_score, skills_score, experience_score,
              education_score, projects_score, matched_skills, missing_skills
    """
    # Weights (must sum to 100)
    WEIGHTS = {
        'similarity':  0.30,
        'skills':      0.35,
        'experience':  0.15,
        'education':   0.10,
        'projects':    0.10,
    }

    # 1. Semantic similarity
    similarity = compute_semantic_similarity(
        resume_data.get('raw_text', ''),
        jd_data.get('raw_text', '')
    )

    # 2. Skills score
    candidate_skills = resume_data.get('skills', [])
    required_skills = jd_data.get('required_skills', [])
    skills_score, matched_skills, missing_skills = compute_skills_score(
        candidate_skills, required_skills
    )

    # 3. Experience score
    experience_score = compute_experience_score(
        resume_data.get('experience_text', '') + ' ' + resume_data.get('raw_text', ''),
        jd_data.get('experience_years', 0)
    )

    # 4. Education score
    education_score = compute_education_score(
        resume_data.get('education_text', ''),
        jd_data.get('education_level', 'any')
    )

    # 5. Projects score
    projects_score = compute_projects_score(resume_data.get('projects_text', ''))

    # Weighted total
    total_score = (
        similarity   * WEIGHTS['similarity'] +
        skills_score * WEIGHTS['skills'] +
        experience_score * WEIGHTS['experience'] +
        education_score  * WEIGHTS['education'] +
        projects_score   * WEIGHTS['projects']
    )

    return {
        'total_score':       round(total_score, 2),
        'similarity_score':  similarity,
        'skills_score':      skills_score,
        'experience_score':  experience_score,
        'education_score':   education_score,
        'projects_score':    projects_score,
        'matched_skills':    matched_skills,
        'missing_skills':    missing_skills,
    }
