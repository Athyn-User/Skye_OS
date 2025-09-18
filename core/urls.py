# core/urls.py

from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Main pages
    path('', views.dashboard_view, name='dashboard'),
    path('catalog/', views.catalog_view, name='catalog'),
    
    # Machine Learning Hub
    path('machine-learning/', views.machine_learning_view, name='machine_learning'),
    
    # Data Seed URLs
    path('machine-learning/data-seeds/', views.data_seed_list, name='data_seed_list'),
    path('machine-learning/data-seeds/<int:pk>/', views.data_seed_detail, name='data_seed_detail'),
    # path('machine-learning/data-seeds/add/', views.data_seed_add, name='data_seed_add'),
    # path('machine-learning/data-seeds/<int:pk>/edit/', views.data_seed_edit, name='data_seed_edit'),
    
    # Generation Job URLs
    path('machine-learning/generation-jobs/', views.generation_job_list, name='generation_job_list'),
    path('machine-learning/generation-jobs/<int:pk>/', views.generation_job_detail, name='generation_job_detail'),
    # path('machine-learning/generation-jobs/add/', views.generation_job_add, name='generation_job_add'),
    # path('machine-learning/generation-jobs/<int:pk>/edit/', views.generation_job_edit, name='generation_job_edit'),
    
    # Generation Log URLs
    path('machine-learning/generation-logs/', views.generation_log_list, name='generation_log_list'),
    path('machine-learning/generation-logs/<int:pk>/', views.generation_log_detail, name='generation_log_detail'),
    # path('machine-learning/generation-logs/add/', views.generation_log_add, name='generation_log_add'),
    # path('machine-learning/generation-logs/<int:pk>/edit/', views.generation_log_edit, name='generation_log_edit'),
    
    # Model Parameter URLs
    path('machine-learning/model-parameters/', views.model_parameter_list, name='model_parameter_list'),
    path('machine-learning/model-parameters/<int:pk>/', views.model_parameter_detail, name='model_parameter_detail'),
    # path('machine-learning/model-parameters/add/', views.model_parameter_add, name='model_parameter_add'),
    # path('machine-learning/model-parameters/<int:pk>/edit/', views.model_parameter_edit, name='model_parameter_edit'),
    
    # Training Job URLs
    path('machine-learning/training-jobs/', views.training_job_list, name='training_job_list'),
    path('machine-learning/training-jobs/<int:pk>/', views.training_job_detail, name='training_job_detail'),
    # path('machine-learning/training-jobs/add/', views.training_job_add, name='training_job_add'),
    # path('machine-learning/training-jobs/<int:pk>/edit/', views.training_job_edit, name='training_job_edit'),
    
    # API endpoints
    path('api/ventures/', views.venture_api, name='venture_api'),

    # Employee Contact URLs
    path('employees/', views.employee_contact_list, name='employee_contact_list'),
    path('employees/<int:pk>/', views.employee_contact_detail, name='employee_contact_detail'),

# Products URLs  
    path('products/', views.products_list, name='products_list'),
    path('products/<int:pk>/', views.products_detail, name='products_detail'),

# Cover URLs
    path('coverage/', views.cover_list, name='cover_list'),
    path('coverage/<int:pk>/', views.cover_detail, name='cover_detail'),

# Employee Function URLs
    path('functions/', views.employee_function_list, name='employee_function_list'),
    path('functions/<int:pk>/', views.employee_function_detail, name='employee_function_detail'),

# Paper URLs
path('papers/', views.paper_list, name='paper_list'),
path('papers/<int:pk>/', views.paper_detail, name='paper_detail'),

# Paper Detail URLs  
path('paper-details/', views.paper_detail_list, name='paper_detail_list'),
path('paper-details/<int:pk>/', views.paper_detail_detail, name='paper_detail_detail'),

# Applications URLs
path('applications/', views.application_list, name='application_list'),
path('applications/<int:pk>/', views.application_detail, name='application_detail'),

# Application Question URLs
path('application-questions/', views.application_question_list, name='application_question_list'),
path('application-questions/<int:pk>/', views.application_question_detail, name='application_question_detail'),

# Parameter URLs
path('parameters/', views.parameter_list, name='parameter_list'),
path('parameters/<int:pk>/', views.parameter_detail, name='parameter_detail'),

# Parameter Map URLs  
path('parameter-maps/', views.parameter_map_list, name='parameter_map_list'),
path('parameter-maps/<int:pk>/', views.parameter_map_detail, name='parameter_map_detail'),

# Document URLs
path('documents/', views.document_list, name='document_list'),
path('documents/<int:pk>/', views.document_detail, name='document_detail'),

# Task URLs
path('tasks/', views.task_list, name='task_list'),
path('tasks/<int:pk>/', views.task_detail, name='task_detail'),

# Workflow URLs
path('workflows/', views.workflow_list, name='workflow_list'),
path('workflows/<int:pk>/', views.workflow_detail, name='workflow_detail'),

