from django.contrib import admin
from .models import Candidate


@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'created_at')
    search_fields = ('name', 'email', 'skills_raw')
    readonly_fields = ('raw_text', 'created_at', 'updated_at')
