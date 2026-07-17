from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing, name='landing'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('toggle-anonymous/', views.toggle_anonymous, name='toggle_anonymous'),
]

