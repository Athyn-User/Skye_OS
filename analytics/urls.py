# analytics/urls.py

from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    path('', views.analytics_dashboard, name='dashboard'),
    path('revenue/', views.revenue_report, name='revenue_report'),
    path('claims/', views.claims_report, name='claims_report'),
    path('clients/', views.client_report, name='client_report'),
]