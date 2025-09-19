from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Authentication URLs
    path('accounts/login/', auth_views.LoginView.as_view(template_name='auth/login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('login/', auth_views.LoginView.as_view(template_name='auth/login.html'), name='login_short'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout_short'),
    
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Main Pages (Vertex AI Style)
    path('main/<str:page_name>/', views.main_page_view, name='main_page'),
    path('main/<str:page_name>/load-more/', views.load_more_sections, name='load_more_sections'),
    path('main/<str:page_name>/search/', views.search_sections, name='search_sections'),
    path('main/<str:page_name>/<str:section_name>/data/', views.get_section_data, name='get_section_data'),
    path('main/<str:page_name>/<str:section_name>/<int:record_id>/edit/', views.edit_record, name='edit_record'),
    path('main/<str:page_name>/<str:section_name>/add/', views.add_record, name='add_record'),

    # Company URLs
    path('companies/', views.CompanyListView.as_view(), name='company_list'),
    path('companies/<int:company_id>/', views.CompanyDetailView.as_view(), name='company_detail'),
    path('companies/create/', views.CompanyCreateView.as_view(), name='company_create'),
    path('companies/<int:company_id>/edit/', views.CompanyUpdateView.as_view(), name='company_edit'),
    path('companies/<int:company_id>/delete/', views.CompanyDeleteView.as_view(), name='company_delete'),
    
    # Products URLs
    path('products/', views.ProductsListView.as_view(), name='products_list'),
    path('products/<int:products_id>/', views.ProductsDetailView.as_view(), name='products_detail'),
    path('products/create/', views.ProductsCreateView.as_view(), name='products_create'),
    path('products/<int:products_id>/edit/', views.ProductsUpdateView.as_view(), name='products_edit'),
    path('products/<int:products_id>/delete/', views.ProductsDeleteView.as_view(), name='products_delete'),
    
    # Orders URLs
    path('orders/', views.OrdersListView.as_view(), name='orders_list'),
    path('orders/<int:orders_id>/', views.OrdersDetailView.as_view(), name='orders_detail'),
    path('orders/create/', views.OrdersCreateView.as_view(), name='orders_create'),
    path('orders/<int:orders_id>/edit/', views.OrdersUpdateView.as_view(), name='orders_edit'),
    path('orders/<int:orders_id>/delete/', views.OrdersDeleteView.as_view(), name='orders_delete'),
    
    # Applications URLs
    path('applications/', views.ApplicationsListView.as_view(), name='applications_list'),
    path('applications/<int:application_id>/', views.ApplicationsDetailView.as_view(), name='applications_detail'),
    path('applications/create/', views.ApplicationsCreateView.as_view(), name='applications_create'),
    path('applications/<int:application_id>/edit/', views.ApplicationsUpdateView.as_view(), name='applications_edit'),
    path('applications/<int:application_id>/delete/', views.ApplicationsDeleteView.as_view(), name='applications_delete'),
    
    # Employee URLs
    path('employees/', views.EmployeeContactListView.as_view(), name='employee_list'),
    path('employees/<int:employee_id>/', views.EmployeeContactDetailView.as_view(), name='employee_detail'),
    path('employees/create/', views.EmployeeContactCreateView.as_view(), name='employee_create'),
    path('employees/<int:employee_id>/edit/', views.EmployeeContactUpdateView.as_view(), name='employee_edit'),
    path('employees/<int:employee_id>/delete/', views.EmployeeContactDeleteView.as_view(), name='employee_delete'),
    
    # Venture URLs
    path('ventures/', views.VentureListView.as_view(), name='venture_list'),
    path('ventures/<int:venture_id>/', views.VentureDetailView.as_view(), name='venture_detail'),
    path('ventures/create/', views.VentureCreateView.as_view(), name='venture_create'),
    path('ventures/<int:venture_id>/edit/', views.VentureUpdateView.as_view(), name='venture_edit'),
    path('ventures/<int:venture_id>/delete/', views.VentureDeleteView.as_view(), name='venture_delete'),
    
    # API endpoints for AJAX/autocomplete
    path('api/companies/search/', views.search_companies, name='api_companies_search'),
    path('api/products/search/', views.search_products, name='api_products_search'),
    path('api/employees/search/', views.search_employees, name='api_employees_search'),
    
    # Reports
    path('reports/', views.reports_dashboard, name='reports_dashboard'),
    path('export/', views.export_data, name='export_data'),
]
