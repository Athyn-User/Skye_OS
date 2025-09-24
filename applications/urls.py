from django.urls import path
from . import views
from .certificate_views import certificate_list, certificate_detail, certificate_create, certificate_from_quote, certificate_pdf, certificate_issue, certificate_cancel, certificate_revise, certificate_email, certificate_pdf
from .policy_views import policy_list, policy_detail, policy_from_quote, policy_renew, renewal_dashboard, renewal_process, renewal_detail, renewal_accept
from .billing_views import billing_dashboard, payment_list, create_billing_schedule, record_payment, commission_report
from .billing_views import billing_dashboard, payment_list, create_billing_schedule, record_payment, commission_report

app_name = 'applications'
urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Applications
    path('applications/', views.application_list, name='application_list'),
    path('applications/create/', views.application_create, name='application_create'),
    path('applications/<int:pk>/', views.application_detail, name='application_detail'),
    path('applications/<int:pk>/edit/', views.application_edit, name='application_edit'),
    
    # Quotes
    path('quotes/', views.quote_list, name='quote_list'),
    path('applications/<int:application_pk>/quotes/create/', views.quote_create, name='quote_create'),
    path('quotes/<int:pk>/', views.quote_detail, name='quote_detail'),
    path('quotes/<int:pk>/edit/', views.quote_edit, name='quote_edit'),
    
    # PDF Generation
    path('quotes/<int:pk>/pdf/', views.quote_pdf, name='quote_pdf'),
    path('quotes/<int:pk>/pdf/view/', views.quote_pdf_view, name='quote_pdf_view'),
    path('quotes/<int:pk>/email/', views.quote_email_pdf, name='quote_email'),
    
    # Certificate Management (New System)
    path('certificates/', certificate_list, name='certificate_list'),
    path('certificates/<int:certificate_id>/', certificate_detail, name='certificate_detail'),
    path('certificates/<int:certificate_id>/pdf/', certificate_pdf, name='certificate_pdf'),
    path('certificates/<int:certificate_id>/issue/', certificate_issue, name='certificate_issue'),
    path('certificates/<int:certificate_id>/cancel/', certificate_cancel, name='certificate_cancel'),
    path('certificates/<int:certificate_id>/revise/', certificate_revise, name='certificate_revise'),
    path('certificates/<int:certificate_id>/email/', certificate_email, name='certificate_email'),
    path('certificates/create/', certificate_create, name='certificate_create'),
    path('certificates/from-quote/<int:quote_id>/', certificate_from_quote, name='certificate_from_quote'),
    
    # Companies
    path('companies/', views.company_list, name='company_list'),
    path('companies/create/', views.company_create, name='company_create'),
    path('companies/<int:pk>/', views.company_detail, name='company_detail'),    
    # Policy Management URLs
    path('policies/', policy_list, name='policy_list'),
    path('policies/<int:policy_id>/', policy_detail, name='policy_detail'),
    path('quotes/<int:quote_id>/convert-to-policy/', policy_from_quote, name='policy_from_quote'),
        path('renewals/', renewal_dashboard, name='renewal_dashboard'),
    path('policies/<int:policy_id>/renew/', renewal_process, name='renewal_process'),
    path('renewals/<int:renewal_id>/', renewal_detail, name='renewal_detail'),
    path('renewals/<int:renewal_id>/accept/', renewal_accept, name='renewal_accept'),    
    # Billing Management URLs
    path('billing/', billing_dashboard, name='billing_dashboard'),
    path('billing/payments/', payment_list, name='payment_list'),
    path('policies/<int:policy_id>/billing/create/', create_billing_schedule, name='create_billing_schedule'),
        path('billing/payments/<int:payment_id>/record/', record_payment, name='record_payment'),
    path('billing/commissions/', commission_report, name='commission_report'),
]



















