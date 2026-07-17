from django.db import models
from candidates.models import Candidate
from jobs.models import JobDescription


class ResumeAnalysis(models.Model):
    candidate = models.ForeignKey(
        Candidate, on_delete=models.CASCADE, related_name='analyses'
    )
    job = models.ForeignKey(
        JobDescription, on_delete=models.CASCADE, related_name='analyses'
    )
    # Scores (0-100)
    total_score = models.FloatField(default=0)
    similarity_score = models.FloatField(default=0, help_text="Semantic similarity 0-100")
    skills_score = models.FloatField(default=0)
    experience_score = models.FloatField(default=0)
    education_score = models.FloatField(default=0)
    projects_score = models.FloatField(default=0)

    # Matched / Missing skills (comma-separated)
    matched_skills_raw = models.TextField(blank=True)
    missing_skills_raw = models.TextField(blank=True)

    # Suggestions
    suggestions = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def get_matched_skills(self):
        if self.matched_skills_raw:
            return [s.strip() for s in self.matched_skills_raw.split(',') if s.strip()]
        return []

    def get_missing_skills(self):
        if self.missing_skills_raw:
            return [s.strip() for s in self.missing_skills_raw.split(',') if s.strip()]
        return []

    def get_suggestions_list(self):
        if self.suggestions:
            return [s.strip() for s in self.suggestions.split('\n') if s.strip()]
        return []

    def get_score_breakdown(self):
        return {
            'Skills Match': round(self.skills_score, 1),
            'Semantic Similarity': round(self.similarity_score, 1),
            'Experience': round(self.experience_score, 1),
            'Education': round(self.education_score, 1),
            'Projects': round(self.projects_score, 1),
        }

    class Meta:
        ordering = ['-total_score']
        verbose_name = 'Resume Analysis'
        verbose_name_plural = 'Resume Analyses'
        unique_together = ('candidate', 'job')

    def __str__(self):
        return f"{self.candidate} → {self.job} ({self.total_score:.1f}%)"


class InterviewQuestion(models.Model):
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]
    CATEGORY_CHOICES = [
        ('technical', 'Technical'),
        ('behavioral', 'Behavioral'),
        ('situational', 'Situational'),
        ('experience', 'Experience'),
    ]

    analysis = models.ForeignKey(
        ResumeAnalysis, on_delete=models.CASCADE, related_name='questions'
    )
    question = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='technical')
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default='medium')
    skill_tag = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"[{self.category}] {self.question[:60]}..."

    class Meta:
        verbose_name = 'Interview Question'
        verbose_name_plural = 'Interview Questions'
