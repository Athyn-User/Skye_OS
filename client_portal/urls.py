from django.urls import path
from . import views

app_name = 'client_portal'

urlpatterns = [
    # Authentication
    path('login/', views.client_login_view, name='login'),
    path('logout/', views.client_logout_view, name='logout'),
    
    # Dashboard
    path('', views.dashboard_view, name='dashboard'),
    
    # Policies/Quotes
    path('policies/', views.policies_view, name='policies'),
    
    # Certificates
    path('certificates/', views.certificates_view, name='certificates'),
    
    # Claims
    path('claims/', views.claims_view, name='claims'),
    path('claims/<int:claim_id>/', views.claim_detail_view, name='claim_detail'),
    path('claims/submit/', views.submit_claim_view, name='submit_claim'),
    
    # Documents
    path('documents/', views.documents_view, name='documents'),
    path('documents/<int:document_id>/download/', views.download_document_view, name='download_document'),
    path('documents/upload/', views.upload_document_view, name='upload_document'),
    path('documents/<int:document_id>/remove/', views.remove_document_view, name='remove_document'),
    path('documents/portal/', views.portal_documents_view, name='portal_documents'),
    
    # Payments
    path('payments/', views.payments_view, name='payments'),
    path('payments/<int:payment_id>/pay/', views.make_payment_view, name='make_payment'),
    
    # Profile
    path('profile/', views.profile_view, name='profile'),
]
