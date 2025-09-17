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
    
    # Generation Job URLs
    path('machine-learning/generation-jobs/', views.generation_job_list, name='generation_job_list'),
    path('machine-learning/generation-jobs/<int:pk>/', views.generation_job_detail, name='generation_job_detail'),
    
    # Generation Log URLs
    path('machine-learning/generation-logs/', views.generation_log_list, name='generation_log_list'),
    path('machine-learning/generation-logs/<int:pk>/', views.generation_log_detail, name='generation_log_detail'),
    
    # Model Parameter URLs
    path('machine-learning/model-parameters/', views.model_parameter_list, name='model_parameter_list'),
    path('machine-learning/model-parameters/<int:pk>/', views.model_parameter_detail, name='model_parameter_detail'),
    
    # Training Job URLs
    path('machine-learning/training-jobs/', views.training_job_list, name='training_job_list'),
    path('machine-learning/training-jobs/<int:pk>/', views.training_job_detail, name='training_job_detail'),
    
    # Employee Contact URLs
    path('employees/', views.employee_contact_list, name='employee_contact_list'),
    path('employees/<int:pk>/', views.employee_contact, name='employee_contact'),
    
    # Products URLs
    path('products/', views.products_list, name='products_list'),
    path('products/<int:pk>/', views.products_detail, name='products_detail'),
    
    # Cover URLs
    path('coverage/', views.cover_list, name='cover_list'),
    path('coverage/<int:pk>/', views.cover_detail, name='cover_detail'),
    
    # Employee Function URLs
    path('functions/', views.employee_function_list, name='employee_function_list'),
    path('functions/<int:pk>/', views.employee_function_detail, name='employee_function_detail'),
    
    # API endpoints
    path('api/ventures/', views.venture_api, name='venture_api'),

    
# Add these lines to your existing core/urls.py file
# Just append these to your current urlpatterns list

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


]