# File: applications/urls.py
# Updated URL patterns with enhanced API endpoints

from django.urls import path
from . import views, document_views
from .certificate_views import certificate_list, certificate_detail, certificate_create, certificate_from_quote, certificate_pdf, certificate_issue, certificate_cancel, certificate_revise, certificate_email, certificate_pdf
from .policy_views import policy_list, policy_detail, policy_from_quote, policy_renew, renewal_dashboard, renewal_process, renewal_detail, renewal_accept
from .billing_views import billing_dashboard, payment_list, create_billing_schedule, record_payment, commission_report

app_name = 'applications'

urlpatterns = [
    # Existing URLs...
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
    
    # Certificate Management
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
    
    # Policy Management
    path('policies/', policy_list, name='policy_list'),
    path('policies/<int:policy_id>/', policy_detail, name='policy_detail'),
    path('quotes/<int:quote_id>/convert-to-policy/', policy_from_quote, name='policy_from_quote'),
    path('renewals/', renewal_dashboard, name='renewal_dashboard'),
    path('policies/<int:policy_id>/renew/', renewal_process, name='renewal_process'),
    path('renewals/<int:renewal_id>/', renewal_detail, name='renewal_detail'),
    path('renewals/<int:renewal_id>/accept/', renewal_accept, name='renewal_accept'),    
    
    # Billing Management
    path('billing/', billing_dashboard, name='billing_dashboard'),
    path('billing/payments/', payment_list, name='payment_list'),
    path('policies/<int:policy_id>/billing/create/', create_billing_schedule, name='create_billing_schedule'),
    path('billing/payments/<int:payment_id>/record/', record_payment, name='record_payment'),
    path('billing/commissions/', commission_report, name='commission_report'),
    
    # Document Management URLs - Basic Functions
    path('policies/<int:policy_id>/generate-documents/', 
         document_views.generate_policy_documents, 
         name='generate_policy_documents'),
    
    path('policies/<int:policy_id>/documents/', 
         document_views.view_policy_documents, 
         name='view_policy_documents'),
    
    path('documents/package/<int:package_id>/download/', 
         document_views.download_policy_package, 
         name='download_policy_package'),
    
    path('documents/templates/', 
         document_views.manage_templates, 
         name='manage_templates'),
    
    path('documents/templates/upload/', 
         document_views.upload_templates_page, 
         name='upload_templates_page'),
    
    path('documents/templates/bulk-upload/', 
         document_views.bulk_upload_templates, 
         name='bulk_upload_templates'),
    
    path('documents/templates/verify/', 
         document_views.verify_template_files, 
         name='verify_template_files'),
    
    path('documents/', 
         document_views.document_dashboard, 
         name='document_dashboard'),

    # Enhanced Document Management API Endpoints
    path('policies/<int:policy_id>/documents/status/', 
         document_views.get_document_status, 
         name='get_document_status'),
    
    path('policies/<int:policy_id>/components/<int:component_id>/regenerate/', 
         document_views.regenerate_component, 
         name='regenerate_component'),
    
    path('policies/<int:policy_id>/generate-missing/', 
         document_views.generate_missing_documents, 
         name='generate_missing_documents'),
    
    path('policies/<int:policy_id>/create-document-package/', 
         document_views.create_document_package, 
         name='create_document_package'),
    
    path('policies/<int:policy_id>/components/add/', 
         document_views.add_component, 
         name='add_component'),
    
    path('policies/<int:policy_id>/components/<int:component_id>/delete/', 
         document_views.delete_component, 
         name='delete_component'),
    
    path('documents/bulk-generate/', 
         document_views.bulk_document_generation, 
         name='bulk_document_generation'),
    
    path('documents/generate-from-template/', 
         document_views.generate_from_template, 
         name='generate_from_template'),
    
    path('documents/get-available-templates/', 
         document_views.get_available_templates, 
         name='get_available_templates'),
    
    path('documents/bulk/policies/', 
         document_views.get_bulk_policies, 
         name='get_bulk_policies'),

    # Component Management URLs
    path('documents/components/<int:component_id>/view/', 
         document_views.view_component, 
         name='view_component'),

    path('documents/components/<int:component_id>/replace/', 
         document_views.replace_component_file, 
         name='replace_component_file'),

    path('documents/components/<int:component_id>/history/', 
         document_views.component_version_history, 
         name='component_version_history'),

    # Advanced Document Operations
    path('policies/<int:policy_id>/documents/email/', 
         document_views.email_document_package, 
         name='email_document_package'),

    path('policies/<int:policy_id>/documents/merge/', 
         document_views.merge_document_packages, 
         name='merge_document_packages'),

    # Endorsement Management
    path('policies/<int:policy_id>/endorsements/create/', 
         document_views.create_endorsement, 
         name='create_endorsement'),
    
    path('policies/<int:policy_id>/endorsements/', 
         document_views.view_endorsements, 
         name='view_endorsements'),
    
    path('endorsements/<int:endorsement_id>/download/', 
         document_views.download_endorsement, 
         name='download_endorsement'),
    
    path('templates/<int:template_id>/upload/', 
         document_views.upload_template_file, 
         name='upload_template_file'),
]