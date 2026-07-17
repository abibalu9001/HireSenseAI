from django.urls import path
from . import views

urlpatterns = [
    path('run/<int:candidate_id>/<int:job_id>/', views.run_analysis, name='run_analysis'),
    path('<int:pk>/', views.analysis_detail, name='analysis_detail'),
]
