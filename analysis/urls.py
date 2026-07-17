from django.urls import path
from . import views

urlpatterns = [
    path('run/<int:candidate_id>/<int:job_id>/', views.run_analysis, name='run_analysis'),
    path('<int:pk>/', views.analysis_detail, name='analysis_detail'),
    path('compare/', views.compare_analyses, name='compare_analyses'),
    path('copilot-chat/<int:job_id>/', views.copilot_chat, name='copilot_chat'),
    path('<int:pk>/feedback/', views.update_analysis_feedback, name='update_analysis_feedback'),
]



