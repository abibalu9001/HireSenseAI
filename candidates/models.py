from django.db import models


class Candidate(models.Model):
    name = models.CharField(max_length=200, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    resume_file = models.FileField(upload_to='resumes/')
    raw_text = models.TextField(blank=True, help_text="Full extracted text from resume")
    # Parsed fields (stored as comma-separated or text)
    skills_raw = models.TextField(blank=True)
    education_raw = models.TextField(blank=True)
    experience_raw = models.TextField(blank=True)
    projects_raw = models.TextField(blank=True)
    
    # Fraud Detection fields
    fraud_score = models.IntegerField(default=0)
    fraud_flags_raw = models.TextField(blank=True, help_text="Comma-separated fraud warning flags")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def get_skills(self):
        if self.skills_raw:
            return [s.strip() for s in self.skills_raw.split(',') if s.strip()]
        return []

    def get_fraud_flags(self):
        if self.fraud_flags_raw:
            return [f.strip() for f in self.fraud_flags_raw.split('|') if f.strip()]
        return []


    def __str__(self):
        return self.name or f"Candidate #{self.pk}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Candidate'
        verbose_name_plural = 'Candidates'
