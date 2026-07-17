from django.contrib import admin
from .models import HiringReport


@admin.register(HiringReport)
class HiringReportAdmin(admin.ModelAdmin):
    list_display = ('job', 'generated_by', 'top_n_candidates', 'created_at')
    search_fields = ('job__title',)
    readonly_fields = ('created_at',)
