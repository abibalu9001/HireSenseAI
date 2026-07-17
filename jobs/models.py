from django.db import models
from django.contrib.auth.models import User
import json


class JobDescription(models.Model):
    EXPERIENCE_CHOICES = [
        (0, 'Entry Level (0-1 years)'),
        (1, 'Junior (1-3 years)'),
        (3, 'Mid-Level (3-5 years)'),
        (5, 'Senior (5-8 years)'),
        (8, 'Lead (8+ years)'),
    ]

    EDUCATION_CHOICES = [
        ('any', 'Any'),
        ('diploma', 'Diploma'),
        ('bachelors', "Bachelor's Degree"),
        ('masters', "Master's Degree"),
        ('phd', 'PhD'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    required_skills_raw = models.TextField(
        blank=True, help_text="Comma-separated skills extracted by AI"
    )
    experience_years = models.IntegerField(choices=EXPERIENCE_CHOICES, default=0)
    education_level = models.CharField(
        max_length=20, choices=EDUCATION_CHOICES, default='any'
    )
    jd_file = models.FileField(upload_to='jd_files/', blank=True, null=True)
    uploaded_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name='job_descriptions'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_required_skills(self):
        if self.required_skills_raw:
            return [s.strip() for s in self.required_skills_raw.split(',') if s.strip()]
        return []

    def set_required_skills(self, skills_list):
        self.required_skills_raw = ', '.join(skills_list)

    @property
    def candidate_count(self):
        return self.analyses.count()

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Job Description'
        verbose_name_plural = 'Job Descriptions'
        ordering = ['-created_at']
