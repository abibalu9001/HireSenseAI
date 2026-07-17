"""
Resume improvement suggestions — rule-based engine that provides
actionable feedback based on missing skills and score breakdown.
"""

# Resource links for skill improvement
LEARNING_RESOURCES = {
    "Python": "https://docs.python.org/3/tutorial/",
    "Django": "https://docs.djangoproject.com/en/stable/intro/tutorial01/",
    "React": "https://react.dev/learn",
    "Docker": "https://docs.docker.com/get-started/",
    "AWS": "https://aws.amazon.com/getting-started/",
    "Machine Learning": "https://www.coursera.org/learn/machine-learning",
    "SQL": "https://www.w3schools.com/sql/",
    "Git": "https://git-scm.com/book/en/v2",
    "Kubernetes": "https://kubernetes.io/docs/tutorials/",
    "TypeScript": "https://www.typescriptlang.org/docs/",
    "Node.js": "https://nodejs.org/en/learn/getting-started/introduction-to-nodejs",
}


def get_suggestions(missing_skills, score_breakdown, education_score=None, projects_score=None):
    """
    Generate a list of improvement suggestions.

    Args:
        missing_skills: list of skills the candidate is missing
        score_breakdown: dict with category scores
        education_score: float (0-100)
        projects_score: float (0-100)

    Returns:
        list of suggestion strings
    """
    suggestions = []

    # Missing skills suggestions
    for skill in missing_skills[:8]:
        resource = LEARNING_RESOURCES.get(skill)
        if resource:
            suggestions.append(
                f"🔧 Learn {skill}: This skill is required for this role. "
                f"Start here: {resource}"
            )
        else:
            suggestions.append(
                f"🔧 Acquire {skill}: Build hands-on projects to demonstrate this skill."
            )

    # Low skills score
    skills_score = score_breakdown.get('Skills Match', 0)
    if skills_score < 50:
        suggestions.append(
            "📚 Expand your technical skill set — aim to match at least 70% "
            "of the required skills for this role."
        )

    # Low experience score
    exp_score = score_breakdown.get('Experience', 0)
    if exp_score < 50:
        suggestions.append(
            "💼 Gain more relevant work experience. Consider freelancing, "
            "internships, or contributing to open-source projects."
        )

    # Low education score
    if education_score is not None and education_score < 50:
        suggestions.append(
            "🎓 Consider pursuing a higher degree or relevant certifications "
            "to meet the educational requirements of this role."
        )

    # Low projects score
    if projects_score is not None and projects_score < 40:
        suggestions.append(
            "🚀 Add more projects to your resume. Build 2-3 solid portfolio "
            "projects that demonstrate your ability to apply your skills."
        )

    # Low semantic similarity
    sim_score = score_breakdown.get('Semantic Similarity', 0)
    if sim_score < 40:
        suggestions.append(
            "📝 Tailor your resume keywords to match the job description. "
            "Use the same terminology the JD uses for your skills and experience."
        )

    # Generic tips if few suggestions
    if len(suggestions) < 3:
        suggestions.extend([
            "✅ Quantify your achievements in your resume (e.g., 'Reduced API response time by 40%').",
            "✅ Add a strong professional summary at the top of your resume.",
            "✅ Ensure your GitHub profile showcases active, quality projects.",
        ])

    return suggestions
