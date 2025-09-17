# core/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.core.paginator import Paginator
from rest_framework import viewsets
from rest_framework.decorators import api_view
from .models import (
    Venture, Drive, EmployeeLocation, GenerationJob, Parameter,
    DataSeed, GenerationLog, ModelParameter, TrainingJob, Products,
    GenerationModel, TrainingModel, InputOutput, EmployeeContact,
    Cover, EmployeeFunction
)

# =============================================================================
# EXISTING VIEWS (KEEP THESE)
# =============================================================================

def catalog_view(request):
    """Main catalog page view with all sections"""
    # Original sections (these work)
    ventures = Venture.objects.all()
    drives = Drive.objects.select_related('venture').all()
    employee_locations = EmployeeLocation.objects.select_related('venture').all()
    
    # NEW sections (these were missing!)
    products = Products.objects.select_related('venture', 'coverage').all()
    coverage_types = Cover.objects.select_related('product').all()
    employee_contacts = EmployeeContact.objects.select_related('employee_location').all()
    employee_functions = EmployeeFunction.objects.all()
    
    context = {
        'ventures': ventures,
        'drives': drives,
        'employee_locations': employee_locations,
        # Add the missing data
        'products': products,
        'coverage_types': coverage_types,
        'employee_contacts': employee_contacts,
        'employee_functions': employee_functions,
    }
    return render(request, 'core/catalog.html', context)

def dashboard_view(request):
    """Main dashboard view"""
    return render(request, 'core/dashboard.html')

# =============================================================================
# MACHINE LEARNING SECTION (EXISTING - KEEP THESE)
# =============================================================================

def machine_learning_view(request):
    """Enhanced Machine Learning hub page with all sections"""
    # Get recent data for each section (5 items each)
    recent_data_seeds = DataSeed.objects.select_related('product').all()[:5]
    recent_generation_jobs = GenerationJob.objects.all()[:5]
    recent_generation_logs = GenerationLog.objects.all()[:5]
    recent_model_parameters = ModelParameter.objects.select_related(
        'training_job', 'parameter', 'input_output'
    ).all()[:5]
    recent_training_jobs = TrainingJob.objects.select_related(
        'training_model', 'products'
    ).all()[:5]
    
    context = {
        'recent_data_seeds': recent_data_seeds,
        'recent_generation_jobs': recent_generation_jobs,
        'recent_generation_logs': recent_generation_logs,
        'recent_model_parameters': recent_model_parameters,
        'recent_training_jobs': recent_training_jobs,
    }
    return render(request, 'core/machine_learning/hub.html', context)

def data_seed_list(request):
    """List all data seeds"""
    search_query = request.GET.get('search', '')
    
    data_seeds = DataSeed.objects.select_related('product').all()
    
    if search_query:
        data_seeds = data_seeds.filter(
            data_seed_filename__icontains=search_query
        )
    
    paginator = Paginator(data_seeds, 25)  # 25 per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'title': 'Data Seeds',
        'add_url': 'core:data_seed_add',
        'total_count': data_seeds.count(),
    }
    return render(request, 'core/machine_learning/data_seed_list.html', context)

def data_seed_detail(request, pk):
    """View individual data seed"""
    data_seed = get_object_or_404(DataSeed, pk=pk)
    
    context = {
        'object': data_seed,
        'title': f'Data Seed: {data_seed.data_seed_filename or pk}',
        'edit_url': 'core:data_seed_edit',
        'list_url': 'core:data_seed_list',
    }
    return render(request, 'core/machine_learning/data_seed_detail.html', context)

def generation_job_list(request):
    """List all generation jobs"""
    search_query = request.GET.get('search', '')
    
    jobs = GenerationJob.objects.all()
    
    if search_query:
        jobs = jobs.filter(
            data_seed_id__icontains=search_query
        )
    
    paginator = Paginator(jobs, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'title': 'Generation Jobs',
        'add_url': 'core:generation_job_add',
        'total_count': jobs.count(),
    }
    return render(request, 'core/machine_learning/generation_job_list.html', context)

def generation_job_detail(request, pk):
    """View individual generation job"""
    job = get_object_or_404(GenerationJob, pk=pk)
    
    context = {
        'object': job,
        'title': f'Generation Job {job.generation_job_id}',
        'edit_url': 'core:generation_job_edit',
        'list_url': 'core:generation_job_list',
    }
    return render(request, 'core/machine_learning/generation_job_detail.html', context)