# Workflow Detail URLs  
path('workflow-details/', views.workflow_detail_list, name='workflow_detail_list'),
path('workflow-details/<int:pk>/', views.workflow_detail_detail, name='workflow_detail_detail'),

# Attachment URLs
path('attachments/', views.attachment_list, name='attachment_list'),
path('attachments/<int:pk>/', views.attachment_detail, name='attachment_detail'),

# Attachment Detail URLs
path('attachment-details/', views.attachment_detail_list, name='attachment_detail_list'),
path('attachment-details/<int:pk>/', views.attachment_detail_detail, name='attachment_detail_detail'),

# Limits URLs
path('limits/', views.limits_list, name='limits_list'),
path('limits/<int:pk>/', views.limits_detail, name='limits_detail'),

# Retention URLs
path('retentions/', views.retention_list, name='retention_list'),
path('retentions/<int:pk>/', views.retention_detail, name='retention_detail'),

# Sublimit URLs
path('sublimits/', views.sublimit_list, name='sublimit_list'),
path('sublimits/<int:pk>/', views.sublimit_detail, name='sublimit_detail'),

# Workstation main page
path('workstation/', views.workstation_view, name='workstation'),

# Application Response URLs
path('workstation/application-responses/', views.application_response_list, name='application_response_list'),
path('workstation/application-responses/<int:pk>/', views.application_response_detail, name='application_response_detail'),

# Company Management URLs
path('workstation/options/', views.options_list, name='options_list'),
path('workstation/options/<int:pk>/', views.options_detail, name='options_detail'),

path('workstation/companies/', views.company_list, name='company_list'),
path('workstation/companies/<int:pk>/', views.company_detail, name='company_detail'),

path('workstation/company-locations/', views.company_location_list, name='company_location_list'),
path('workstation/company-locations/<int:pk>/', views.company_location_detail, name='company_location_detail'),

path('workstation/company-contacts/', views.company_contact_list, name='company_contact_list'),
path('workstation/company-contacts/<int:pk>/', views.company_contact_detail, name='company_contact_detail'),

path('workstation/company-aliases/', views.company_alias_list, name='company_alias_list'),
path('workstation/company-aliases/<int:pk>/', views.company_alias_detail, name='company_alias_detail'),

# Order Management URLs
path('workstation/order-options/', views.order_option_list, name='order_option_list'),
path('workstation/order-options/<int:pk>/', views.order_option_detail, name='order_option_detail'),

path('workstation/order-data-verts/', views.order_data_vert_list, name='order_data_vert_list'),
path('workstation/order-data-verts/<int:pk>/', views.order_data_vert_detail, name='order_data_vert_detail'),

path('workstation/document-details/', views.document_detail_list, name='document_detail_list'),
path('workstation/document-details/<int:pk>/', views.document_detail_detail, name='document_detail_detail'),

# AJAX Modal endpoints (add these to your existing urlpatterns)
path('ajax/company-contact/<int:pk>/edit/', views.company_contact_modal_edit, name='company_contact_modal_edit'),
path('ajax/company-contact/add/', views.company_contact_modal_add, name='company_contact_modal_add'),

# Company AJAX endpoints
path('ajax/company/<int:pk>/edit/', views.company_modal_edit, name='company_modal_edit'),
path('ajax/company/add/', views.company_modal_add, name='company_modal_add'),
    
# Options AJAX endpoints  
path('ajax/options/<int:pk>/edit/', views.options_modal_edit, name='options_modal_edit'),
path('ajax/options/add/', views.options_modal_add, name='options_modal_add'),
# Company Location AJAX endpoints
path('ajax/company-location/<int:pk>/edit/', views.company_location_modal_edit, name='company_location_modal_edit'),
path('ajax/company-location/add/', views.company_location_modal_add, name='company_location_modal_add'),
    
# Company Alias AJAX endpoints
path('ajax/company-alias/<int:pk>/edit/', views.company_alias_modal_edit, name='company_alias_modal_edit'),
path('ajax/company-alias/add/', views.company_alias_modal_add, name='company_alias_modal_add'),
    
# Application Response AJAX endpoints
path('ajax/application-response/<int:pk>/edit/', views.application_response_modal_edit, name='application_response_modal_edit'),
path('ajax/application-response/add/', views.application_response_modal_add, name='application_response_modal_add'),
    
# Order Option AJAX endpoints
path('ajax/order-option/<int:pk>/edit/', views.order_option_modal_edit, name='order_option_modal_edit'),
path('ajax/order-option/add/', views.order_option_modal_add, name='order_option_modal_add'),
    
# Order Data Vert AJAX endpoints
path('ajax/order-data-vert/<int:pk>/edit/', views.order_data_vert_modal_edit, name='order_data_vert_modal_edit'),
path('ajax/order-data-vert/add/', views.order_data_vert_modal_add, name='order_data_vert_modal_add'),
    
# Document Detail AJAX endpoints
path('ajax/document-detail/<int:pk>/edit/', views.document_detail_modal_edit, name='document_detail_modal_edit'),
path('ajax/document-detail/add/', views.document_detail_modal_add, name='document_detail_modal_add'),

    
]