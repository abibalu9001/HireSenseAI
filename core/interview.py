"""
Rule-based interview question generator.
Generates questions based on matched skills, missing skills,
and candidate profile.
"""

# Question bank per skill/category
SKILL_QUESTIONS = {
    "Python": [
        ("Explain the difference between a list and a tuple in Python.", "technical", "medium", "Python"),
        ("What are Python decorators and how do you use them?", "technical", "medium", "Python"),
        ("How does Python's GIL affect multithreading?", "technical", "hard", "Python"),
        ("What is the difference between @staticmethod and @classmethod?", "technical", "medium", "Python"),
    ],
    "Django": [
        ("Explain the Django MVT architecture.", "technical", "easy", "Django"),
        ("How does Django's ORM handle database migrations?", "technical", "medium", "Django"),
        ("What is the difference between select_related and prefetch_related?", "technical", "hard", "Django"),
        ("How do you implement authentication in Django?", "technical", "medium", "Django"),
    ],
    "React": [
        ("What are React hooks and why were they introduced?", "technical", "medium", "React"),
        ("Explain the Virtual DOM and how React uses it.", "technical", "easy", "React"),
        ("What is the difference between useEffect and useLayoutEffect?", "technical", "hard", "React"),
        ("How do you manage global state in a React application?", "technical", "medium", "React"),
    ],
    "Machine Learning": [
        ("Explain the bias-variance tradeoff.", "technical", "medium", "Machine Learning"),
        ("What is overfitting and how do you prevent it?", "technical", "easy", "Machine Learning"),
        ("Explain the difference between supervised and unsupervised learning.", "technical", "easy", "Machine Learning"),
        ("How does gradient descent work?", "technical", "medium", "Machine Learning"),
    ],
    "SQL": [
        ("What is the difference between INNER JOIN and LEFT JOIN?", "technical", "easy", "SQL"),
        ("Explain database normalization and its forms.", "technical", "medium", "SQL"),
        ("How would you optimize a slow SQL query?", "technical", "hard", "SQL"),
        ("What are window functions in SQL?", "technical", "hard", "SQL"),
    ],
    "Docker": [
        ("What is the difference between a Docker image and a container?", "technical", "easy", "Docker"),
        ("Explain Docker Compose and when you would use it.", "technical", "medium", "Docker"),
        ("How do you reduce the size of a Docker image?", "technical", "medium", "Docker"),
    ],
    "AWS": [
        ("Explain the difference between EC2 and Lambda.", "technical", "easy", "AWS"),
        ("What is S3 and what use cases is it good for?", "technical", "easy", "AWS"),
        ("How does auto-scaling work in AWS?", "technical", "medium", "AWS"),
    ],
    "default": [
        ("Tell me about a challenging project you worked on and how you overcame obstacles.", "behavioral", "medium", ""),
        ("Describe a situation where you had to learn a new technology quickly.", "behavioral", "medium", ""),
        ("How do you approach debugging a complex issue?", "behavioral", "easy", ""),
        ("Where do you see yourself in 5 years?", "behavioral", "easy", ""),
        ("How do you handle tight deadlines and pressure?", "situational", "medium", ""),
        ("Describe your experience working in an Agile/Scrum team.", "experience", "easy", ""),
        ("What is your approach to writing clean, maintainable code?", "technical", "easy", ""),
        ("How do you keep yourself updated with the latest technologies?", "behavioral", "easy", ""),
    ],
}

# Questions for missing skills (gap-focused)
MISSING_SKILL_QUESTIONS = {
    "Python": ("Are you open to learning Python? Have you had any exposure to it?", "technical", "easy"),
    "Docker": ("Have you worked with containerization technologies? How do you plan to learn Docker?", "technical", "easy"),
    "AWS": ("Have you worked with any cloud platforms? What is your approach to learning cloud services?", "technical", "easy"),
    "Machine Learning": ("Do you have any experience with data analysis or statistical modelling?", "technical", "medium"),
    "default": ("This role requires {skill}. Can you share your experience or plans to acquire this skill?", "technical", "easy"),
}


def generate_questions(matched_skills, missing_skills, max_questions=10):
    """
    Generate interview questions based on matched and missing skills.

    Args:
        matched_skills: list of skills the candidate has
        missing_skills: list of skills the JD requires but candidate lacks
        max_questions: maximum number of questions to return

    Returns:
        list of dicts: {question, category, difficulty, skill_tag}
    """
    questions = []
    seen_questions = set()

    # Questions for matched skills (assess depth)
    for skill in matched_skills[:5]:
        bank = SKILL_QUESTIONS.get(skill, [])
        for q_tuple in bank[:2]:  # max 2 per skill
            q_text, cat, diff, tag = q_tuple
            if q_text not in seen_questions:
                questions.append({
                    'question': q_text,
                    'category': cat,
                    'difficulty': diff,
                    'skill_tag': tag,
                })
                seen_questions.add(q_text)

    # Questions for missing skills (assess potential/gap)
    for skill in missing_skills[:3]:
        template = MISSING_SKILL_QUESTIONS.get(
            skill, MISSING_SKILL_QUESTIONS['default']
        )
        q_text, cat, diff = template
        q_text = q_text.format(skill=skill)
        if q_text not in seen_questions:
            questions.append({
                'question': q_text,
                'category': cat,
                'difficulty': diff,
                'skill_tag': skill,
            })
            seen_questions.add(q_text)

    # Fill remaining slots with behavioral / default questions
    for q_tuple in SKILL_QUESTIONS['default']:
        if len(questions) >= max_questions:
            break
        q_text, cat, diff, tag = q_tuple
        if q_text not in seen_questions:
            questions.append({
                'question': q_text,
                'category': cat,
                'difficulty': diff,
                'skill_tag': tag,
            })
            seen_questions.add(q_text)

    return questions[:max_questions]
