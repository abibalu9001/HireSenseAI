"""
NLP module — skill extraction using spaCy + skills dictionary,
and JD requirement parsing.
"""

import re
import logging
from core.skills_data import SKILLS_LIST, SKILLS_LOWER

logger = logging.getLogger(__name__)

# Lazy-load spaCy model to avoid slow startup
_nlp = None


def get_nlp():
    global _nlp
    if _nlp is None:
        try:
            import spacy
            _nlp = spacy.load("en_core_web_sm")
        except OSError:
            logger.warning("spaCy model 'en_core_web_sm' not found. Using basic extraction.")
            _nlp = False  # Mark as tried but failed
    return _nlp


def extract_skills(text):
    """
    Extract skills from text using:
    1. Direct dictionary lookup (case-insensitive, multi-word)
    2. spaCy NER for additional entities (if model is available)
    Returns a list of canonical skill names.
    """
    if not text:
        return []

    found = set()
    text_lower = text.lower()

    # Multi-word skills first (longer matches take priority)
    sorted_skills = sorted(SKILLS_LOWER.keys(), key=len, reverse=True)
    for skill_lower in sorted_skills:
        # Use word boundary matching to avoid partial matches
        pattern = r'\b' + re.escape(skill_lower) + r'\b'
        if re.search(pattern, text_lower):
            found.add(SKILLS_LOWER[skill_lower])

    return sorted(found)


def extract_years_of_experience(text):
    """Extract required years of experience from text."""
    patterns = [
        r'(\d+)\+?\s*years?\s+of\s+experience',
        r'(\d+)\+?\s*years?\s+experience',
        r'minimum\s+(\d+)\s+years?',
        r'at\s+least\s+(\d+)\s+years?',
        r'(\d+)-\d+\s+years?\s+of\s+experience',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return int(match.group(1))
    return 0


def extract_education_level(text):
    """Detect education level from text."""
    text_lower = text.lower()
    if any(kw in text_lower for kw in ['phd', 'doctorate', 'ph.d']):
        return 'phd'
    if any(kw in text_lower for kw in ["master's", "masters", "msc", "m.sc", "mba", "m.tech", "me "]):
        return 'masters'
    if any(kw in text_lower for kw in ["bachelor's", "bachelors", "b.sc", "bsc", "b.tech", "be ", "bca", "b.e."]):
        return 'bachelors'
    if any(kw in text_lower for kw in ['diploma', 'polytechnic']):
        return 'diploma'
    return 'any'


# Education level ordering for comparison
EDUCATION_RANK = {
    'any': 0, 'diploma': 1, 'bachelors': 2, 'masters': 3, 'phd': 4
}