def generation_log_list(request):
    """List all generation logs"""
    search_query = request.GET.get('search', '')
    
    logs = GenerationLog.objects.all()
    
    if search_query:
        logs = logs.filter(
            output_file_name__icontains=search_query
        )
    
    paginator = Paginator(logs, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'title': 'Generation Logs',
        'add_url': 'core:generation_log_add',
        'total_count': logs.count(),
    }
    return render(request, 'core/machine_learning/generation_log_list.html', context)

def generation_log_detail(request, pk):
    """View individual generation log"""
    log = get_object_or_404(GenerationLog, pk=pk)
    
    context = {
        'object': log,
        'title': f'Generation Log: {log.output_file_name or log.output_id}',
        'edit_url': 'core:generation_log_edit',
        'list_url': 'core:generation_log_list',
    }
    return render(request, 'core/machine_learning/generation_log_detail.html', context)

def model_parameter_list(request):
    """List all model parameters"""
    parameters = ModelParameter.objects.select_related(
        'training_job', 'parameter', 'input_output'
    ).all()
    
    paginator = Paginator(parameters, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'title': 'Model Parameters',
        'add_url': 'core:model_parameter_add',
        'total_count': parameters.count(),
    }
    return render(request, 'core/machine_learning/model_parameter_list.html', context)

def model_parameter_detail(request, pk):
    """View individual model parameter"""
    param = get_object_or_404(ModelParameter, pk=pk)
    
    context = {
        'object': param,
        'title': f'Model Parameter {param.model_parameter_id}',
        'edit_url': 'core:model_parameter_edit',
        'list_url': 'core:model_parameter_list',
    }
    return render(request, 'core/machine_learning/model_parameter_detail.html', context)

def training_job_list(request):
    """List all training jobs"""
    search_query = request.GET.get('search', '')
    
    jobs = TrainingJob.objects.select_related('training_model', 'products').all()
    
    if search_query:
        jobs = jobs.filter(
            pickle_file_name__icontains=search_query
        )
    
    paginator = Paginator(jobs, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'title': 'Training Jobs',
        'add_url': 'core:training_job_add',
        'total_count': jobs.count(),
    }
    return render(request, 'core/machine_learning/training_job_list.html', context)

def training_job_detail(request, pk):
    """View individual training job"""
    job = get_object_or_404(TrainingJob, pk=pk)
    
    context = {
        'object': job,
        'title': f'Training Job: {job.pickle_file_name or job.training_job_id}',
        'edit_url': 'core:training_job_edit',
        'list_url': 'core:training_job_list',
    }
    return render(request, 'core/machine_learning/training_job_detail.html', context)

# =============================================================================
# NEW EMPLOYEE CONTACT SECTION
# =============================================================================

def employee_contact_list(request):
    """List all employee contacts"""
    search_query = request.GET.get('search', '')
    
    employees = EmployeeContact.objects.select_related('employee_location').all()
    
    if search_query:
        employees = employees.filter(
            employee_name_first__icontains=search_query
        ) | employees.filter(
            employee_name_last__icontains=search_query
        ) | employees.filter(
            employee_email__icontains=search_query
        )
    
    paginator = Paginator(employees, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'title': 'Employee Contacts',
        'total_count': employees.count(),
    }
    return render(request, 'core/employee_contact_list.html', context)

def employee_contact_detail(request, pk):
    """View individual employee contact"""
    employee = get_object_or_404(EmployeeContact, pk=pk)
    
    context = {
        'object': employee,
        'title': f'Employee: {employee.employee_name_first} {employee.employee_name_last}',
        'list_url': 'core:employee_contact_list',
    }
    return render(request, 'core/employee_contact_detail.html', context)

# =============================================================================
# NEW PRODUCTS SECTION
# =============================================================================

def products_list(request):
    """List all products"""
    search_query = request.GET.get('search', '')
    
    products = Products.objects.select_related('venture', 'coverage').all()
    
    if search_query:
        products = products.filter(
            product_name__icontains=search_query
        ) | products.filter(
            product_code__icontains=search_query
        )
    
    paginator = Paginator(products, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'title': 'Products',
        'total_count': products.count(),
    }
    return render(request, 'core/products_list.html', context)

