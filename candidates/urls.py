from django.urls import path
from . import views

urlpatterns = [
    path('', views.candidate_list, name='candidate_list'),
    path('upload/', views.candidate_upload, name='candidate_upload'),
    path('<int:pk>/', views.candidate_detail, name='candidate_detail'),
    path('<int:pk>/delete/', views.candidate_delete, name='candidate_delete'),
]
