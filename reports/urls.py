from django.urls import path
from . import views

urlpatterns = [
    path('generate/<int:job_id>/', views.generate_report, name='generate_report'),
    path('<int:pk>/', views.report_detail, name='report_detail'),
    path('<int:pk>/download/', views.download_report, name='download_report'),
]