def products_detail(request, pk):
    """View individual product"""
    product = get_object_or_404(Products, pk=pk)
    
    # Get related covers for this product
    covers = Cover.objects.filter(product=product)
    
    context = {
        'object': product,
        'covers': covers,
        'title': f'Product: {product.product_name or f"Product {product.products_id}"}',
        'list_url': 'core:products_list',
    }
    return render(request, 'core/products_detail.html', context)

# =============================================================================
# NEW COVER SECTION
# =============================================================================

def cover_list(request):
    """List all covers"""
    search_query = request.GET.get('search', '')
    
    covers = Cover.objects.select_related('product').all()
    
    if search_query:
        covers = covers.filter(
            cover_name__icontains=search_query
        )
    
    paginator = Paginator(covers, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'title': 'Coverage Types',
        'total_count': covers.count(),
    }
    return render(request, 'core/cover_list.html', context)

def cover_detail(request, pk):
    """View individual cover"""
    cover = get_object_or_404(Cover, pk=pk)
    
    context = {
        'object': cover,
        'title': f'Cover: {cover.cover_name or f"Cover {cover.cover_id}"}',
        'list_url': 'core:cover_list',
    }
    return render(request, 'core/cover_detail.html', context)

# =============================================================================
# NEW EMPLOYEE FUNCTION SECTION
# =============================================================================

def employee_function_list(request):
    """List all employee functions"""
    search_query = request.GET.get('search', '')
    
    functions = EmployeeFunction.objects.all()
    
    if search_query:
        functions = functions.filter(
            employee_function__icontains=search_query
        )
    
    paginator = Paginator(functions, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'title': 'Employee Functions',
        'total_count': functions.count(),
    }
    return render(request, 'core/employee_function_list.html', context)

def employee_function_detail(request, pk):
    """View individual employee function"""
    function = get_object_or_404(EmployeeFunction, pk=pk)
    
    context = {
        'object': function,
        'title': f'Function: {function.employee_function or f"Function {function.employee_function_id}"}',
        'list_url': 'core:employee_function_list',
    }
    return render(request, 'core/employee_function_detail.html', context)

# =============================================================================
# GENERIC CRUD OPERATIONS (EXISTING - FOR FUTURE EXTENSIBILITY)
# =============================================================================

def generic_add_view(request, model_class, form_class, template_name, success_url):
    """Generic add view for any model"""
    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            instance = form.save()
            messages.success(request, f'{model_class._meta.verbose_name} added successfully!')
            return redirect(success_url, pk=instance.pk if hasattr(instance, 'pk') else None)
    else:
        form = form_class()
    
    context = {
        'form': form,
        'title': f'Add {model_class._meta.verbose_name}',
        'model_name': model_class._meta.verbose_name,
    }
    return render(request, template_name, context)

def generic_edit_view(request, model_class, form_class, template_name, success_url, pk):
    """Generic edit view for any model"""
    instance = get_object_or_404(model_class, pk=pk)
    
    if request.method == 'POST':
        form = form_class(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request, f'{model_class._meta.verbose_name} updated successfully!')
            return redirect(success_url, pk=pk)
    else:
        form = form_class(instance=instance)
    
    context = {
        'form': form,
        'object': instance,
        'title': f'Edit {model_class._meta.verbose_name}',
        'model_name': model_class._meta.verbose_name,
    }
    return render(request, template_name, context)

# =============================================================================
# API VIEWS (EXISTING - FOR AJAX OPERATIONS)
# =============================================================================

@api_view(['GET', 'POST'])
def venture_api(request):
    if request.method == 'GET':
        ventures = Venture.objects.all()
        data = [{
            'venture_id': v.venture_id,
            'venture_name': v.venture_name,
            'venture_address_1': v.venture_address_1,
            'venture_address_2': v.venture_address_2,
            'venture_city': v.venture_city,
            'venture_state': v.venture_state,
            'venture_zip': v.venture_zip,
        } for v in ventures]
        return JsonResponse({'ventures': data})
    
    elif request.method == 'POST':
        # Handle adding new venture
        data = request.data
        venture = Venture.objects.create(
            venture_name=data.get('venture_name'),
            venture_address_1=data.get('venture_address_1'),
            venture_address_2=data.get('venture_address_2'),
            venture_city=data.get('venture_city'),
            venture_state=data.get('venture_state'),
            venture_zip=data.get('venture_zip'),
        )
        return JsonResponse({'success': True, 'venture_id': venture.venture_id})