from django.contrib import admin
from .models import JobDescription


@admin.register(JobDescription)
class JobDescriptionAdmin(admin.ModelAdmin):
    list_display = ('title', 'uploaded_by', 'experience_years', 'education_level', 'candidate_count', 'is_active', 'created_at')
    list_filter = ('is_active', 'education_level', 'experience_years')
    search_fields = ('title', 'description')
    readonly_fields = ('created_at', 'updated_at')
