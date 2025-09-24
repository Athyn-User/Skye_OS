from django.urls import path
from . import views

app_name = 'claims'

urlpatterns = [
    # Dashboard
    path('', views.claims_dashboard, name='dashboard'),
    
    # Claim List and Detail
    path('list/', views.claim_list, name='claim_list'),
    path('<int:pk>/', views.claim_detail, name='claim_detail'),
    
    # Claim Creation and Updates
    path('fnol/', views.claim_fnol, name='claim_fnol'),
    path('<int:pk>/update/', views.claim_update, name='claim_update'),
    
    # Claim Actions
    path('<int:pk>/assign/', views.claim_assign_adjuster, name='claim_assign'),
    path('<int:pk>/approve/', views.claim_approve, name='claim_approve'),
    path('<int:pk>/deny/', views.claim_deny, name='claim_deny'),
    path('<int:pk>/close/', views.claim_close, name='claim_close'),
    path('<int:pk>/reopen/', views.claim_reopen, name='claim_reopen'),
    
    # Claim Components
    path('<int:pk>/note/add/', views.claim_add_note, name='claim_add_note'),
    path('<int:pk>/payment/add/', views.claim_add_payment, name='claim_add_payment'),
    path('<int:pk>/document/add/', views.claim_add_document, name='claim_add_document'),
    path('<int:pk>/reserve/adjust/', views.claim_adjust_reserve, name='claim_adjust_reserve'),
]
