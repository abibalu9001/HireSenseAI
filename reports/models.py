from django.db import models
from django.contrib.auth.models import User
from jobs.models import JobDescription


class HiringReport(models.Model):
    job = models.ForeignKey(
        JobDescription, on_delete=models.CASCADE, related_name='reports'
    )
    generated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name='reports'
    )
    pdf_file = models.FileField(upload_to='reports/', blank=True, null=True)
    top_n_candidates = models.IntegerField(default=10)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report: {self.job.title} ({self.created_at.strftime('%Y-%m-%d')})"

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Hiring Report'
        verbose_name_plural = 'Hiring Reports'
