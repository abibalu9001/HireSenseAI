from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('recruiter', 'Recruiter'),
        ('admin', 'Admin'),
        ('hr_manager', 'HR Manager'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='recruiter')
    company = models.CharField(max_length=200, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.role})"

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
