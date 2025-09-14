# Skye_OS/urls.py

from django.urls import path
from . import views

app_name = 'Skye_OS'

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('catalog/', views.catalog_view, name='catalog'),
    path('machine-learning/', views.machine_learning_view, name='machine_learning'),
    
    # API endpoints
    path('api/ventures/', views.venture_api, name='venture_api'),
]