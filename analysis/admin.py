from django.contrib import admin
from .models import ResumeAnalysis, InterviewQuestion


class InterviewQuestionInline(admin.TabularInline):
    model = InterviewQuestion
    extra = 0
    fields = ('question', 'category', 'difficulty', 'skill_tag')


@admin.register(ResumeAnalysis)
class ResumeAnalysisAdmin(admin.ModelAdmin):
    list_display = ('candidate', 'job', 'total_score', 'skills_score', 'similarity_score', 'created_at')
    list_filter = ('job',)
    search_fields = ('candidate__name', 'job__title')
    readonly_fields = ('created_at',)
    inlines = [InterviewQuestionInline]


@admin.register(InterviewQuestion)
class InterviewQuestionAdmin(admin.ModelAdmin):
    list_display = ('question', 'category', 'difficulty', 'skill_tag', 'analysis')
    list_filter = ('category', 'difficulty')
