# core/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.core.paginator import Paginator
from rest_framework import viewsets
from rest_framework.decorators import api_view
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .forms import CompanyContactForm 
from .models import (
    Venture, Drive, EmployeeLocation, GenerationJob, Parameter,
    DataSeed, GenerationLog, ModelParameter, TrainingJob, Products,
    GenerationModel, TrainingModel, InputOutput, EmployeeContact,
    Cover, EmployeeFunction, Paper, PaperDetail, Applications, ApplicationQuestion,
    ParameterMap, Document, Task, Workflow, WorkflowDetail, Attachment, 
    AttachmentDetail, Limits, Retention, Sublimit, ApplicationResponse,
    Options, Company, CompanyLocation, CompanyContact, CompanyAlias,
    OrderOption, OrderDataVert, DocumentDetail
)

from .forms import (
    CompanyContactForm, CompanyForm, OptionsForm, CompanyLocationForm, 
    CompanyAliasForm, ApplicationResponseForm, OrderOptionForm, 
    OrderDataVertForm, DocumentDetailForm
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
    
    # Existing new sections
    products = Products.objects.select_related('venture', 'coverage').all()
    coverage_types = Cover.objects.select_related('product').all()
    employee_contacts = EmployeeContact.objects.select_related('employee_location').all()
    employee_functions = EmployeeFunction.objects.all()
    
    # Previous additions - Paper, PaperDetail, Applications, ApplicationQuestion
    papers = Paper.objects.all()
    paper_details = PaperDetail.objects.select_related('products', 'paper').all()
    applications = Applications.objects.select_related('product').all()
    application_questions = ApplicationQuestion.objects.select_related('application', 'parameter').all()
    
    # Recent additions - Parameter, ParameterMap, Document, Task
    parameters = Parameter.objects.all()
    parameter_maps = ParameterMap.objects.select_related('products', 'parameter').all()
    documents = Document.objects.select_related('product').all()
    tasks = Task.objects.all()
    
    # NEWEST sections - Workflow and Business Logic models
    workflows = Workflow.objects.all()
    workflow_details = WorkflowDetail.objects.select_related('workflow', 'task').all()
    attachments = Attachment.objects.select_related('attachment_type').all()
    attachment_details = AttachmentDetail.objects.select_related('attachment', 'product', 'task', 'attachment_type').all()
    limits = Limits.objects.select_related('product', 'cover').all()
    retentions = Retention.objects.select_related('products').all()
    sublimits = Sublimit.objects.select_related('orders', 'products').all()
    
    context = {
        'ventures': ventures,
        'drives': drives,
        'employee_locations': employee_locations,
        'products': products,
        'coverage_types': coverage_types,
        'employee_contacts': employee_contacts,
        'employee_functions': employee_functions,
        'papers': papers,
        'paper_details': paper_details,
        'applications': applications,
        'application_questions': application_questions,
        'parameters': parameters,
        'parameter_maps': parameter_maps,
        'documents': documents,
        'tasks': tasks,
        # Add the 7 newest data sets
        'workflows': workflows,
        'workflow_details': workflow_details,
        'attachments': attachments,
        'attachment_details': attachment_details,
        'limits': limits,
        'retentions': retentions,
        'sublimits': sublimits,
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

def paper_list(request):
    """List all papers"""
    search_query = request.GET.get('search', '')
    
    papers = Paper.objects.all()
    
    if search_query:
        papers = papers.filter(
            paper_name__icontains=search_query
        )
    
    paginator = Paginator(papers, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'title': 'Papers',
        'total_count': papers.count(),
    }
    return render(request, 'core/paper_list.html', context)

def paper_detail(request, pk):
    """View individual paper"""
    paper = get_object_or_404(Paper, pk=pk)
    
    # Get related paper details for this paper
    related_paper_details = PaperDetail.objects.filter(paper=paper).select_related('products')
    
    context = {
        'object': paper,
        'related_paper_details': related_paper_details,
        'title': f'Paper: {paper.paper_name or f"Paper {paper.paper_id}"}',
        'list_url': 'core:paper_list',
    }
    return render(request, 'core/paper_detail.html', context)

# =============================================================================
# NEW PAPER DETAIL SECTION
# =============================================================================

def paper_detail_list(request):
    """List all paper details"""
    search_query = request.GET.get('search', '')
    
    paper_details = PaperDetail.objects.select_related('products', 'paper').all()
    
    if search_query:
        paper_details = paper_details.filter(
            paper__paper_name__icontains=search_query
        ) | paper_details.filter(
            products__product_name__icontains=search_query
        )
    
    paginator = Paginator(paper_details, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'title': 'Paper Details',
        'total_count': paper_details.count(),
    }
    return render(request, 'core/paper_detail_list.html', context)

def paper_detail_detail(request, pk):
    """View individual paper detail"""
    paper_detail = get_object_or_404(PaperDetail, pk=pk)
    
    context = {
        'object': paper_detail,
        'title': f'Paper Detail: {paper_detail.paper_detail_id}',
        'list_url': 'core:paper_detail_list',
    }
    return render(request, 'core/paper_detail_detail.html', context)

# =============================================================================
# NEW APPLICATIONS SECTION
# =============================================================================

def application_list(request):
    """List all applications"""
    search_query = request.GET.get('search', '')
    
    applications = Applications.objects.select_related('product').all()
    
    if search_query:
        applications = applications.filter(
            application_name__icontains=search_query
        )
    
    paginator = Paginator(applications, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'title': 'Applications',
        'total_count': applications.count(),
    }
    return render(request, 'core/application_list.html', context)

def application_detail(request, pk):
    """View individual application"""
    application = get_object_or_404(Applications, pk=pk)
    
    # Get related application questions
    related_questions = ApplicationQuestion.objects.filter(application=application).select_related('parameter')
    
    context = {
        'object': application,
        'related_questions': related_questions,
        'title': f'Application: {application.application_name or f"Application {application.application_id}"}',
        'list_url': 'core:application_list',
    }
    return render(request, 'core/application_detail.html', context)

# =============================================================================
# NEW APPLICATION QUESTION SECTION
# =============================================================================

def application_question_list(request):
    """List all application questions"""
    search_query = request.GET.get('search', '')
    
    questions = ApplicationQuestion.objects.select_related('application', 'parameter').all()
    
    if search_query:
        questions = questions.filter(
            custom_question__icontains=search_query
        ) | questions.filter(
            application__application_name__icontains=search_query
        )
    
    paginator = Paginator(questions, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'title': 'Application Questions',
        'total_count': questions.count(),
    }
    return render(request, 'core/application_question_list.html', context)

def application_question_detail(request, pk):
    """View individual application question"""
    question = get_object_or_404(ApplicationQuestion, pk=pk)
    
    context = {
        'object': question,
        'title': f'Application Question: {question.application_question_id}',
        'list_url': 'core:application_question_list',
    }
    return render(request, 'core/application_question_detail.html', context)

def parameter_list(request):
    """List all parameters"""
    search_query = request.GET.get('search', '')
    
    parameters = Parameter.objects.all()
    
    if search_query:
        parameters = parameters.filter(
            parameter_name__icontains=search_query
        ) | parameters.filter(
            parameter_docs__icontains=search_query
        )
    
    paginator = Paginator(parameters, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'title': 'Parameters',
        'total_count': parameters.count(),
    }
    return render(request, 'core/parameter_list.html', context)

def parameter_detail(request, pk):
    """View individual parameter"""
    parameter = get_object_or_404(Parameter, pk=pk)
    
    # Get related parameter maps for this parameter
    related_maps = ParameterMap.objects.filter(parameter=parameter).select_related('products')
    
    context = {
        'object': parameter,
        'related_maps': related_maps,
        'title': f'Parameter: {parameter.parameter_name or f"Parameter {parameter.parameter_id}"}',
        'list_url': 'core:parameter_list',
    }
    return render(request, 'core/parameter_detail.html', context)

# =============================================================================
# NEWEST PARAMETER MAP SECTION
# =============================================================================

def parameter_map_list(request):
    """List all parameter maps"""
    search_query = request.GET.get('search', '')
    
    parameter_maps = ParameterMap.objects.select_related('products', 'parameter').all()
    
    if search_query:
        parameter_maps = parameter_maps.filter(
            parameter__parameter_name__icontains=search_query
        ) | parameter_maps.filter(
            products__product_name__icontains=search_query
        )
    
    paginator = Paginator(parameter_maps, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'title': 'Parameter Maps',
        'total_count': parameter_maps.count(),
    }
    return render(request, 'core/parameter_map_list.html', context)

def parameter_map_detail(request, pk):
    """View individual parameter map"""
    parameter_map = get_object_or_404(ParameterMap, pk=pk)
    
    context = {
        'object': parameter_map,
        'title': f'Parameter Map: {parameter_map.parameter_map_id}',
        'list_url': 'core:parameter_map_list',
    }
    return render(request, 'core/parameter_map_detail.html', context)

# =============================================================================
# NEWEST DOCUMENT SECTION
# =============================================================================

def document_list(request):
    """List all documents"""
    search_query = request.GET.get('search', '')
    
    documents = Document.objects.select_related('product').all()
    
    if search_query:
        documents = documents.filter(
            document_name__icontains=search_query
        ) | documents.filter(
            document_code__icontains=search_query
        )
    
    paginator = Paginator(documents, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'title': 'Documents',
        'total_count': documents.count(),
    }
    return render(request, 'core/document_list.html', context)

def document_detail(request, pk):
    """View individual document"""
    document = get_object_or_404(Document, pk=pk)
    
    context = {
        'object': document,
        'title': f'Document: {document.document_name or f"Document {document.document_id}"}',
        'list_url': 'core:document_list',
    }
    return render(request, 'core/document_detail.html', context)

# =============================================================================
# NEWEST TASK SECTION
# =============================================================================

def task_list(request):
    """List all tasks"""
    search_query = request.GET.get('search', '')
    
    tasks = Task.objects.all()
    
    if search_query:
        tasks = tasks.filter(
            task_name__icontains=search_query
        ) | tasks.filter(
            task_description__icontains=search_query
        )
    
    paginator = Paginator(tasks, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'title': 'Tasks',
        'total_count': tasks.count(),
    }
    return render(request, 'core/task_list.html', context)

def task_detail(request, pk):
    """View individual task"""
    task = get_object_or_404(Task, pk=pk)
    
    context = {
        'object': task,
        'title': f'Task: {task.task_name or f"Task {task.task_id}"}',
        'list_url': 'core:task_list',
    }
    return render(request, 'core/task_detail.html', context)

# =============================================================================
# WORKFLOW SECTION
# =============================================================================

def workflow_list(request):
    """List all workflows"""
    search_query = request.GET.get('search', '')
    
    workflows = Workflow.objects.all()
    
    if search_query:
        workflows = workflows.filter(
            workflow_name__icontains=search_query
        ) | workflows.filter(
            workflow_type__icontains=search_query
        )
    
    paginator = Paginator(workflows, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'title': 'Workflows',
        'total_count': workflows.count(),
    }
    return render(request, 'core/workflow_list.html', context)

def workflow_detail(request, pk):
    """View individual workflow"""
    workflow = get_object_or_404(Workflow, pk=pk)
    
    # Get related workflow details
    related_details = WorkflowDetail.objects.filter(workflow=workflow).select_related('task')
    
    context = {
        'object': workflow,
        'related_details': related_details,
        'title': f'Workflow: {workflow.workflow_name or f"Workflow {workflow.workflow_id}"}',
        'list_url': 'core:workflow_list',
    }
    return render(request, 'core/workflow_detail.html', context)

# =============================================================================
# WORKFLOW DETAIL SECTION
# =============================================================================

def workflow_detail_list(request):
    """List all workflow details"""
    search_query = request.GET.get('search', '')
    
    workflow_details = WorkflowDetail.objects.select_related('workflow', 'task').all()
    
    if search_query:
        workflow_details = workflow_details.filter(
            workflow__workflow_name__icontains=search_query
        ) | workflow_details.filter(
            task__task_name__icontains=search_query
        )
    
    paginator = Paginator(workflow_details, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'title': 'Workflow Details',
        'total_count': workflow_details.count(),
    }
    return render(request, 'core/workflow_detail_list.html', context)

def workflow_detail_detail(request, pk):
    """View individual workflow detail"""
    workflow_detail = get_object_or_404(WorkflowDetail, pk=pk)
    
    context = {
        'object': workflow_detail,
        'title': f'Workflow Detail: {workflow_detail.workflow_detail_id}',
        'list_url': 'core:workflow_detail_list',
    }
    return render(request, 'core/workflow_detail_detail.html', context)

# =============================================================================
# ATTACHMENT SECTION
# =============================================================================

def attachment_list(request):
    """List all attachments"""
    search_query = request.GET.get('search', '')
    
    attachments = Attachment.objects.select_related('attachment_type').all()
    
    if search_query:
        attachments = attachments.filter(
            attachment_name__icontains=search_query
        ) | attachments.filter(
            output_description__icontains=search_query
        )
    
    paginator = Paginator(attachments, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'title': 'Attachments',
        'total_count': attachments.count(),
    }
    return render(request, 'core/attachment_list.html', context)

def attachment_detail(request, pk):
    """View individual attachment"""
    attachment = get_object_or_404(Attachment, pk=pk)
    
    # Get related attachment details
    related_details = AttachmentDetail.objects.filter(attachment=attachment).select_related('product', 'task', 'attachment_type')
    
    context = {
        'object': attachment,
        'related_details': related_details,
        'title': f'Attachment: {attachment.attachment_name or f"Attachment {attachment.attachment_id}"}',
        'list_url': 'core:attachment_list',
    }
    return render(request, 'core/attachment_detail.html', context)

# =============================================================================
# ATTACHMENT DETAIL SECTION
# =============================================================================

def attachment_detail_list(request):
    """List all attachment details"""
    search_query = request.GET.get('search', '')
    
    attachment_details = AttachmentDetail.objects.select_related('attachment', 'product', 'task', 'attachment_type').all()
    
    if search_query:
        attachment_details = attachment_details.filter(
            attachment__attachment_name__icontains=search_query
        ) | attachment_details.filter(
            product__product_name__icontains=search_query
        )
    
    paginator = Paginator(attachment_details, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'title': 'Attachment Details',
        'total_count': attachment_details.count(),
    }
    return render(request, 'core/attachment_detail_list.html', context)

def attachment_detail_detail(request, pk):
    """View individual attachment detail"""
    attachment_detail = get_object_or_404(AttachmentDetail, pk=pk)
    
    context = {
        'object': attachment_detail,
        'title': f'Attachment Detail: {attachment_detail.attachment_detail_id}',
        'list_url': 'core:attachment_detail_list',
    }
    return render(request, 'core/attachment_detail_detail.html', context)

# =============================================================================
# LIMITS SECTION
# =============================================================================

def limits_list(request):
    """List all limits"""
    search_query = request.GET.get('search', '')
    
    limits = Limits.objects.select_related('product', 'cover').all()
    
    if search_query:
        limits = limits.filter(
            limit_text__icontains=search_query
        ) | limits.filter(
            product__product_name__icontains=search_query
        )
    
    paginator = Paginator(limits, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'title': 'Limits',
        'total_count': limits.count(),
    }
    return render(request, 'core/limits_list.html', context)

def limits_detail(request, pk):
    """View individual limits"""
    limits = get_object_or_404(Limits, pk=pk)
    
    context = {
        'object': limits,
        'title': f'Limits: {limits.limit_text or f"Limits {limits.limits_id}"}',
        'list_url': 'core:limits_list',
    }
    return render(request, 'core/limits_detail.html', context)

# =============================================================================
# RETENTION SECTION
# =============================================================================

def retention_list(request):
    """List all retentions"""
    search_query = request.GET.get('search', '')
    
    retentions = Retention.objects.select_related('products').all()
    
    if search_query:
        retentions = retentions.filter(
            retention_text__icontains=search_query
        ) | retentions.filter(
            products__product_name__icontains=search_query
        )
    
    paginator = Paginator(retentions, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'title': 'Retentions',
        'total_count': retentions.count(),
    }
    return render(request, 'core/retention_list.html', context)

def retention_detail(request, pk):
    """View individual retention"""
    retention = get_object_or_404(Retention, pk=pk)
    
    context = {
        'object': retention,
        'title': f'Retention: {retention.retention_text or f"Retention {retention.retention_id}"}',
        'list_url': 'core:retention_list',
    }
    return render(request, 'core/retention_detail.html', context)

# =============================================================================
# SUBLIMIT SECTION
# =============================================================================

def sublimit_list(request):
    """List all sublimits"""
    search_query = request.GET.get('search', '')
    
    sublimits = Sublimit.objects.select_related('orders', 'products').all()
    
    if search_query:
        sublimits = sublimits.filter(
            sublimit_name__icontains=search_query
        ) | sublimits.filter(
            products__product_name__icontains=search_query
        )
    
    paginator = Paginator(sublimits, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'title': 'Sublimits',
        'total_count': sublimits.count(),
    }
    return render(request, 'core/sublimit_list.html', context)

def sublimit_detail(request, pk):
    """View individual sublimit"""
    sublimit = get_object_or_404(Sublimit, pk=pk)
    
    context = {
        'object': sublimit,
        'title': f'Sublimit: {sublimit.sublimit_name or f"Sublimit {sublimit.sublimit_id}"}',
        'list_url': 'core:sublimit_list',
    }
    return render(request, 'core/sublimit_detail.html', context)

# =============================================================================
# WORKSTATION SECTION - Add these views to your existing core/views.py
# =============================================================================

def workstation_view(request):
    """Main workstation page with all sections - matches Catalog format"""
    # Get application responses from PostgreSQL (limit to 20 for main page performance)
    application_responses = ApplicationResponse.objects.select_related(
        'application', 'application_question', 'order'
    ).all()[:20]
    
    # Get company management data (limit to 20 each)
    options = Options.objects.all()[:20]
    companies = Company.objects.all()[:20]
    company_locations = CompanyLocation.objects.select_related('company').all()[:20]
    company_contacts = CompanyContact.objects.select_related('company').all()[:20]
    company_aliases = CompanyAlias.objects.select_related('company').all()[:20]
    
    # Calculate stats for dashboard
    total_responses = ApplicationResponse.objects.count()
    unique_applications = ApplicationResponse.objects.values('application').distinct().count()
    unique_orders = ApplicationResponse.objects.exclude(order=None).values('order').distinct().count()
    
    # Company management stats
    total_options = Options.objects.count()
    total_companies = Company.objects.count()
    total_locations = CompanyLocation.objects.count()
    total_contacts = CompanyContact.objects.count()
    total_aliases = CompanyAlias.objects.count()
    
    # Debug information - you can remove this after testing
    print(f"Debug: Found {total_responses} total application responses in database")
    print(f"Debug: Found {total_companies} companies, {total_contacts} contacts, {total_locations} locations")
    
    context = {
        # Application Response data
        'application_responses': application_responses,
        'unique_applications': unique_applications,
        'unique_orders': unique_orders,
        'total_responses': total_responses,
        # Company Management data
        'options': options,
        'companies': companies,
        'company_locations': company_locations,
        'company_contacts': company_contacts,
        'company_aliases': company_aliases,
        # Stats
        'total_options': total_options,
        'total_companies': total_companies,
        'total_locations': total_locations,
        'total_contacts': total_contacts,
        'total_aliases': total_aliases,
    }
    return render(request, 'core/workstation.html', context)

def application_response_list(request):
    """List all application responses with pagination and search - PostgreSQL data"""
    search_query = request.GET.get('search', '')
    
    # Query PostgreSQL for all application responses
    responses = ApplicationResponse.objects.select_related(
        'application', 'application_question', 'order'
    ).all()
    
    # Apply search filter if provided
    if search_query:
        responses = responses.filter(
            response__icontains=search_query
        ) | responses.filter(
            application__application_name__icontains=search_query
        ) | responses.filter(
            application_question__custom_question__icontains=search_query
        )
    
    # Add pagination
    paginator = Paginator(responses, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'title': 'Application Responses',
        'total_count': responses.count(),
    }
    return render(request, 'core/application_response_list.html', context)

def application_response_detail(request, pk):
    """View individual application response - PostgreSQL data"""
    response = get_object_or_404(ApplicationResponse, pk=pk)
    
    context = {
        'object': response,
        'title': f'Application Response: {response.application_response_id}',
        'list_url': 'core:application_response_list',
    }
    return render(request, 'core/application_response_detail.html', context)

def options_list(request):
    """List all options with pagination and search"""
    search_query = request.GET.get('search', '')
    
    options = Options.objects.all()
    
    if search_query:
        options = options.filter(
            option_name__icontains=search_query
        )
    
    paginator = Paginator(options, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'title': 'Options',
        'total_count': options.count(),
    }
    return render(request, 'core/options_list.html', context)

def options_detail(request, pk):
    """View individual option"""
    option = get_object_or_404(Options, pk=pk)
    
    context = {
        'object': option,
        'title': f'Option: {option.option_name or f"Option {option.options_id}"}',
        'list_url': 'core:options_list',
    }
    return render(request, 'core/options_detail.html', context)

# =============================================================================
# COMPANY SECTION
# =============================================================================

def company_list(request):
    """List all companies with pagination and search"""
    search_query = request.GET.get('search', '')
    
    companies = Company.objects.all()
    
    if search_query:
        companies = companies.filter(
            company_name__icontains=search_query
        )
    
    paginator = Paginator(companies, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'title': 'Companies',
        'total_count': companies.count(),
    }
    return render(request, 'core/company_list.html', context)

def company_detail(request, pk):
    """View individual company with related data"""
    company = get_object_or_404(Company, pk=pk)
    
    # Get related company data
    company_locations = CompanyLocation.objects.filter(company=company)
    company_contacts = CompanyContact.objects.filter(company=company)
    company_aliases = CompanyAlias.objects.filter(company=company)
    
    context = {
        'object': company,
        'company_locations': company_locations,
        'company_contacts': company_contacts,
        'company_aliases': company_aliases,
        'title': f'Company: {company.company_name or f"Company {company.company_id}"}',
        'list_url': 'core:company_list',
    }
    return render(request, 'core/company_detail.html', context)

# =============================================================================
# COMPANY LOCATION SECTION
# =============================================================================

def company_location_list(request):
    """List all company locations with pagination and search"""
    search_query = request.GET.get('search', '')
    
    locations = CompanyLocation.objects.select_related('company').all()
    
    if search_query:
        locations = locations.filter(
            company_location_city__icontains=search_query
        ) | locations.filter(
            company_location_state__icontains=search_query
        ) | locations.filter(
            company__company_name__icontains=search_query
        )
    
    paginator = Paginator(locations, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'title': 'Company Locations',
        'total_count': locations.count(),
    }
    return render(request, 'core/company_location_list.html', context)

def company_location_detail(request, pk):
    """View individual company location"""
    location = get_object_or_404(CompanyLocation, pk=pk)
    
    context = {
        'object': location,
        'title': f'Location: {location.company_location_city or f"Location {location.company_location_id}"}',
        'list_url': 'core:company_location_list',
    }
    return render(request, 'core/company_location_detail.html', context)

# =============================================================================
# COMPANY CONTACT SECTION
# =============================================================================

def company_contact_list(request):
    """List all company contacts with pagination and search"""
    search_query = request.GET.get('search', '')
    
    contacts = CompanyContact.objects.select_related('company').all()
    
    if search_query:
        contacts = contacts.filter(
            company_contact_first__icontains=search_query
        ) | contacts.filter(
            company_contact_last__icontains=search_query
        ) | contacts.filter(
            company_contact_email__icontains=search_query
        ) | contacts.filter(
            company__company_name__icontains=search_query
        )
    
    paginator = Paginator(contacts, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'title': 'Company Contacts',
        'total_count': contacts.count(),
    }
    return render(request, 'core/company_contact_list.html', context)

def company_contact_detail(request, pk):
    """View individual company contact"""
    contact = get_object_or_404(CompanyContact, pk=pk)
    
    context = {
        'object': contact,
        'title': f'Contact: {contact.company_contact_first} {contact.company_contact_last}',
        'list_url': 'core:company_contact_list',
    }
    return render(request, 'core/company_contact_detail.html', context)

# =============================================================================
# COMPANY ALIAS SECTION
# =============================================================================

def company_alias_list(request):
    """List all company aliases with pagination and search"""
    search_query = request.GET.get('search', '')
    
    aliases = CompanyAlias.objects.select_related('company').all()
    
    if search_query:
        aliases = aliases.filter(
            company_alias_name__icontains=search_query
        ) | aliases.filter(
            company__company_name__icontains=search_query
        )
    
    paginator = Paginator(aliases, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'title': 'Company Aliases',
        'total_count': aliases.count(),
    }
    return render(request, 'core/company_alias_list.html', context)

def company_alias_detail(request, pk):
    """View individual company alias"""
    alias = get_object_or_404(CompanyAlias, pk=pk)
    
    context = {
        'object': alias,
        'title': f'Alias: {alias.company_alias_name or f"Alias {alias.company_alias_id}"}',
        'list_url': 'core:company_alias_list',
    }
    return render(request, 'core/company_alias_detail.html', context)

# =============================================================================
# ORDER MANAGEMENT SECTION - Add these imports to your existing models import
# =============================================================================
# Add these to your existing imports: OrderOption, OrderDataVert, DocumentDetail

# Update your workstation_view function to include order data
def workstation_view(request):
    """Main workstation page with all sections - matches Catalog format"""
    # Get application responses from PostgreSQL (limit to 20 for main page performance)
    application_responses = ApplicationResponse.objects.select_related(
        'application', 'application_question', 'order'
    ).all()[:20]
    
    # Get company management data (limit to 20 each)
    options = Options.objects.all()[:20]
    companies = Company.objects.all()[:20]
    company_locations = CompanyLocation.objects.select_related('company').all()[:20]
    company_contacts = CompanyContact.objects.select_related('company').all()[:20]
    company_aliases = CompanyAlias.objects.select_related('company').all()[:20]
    
    # Get order management data (limit to 20 each)
    order_options = OrderOption.objects.select_related(
        'orders', 'options', 'cover', 'retention', 'limits'
    ).all()[:20]
    order_data_verts = OrderDataVert.objects.select_related(
        'order', 'parameter', 'parameter_map'
    ).all()[:20]
    document_details = DocumentDetail.objects.select_related(
        'order_option', 'document'
    ).all()[:20]
    
    # Calculate stats for dashboard
    total_responses = ApplicationResponse.objects.count()
    unique_applications = ApplicationResponse.objects.values('application').distinct().count()
    unique_orders = ApplicationResponse.objects.exclude(order=None).values('order').distinct().count()
    
    # Company management stats
    total_options = Options.objects.count()
    total_companies = Company.objects.count()
    total_locations = CompanyLocation.objects.count()
    total_contacts = CompanyContact.objects.count()
    total_aliases = CompanyAlias.objects.count()
    
    # Order management stats
    total_order_options = OrderOption.objects.count()
    total_order_data_verts = OrderDataVert.objects.count()
    total_document_details = DocumentDetail.objects.count()
    
    # Debug information - you can remove this after testing
    print(f"Debug: Found {total_responses} total application responses in database")
    print(f"Debug: Found {total_companies} companies, {total_contacts} contacts, {total_locations} locations")
    print(f"Debug: Found {total_order_options} order options, {total_order_data_verts} order data verts, {total_document_details} document details")
    
    context = {
        # Application Response data
        'application_responses': application_responses,
        'unique_applications': unique_applications,
        'unique_orders': unique_orders,
        'total_responses': total_responses,
        # Company Management data
        'options': options,
        'companies': companies,
        'company_locations': company_locations,
        'company_contacts': company_contacts,
        'company_aliases': company_aliases,
        # Company stats
        'total_options': total_options,
        'total_companies': total_companies,
        'total_locations': total_locations,
        'total_contacts': total_contacts,
        'total_aliases': total_aliases,
        # Order Management data
        'order_options': order_options,
        'order_data_verts': order_data_verts,
        'document_details': document_details,
        # Order stats
        'total_order_options': total_order_options,
        'total_order_data_verts': total_order_data_verts,
        'total_document_details': total_document_details,
    }
    return render(request, 'core/workstation.html', context)

# =============================================================================
# ORDER OPTION SECTION
# =============================================================================

def order_option_list(request):
    """List all order options with pagination and search"""
    search_query = request.GET.get('search', '')
    
    order_options = OrderOption.objects.select_related(
        'orders', 'options', 'cover', 'retention', 'limits'
    ).all()
    
    if search_query:
        order_options = order_options.filter(
            options__option_name__icontains=search_query
        ) | order_options.filter(
            orders__orders_id__icontains=search_query
        ) | order_options.filter(
            cover__cover_name__icontains=search_query
        )
    
    paginator = Paginator(order_options, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'title': 'Order Options',
        'total_count': order_options.count(),
    }
    return render(request, 'core/order_option_list.html', context)

def order_option_detail(request, pk):
    """View individual order option"""
    order_option = get_object_or_404(OrderOption, pk=pk)
    
    context = {
        'object': order_option,
        'title': f'Order Option: {order_option.order_option_id}',
        'list_url': 'core:order_option_list',
    }
    return render(request, 'core/order_option_detail.html', context)

# =============================================================================
# ORDER DATA VERT SECTION
# =============================================================================

def order_data_vert_list(request):
    """List all order data verts with pagination and search"""
    search_query = request.GET.get('search', '')
    
    order_data_verts = OrderDataVert.objects.select_related(
        'order', 'parameter', 'parameter_map'
    ).all()
    
    if search_query:
        order_data_verts = order_data_verts.filter(
            vert_value__icontains=search_query
        ) | order_data_verts.filter(
            parameter__parameter_name__icontains=search_query
        ) | order_data_verts.filter(
            order__orders_id__icontains=search_query
        )
    
    paginator = Paginator(order_data_verts, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'title': 'Order Data Verts',
        'total_count': order_data_verts.count(),
    }
    return render(request, 'core/order_data_vert_list.html', context)

def order_data_vert_detail(request, pk):
    """View individual order data vert"""
    order_data_vert = get_object_or_404(OrderDataVert, pk=pk)
    
    context = {
        'object': order_data_vert,
        'title': f'Order Data Vert: {order_data_vert.order_date_vert_id}',
        'list_url': 'core:order_data_vert_list',
    }
    return render(request, 'core/order_data_vert_detail.html', context)

# =============================================================================
# DOCUMENT DETAIL SECTION
# =============================================================================

def document_detail_list(request):
    """List all document details with pagination and search"""
    search_query = request.GET.get('search', '')
    
    document_details = DocumentDetail.objects.select_related(
        'order_option', 'document'
    ).all()
    
    if search_query:
        document_details = document_details.filter(
            document__document_name__icontains=search_query
        ) | document_details.filter(
            order_option__order_option_id__icontains=search_query
        )
    
    paginator = Paginator(document_details, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'title': 'Document Details',
        'total_count': document_details.count(),
    }
    return render(request, 'core/document_detail_list.html', context)

def document_detail_detail(request, pk):
    """View individual document detail"""
    document_detail = get_object_or_404(DocumentDetail, pk=pk)
    
    context = {
        'object': document_detail,
        'title': f'Document Detail: {document_detail.document_detail_id}',
        'list_url': 'core:document_detail_list',
    }
    return render(request, 'core/document_detail_detail.html', context)

# =============================================================================
# AJAX MODAL VIEWS - Add these to your existing core/views.py file
# =============================================================================

from django.http import JsonResponse
from django.template.loader import render_to_string
from .forms import CompanyContactForm

@api_view(['GET', 'POST'])
def company_contact_modal_edit(request, pk):
    """AJAX view for editing CompanyContact in modal"""
    try:
        contact = get_object_or_404(CompanyContact, pk=pk)
    except CompanyContact.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Contact not found'
        })

    if request.method == 'GET':
        # Return the modal form HTML
        form = CompanyContactForm(instance=contact)
        
        modal_html = render_to_string('core/modals/company_contact_modal.html', {
            'form': form,
            'object': contact
        }, request=request)
        
        return JsonResponse({
            'success': True,
            'html': modal_html
        })
    
    elif request.method == 'POST':
        # Process the form submission
        form = CompanyContactForm(request.POST, instance=contact)
        
        if form.is_valid():
            updated_contact = form.save()
            
            # Generate updated table row HTML
            row_html = render_to_string('core/partials/company_contact_row.html', {
                'contact': updated_contact
            }, request=request)
            
            return JsonResponse({
                'success': True,
                'message': f'Contact {updated_contact.company_contact_first} {updated_contact.company_contact_last} updated successfully!',
                'object_id': updated_contact.company_contact_id,
                'row_html': row_html
            })
        else:
            # Return form with errors
            modal_html = render_to_string('core/modals/company_contact_modal.html', {
                'form': form,
                'object': contact
            }, request=request)
            
            return JsonResponse({
                'success': False,
                'html': modal_html,
                'errors': form.errors
            })

@api_view(['GET', 'POST'])  
def company_contact_modal_add(request):
    """AJAX view for adding new CompanyContact in modal"""
    
    if request.method == 'GET':
        # Return the modal form HTML for new contact
        form = CompanyContactForm()
        
        modal_html = render_to_string('core/modals/company_contact_modal.html', {
            'form': form,
            'object': None
        }, request=request)
        
        return JsonResponse({
            'success': True,
            'html': modal_html
        })
    
    elif request.method == 'POST':
        # Process the form submission
        form = CompanyContactForm(request.POST)
        
        if form.is_valid():
            new_contact = form.save()
            
            # Generate new table row HTML
            row_html = render_to_string('core/partials/company_contact_row.html', {
                'contact': new_contact
            }, request=request)
            
            return JsonResponse({
                'success': True,
                'message': f'Contact {new_contact.company_contact_first} {new_contact.company_contact_last} added successfully!',
                'object_id': new_contact.company_contact_id,
                'row_html': row_html,
                'action': 'add'  # This tells JS to add a new row instead of updating
            })
        else:
            # Return form with errors
            modal_html = render_to_string('core/modals/company_contact_modal.html', {
                'form': form,
                'object': None
            }, request=request)
            
            return JsonResponse({
                'success': False,
                'html': modal_html,
                'errors': form.errors
            })

# =============================================================================
# AJAX MODAL VIEWS - Add these to your core/views.py file
# =============================================================================

@csrf_exempt  # Temporarily disable CSRF for testing
@require_http_methods(["GET", "POST"])
def company_contact_modal_edit(request, pk):
    """AJAX view for editing CompanyContact in modal"""
    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': False, 'error': 'AJAX request required'})
    
    try:
        contact = get_object_or_404(CompanyContact, pk=pk)
    except CompanyContact.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Contact not found'
        })

    if request.method == 'GET':
        # Return the modal form HTML
        form = CompanyContactForm(instance=contact)
        
        modal_html = render_to_string('core/modals/company_contact_modal.html', {
            'form': form,
            'object': contact
        }, request=request)
        
        return JsonResponse({
            'success': True,
            'html': modal_html
        })
    
    elif request.method == 'POST':
        # Process the form submission
        form = CompanyContactForm(request.POST, instance=contact)
        
        if form.is_valid():
            updated_contact = form.save()
            
            # Generate updated table row HTML
            row_html = render_to_string('core/partials/company_contact_row.html', {
                'contact': updated_contact
            }, request=request)
            
            return JsonResponse({
                'success': True,
                'message': f'Contact {updated_contact.company_contact_first} {updated_contact.company_contact_last} updated successfully!',
                'object_id': updated_contact.company_contact_id,
                'row_html': row_html
            })
        else:
            # Return form with errors
            modal_html = render_to_string('core/modals/company_contact_modal.html', {
                'form': form,
                'object': contact
            }, request=request)
            
            return JsonResponse({
                'success': False,
                'html': modal_html,
                'errors': form.errors
            })

@csrf_exempt  # Temporarily disable CSRF for testing
@require_http_methods(["GET", "POST"])
def company_contact_modal_add(request):
    """AJAX view for adding new CompanyContact in modal"""
    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': False, 'error': 'AJAX request required'})
    
    if request.method == 'GET':
        # Return the modal form HTML for new contact
        form = CompanyContactForm()
        
        modal_html = render_to_string('core/modals/company_contact_modal.html', {
            'form': form,
            'object': None
        }, request=request)
        
        return JsonResponse({
            'success': True,
            'html': modal_html
        })
    
    elif request.method == 'POST':
        # Process the form submission
        form = CompanyContactForm(request.POST)
        
        if form.is_valid():
            new_contact = form.save()
            
            # Generate new table row HTML
            row_html = render_to_string('core/partials/company_contact_row.html', {
                'contact': new_contact
            }, request=request)
            
            return JsonResponse({
                'success': True,
                'message': f'Contact {new_contact.company_contact_first} {new_contact.company_contact_last} added successfully!',
                'object_id': new_contact.company_contact_id,
                'row_html': row_html,
                'action': 'add'
            })
        else:
            # Return form with errors
            modal_html = render_to_string('core/modals/company_contact_modal.html', {
                'form': form,
                'object': None
            }, request=request)
            
            return JsonResponse({
                'success': False,
                'html': modal_html,
                'errors': form.errors
            })

# Fix the pagination warning in your existing company_contact_list view
def company_contact_list(request):
    """List all company contacts with pagination and search"""
    search_query = request.GET.get('search', '')
    
    # Add ordering to fix the pagination warning
    contacts = CompanyContact.objects.select_related('company').order_by('company_contact_id')
    
    if search_query:
        contacts = contacts.filter(
            company_contact_first__icontains=search_query
        ) | contacts.filter(
            company_contact_last__icontains=search_query
        ) | contacts.filter(
            company_contact_email__icontains=search_query
        ) | contacts.filter(
            company__company_name__icontains=search_query
        )
    
    paginator = Paginator(contacts, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'title': 'Company Contacts',
        'total_count': contacts.count(),
    }
    return render(request, 'core/company_contact_list.html', context)
# =============================================================================
# ADDITIONAL AJAX MODAL VIEWS - Add these to your core/views.py file
# =============================================================================

# Add these imports to the top of your file (if not already there)
from .forms import CompanyContactForm, CompanyForm, OptionsForm

# Company AJAX Views
@csrf_exempt
@require_http_methods(["GET", "POST"])
def company_modal_edit(request, pk):
    """AJAX view for editing Company in modal"""
    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': False, 'error': 'AJAX request required'})
    
    try:
        company = get_object_or_404(Company, pk=pk)
    except Company.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Company not found'
        })

    if request.method == 'GET':
        form = CompanyForm(instance=company)
        
        modal_html = render_to_string('core/modals/company_modal.html', {
            'form': form,
            'object': company
        }, request=request)
        
        return JsonResponse({
            'success': True,
            'html': modal_html
        })
    
    elif request.method == 'POST':
        form = CompanyForm(request.POST, instance=company)
        
        if form.is_valid():
            updated_company = form.save()
            
            row_html = render_to_string('core/partials/company_row.html', {
                'company': updated_company
            }, request=request)
            
            return JsonResponse({
                'success': True,
                'message': f'Company "{updated_company.company_name}" updated successfully!',
                'object_id': updated_company.company_id,
                'row_html': row_html
            })
        else:
            modal_html = render_to_string('core/modals/company_modal.html', {
                'form': form,
                'object': company
            }, request=request)
            
            return JsonResponse({
                'success': False,
                'html': modal_html,
                'errors': form.errors
            })

@csrf_exempt
@require_http_methods(["GET", "POST"])
def company_modal_add(request):
    """AJAX view for adding new Company in modal"""
    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': False, 'error': 'AJAX request required'})
    
    if request.method == 'GET':
        form = CompanyForm()
        
        modal_html = render_to_string('core/modals/company_modal.html', {
            'form': form,
            'object': None
        }, request=request)
        
        return JsonResponse({
            'success': True,
            'html': modal_html
        })
    
    elif request.method == 'POST':
        form = CompanyForm(request.POST)
        
        if form.is_valid():
            new_company = form.save()
            
            row_html = render_to_string('core/partials/company_row.html', {
                'company': new_company
            }, request=request)
            
            return JsonResponse({
                'success': True,
                'message': f'Company "{new_company.company_name}" added successfully!',
                'object_id': new_company.company_id,
                'row_html': row_html,
                'action': 'add'
            })
        else:
            modal_html = render_to_string('core/modals/company_modal.html', {
                'form': form,
                'object': None
            }, request=request)
            
            return JsonResponse({
                'success': False,
                'html': modal_html,
                'errors': form.errors
            })

# Options AJAX Views
@csrf_exempt
@require_http_methods(["GET", "POST"])
def options_modal_edit(request, pk):
    """AJAX view for editing Options in modal"""
    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': False, 'error': 'AJAX request required'})
    
    try:
        option = get_object_or_404(Options, pk=pk)
    except Options.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Option not found'
        })

    if request.method == 'GET':
        form = OptionsForm(instance=option)
        
        modal_html = render_to_string('core/modals/options_modal.html', {
            'form': form,
            'object': option
        }, request=request)
        
        return JsonResponse({
            'success': True,
            'html': modal_html
        })
    
    elif request.method == 'POST':
        form = OptionsForm(request.POST, instance=option)
        
        if form.is_valid():
            updated_option = form.save()
            
            row_html = render_to_string('core/partials/options_row.html', {
                'option': updated_option
            }, request=request)
            
            return JsonResponse({
                'success': True,
                'message': f'Option "{updated_option.option_name}" updated successfully!',
                'object_id': updated_option.options_id,
                'row_html': row_html
            })
        else:
            modal_html = render_to_string('core/modals/options_modal.html', {
                'form': form,
                'object': option
            }, request=request)
            
            return JsonResponse({
                'success': False,
                'html': modal_html,
                'errors': form.errors
            })

@csrf_exempt
@require_http_methods(["GET", "POST"])
def options_modal_add(request):
    """AJAX view for adding new Options in modal"""
    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': False, 'error': 'AJAX request required'})
    
    if request.method == 'GET':
        form = OptionsForm()
        
        modal_html = render_to_string('core/modals/options_modal.html', {
            'form': form,
            'object': None
        }, request=request)
        
        return JsonResponse({
            'success': True,
            'html': modal_html
        })
    
    elif request.method == 'POST':
        form = OptionsForm(request.POST)
        
        if form.is_valid():
            new_option = form.save()
            
            row_html = render_to_string('core/partials/options_row.html', {
                'option': new_option
            }, request=request)
            
            return JsonResponse({
                'success': True,
                'message': f'Option "{new_option.option_name}" added successfully!',
                'object_id': new_option.options_id,
                'row_html': row_html,
                'action': 'add'
            })
        else:
            modal_html = render_to_string('core/modals/options_modal.html', {
                'form': form,
                'object': None
            }, request=request)
            
            return JsonResponse({
                'success': False,
                'html': modal_html,
                'errors': form.errors
            })

# Company Location AJAX Views
@csrf_exempt
@require_http_methods(["GET", "POST"])
def company_location_modal_edit(request, pk):
    """AJAX view for editing CompanyLocation in modal"""
    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': False, 'error': 'AJAX request required'})
    
    try:
        location = get_object_or_404(CompanyLocation, pk=pk)
    except CompanyLocation.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Location not found'})

    if request.method == 'GET':
        form = CompanyLocationForm(instance=location)
        modal_html = render_to_string('core/modals/company_location_modal.html', {
            'form': form, 'object': location
        }, request=request)
        return JsonResponse({'success': True, 'html': modal_html})
    
    elif request.method == 'POST':
        form = CompanyLocationForm(request.POST, instance=location)
        if form.is_valid():
            updated_location = form.save()
            row_html = render_to_string('core/partials/company_location_row.html', {
                'location': updated_location
            }, request=request)
            return JsonResponse({
                'success': True,
                'message': f'Location updated successfully!',
                'object_id': updated_location.company_location_id,
                'row_html': row_html
            })
        else:
            modal_html = render_to_string('core/modals/company_location_modal.html', {
                'form': form, 'object': location
            }, request=request)
            return JsonResponse({'success': False, 'html': modal_html, 'errors': form.errors})

@csrf_exempt
@require_http_methods(["GET", "POST"])
def company_location_modal_add(request):
    """AJAX view for adding new CompanyLocation in modal"""
    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': False, 'error': 'AJAX request required'})
    
    if request.method == 'GET':
        form = CompanyLocationForm()
        modal_html = render_to_string('core/modals/company_location_modal.html', {
            'form': form, 'object': None
        }, request=request)
        return JsonResponse({'success': True, 'html': modal_html})
    
    elif request.method == 'POST':
        form = CompanyLocationForm(request.POST)
        if form.is_valid():
            new_location = form.save()
            row_html = render_to_string('core/partials/company_location_row.html', {
                'location': new_location
            }, request=request)
            return JsonResponse({
                'success': True,
                'message': f'Location added successfully!',
                'object_id': new_location.company_location_id,
                'row_html': row_html,
                'action': 'add'
            })
        else:
            modal_html = render_to_string('core/modals/company_location_modal.html', {
                'form': form, 'object': None
            }, request=request)
            return JsonResponse({'success': False, 'html': modal_html, 'errors': form.errors})

# Company Alias AJAX Views
@csrf_exempt
@require_http_methods(["GET", "POST"])
def company_alias_modal_edit(request, pk):
    """AJAX view for editing CompanyAlias in modal"""
    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': False, 'error': 'AJAX request required'})
    
    try:
        alias = get_object_or_404(CompanyAlias, pk=pk)
    except CompanyAlias.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Alias not found'})

    if request.method == 'GET':
        form = CompanyAliasForm(instance=alias)
        modal_html = render_to_string('core/modals/company_alias_modal.html', {
            'form': form, 'object': alias
        }, request=request)
        return JsonResponse({'success': True, 'html': modal_html})
    
    elif request.method == 'POST':
        form = CompanyAliasForm(request.POST, instance=alias)
        if form.is_valid():
            updated_alias = form.save()
            row_html = render_to_string('core/partials/company_alias_row.html', {
                'alias': updated_alias
            }, request=request)
            return JsonResponse({
                'success': True,
                'message': f'Alias "{updated_alias.company_alias_name}" updated successfully!',
                'object_id': updated_alias.company_alias_id,
                'row_html': row_html
            })
        else:
            modal_html = render_to_string('core/modals/company_alias_modal.html', {
                'form': form, 'object': alias
            }, request=request)
            return JsonResponse({'success': False, 'html': modal_html, 'errors': form.errors})

@csrf_exempt
@require_http_methods(["GET", "POST"])
def company_alias_modal_add(request):
    """AJAX view for adding new CompanyAlias in modal"""
    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': False, 'error': 'AJAX request required'})
    
    if request.method == 'GET':
        form = CompanyAliasForm()
        modal_html = render_to_string('core/modals/company_alias_modal.html', {
            'form': form, 'object': None
        }, request=request)
        return JsonResponse({'success': True, 'html': modal_html})
    
    elif request.method == 'POST':
        form = CompanyAliasForm(request.POST)
        if form.is_valid():
            new_alias = form.save()
            row_html = render_to_string('core/partials/company_alias_row.html', {
                'alias': new_alias
            }, request=request)
            return JsonResponse({
                'success': True,
                'message': f'Alias "{new_alias.company_alias_name}" added successfully!',
                'object_id': new_alias.company_alias_id,
                'row_html': row_html,
                'action': 'add'
            })
        else:
            modal_html = render_to_string('core/modals/company_alias_modal.html', {
                'form': form, 'object': None
            }, request=request)
            return JsonResponse({'success': False, 'html': modal_html, 'errors': form.errors})

# Application Response AJAX Views
@csrf_exempt
@require_http_methods(["GET", "POST"])
def application_response_modal_edit(request, pk):
    """AJAX view for editing ApplicationResponse in modal"""
    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': False, 'error': 'AJAX request required'})
    
    try:
        response = get_object_or_404(ApplicationResponse, pk=pk)
    except ApplicationResponse.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Response not found'})

    if request.method == 'GET':
        form = ApplicationResponseForm(instance=response)
        modal_html = render_to_string('core/modals/application_response_modal.html', {
            'form': form, 'object': response
        }, request=request)
        return JsonResponse({'success': True, 'html': modal_html})
    
    elif request.method == 'POST':
        form = ApplicationResponseForm(request.POST, instance=response)
        if form.is_valid():
            updated_response = form.save()
            row_html = render_to_string('core/partials/application_response_row.html', {
                'response': updated_response
            }, request=request)
            return JsonResponse({
                'success': True,
                'message': f'Application response updated successfully!',
                'object_id': updated_response.application_response_id,
                'row_html': row_html
            })
        else:
            modal_html = render_to_string('core/modals/application_response_modal.html', {
                'form': form, 'object': response
            }, request=request)
            return JsonResponse({'success': False, 'html': modal_html, 'errors': form.errors})

@csrf_exempt
@require_http_methods(["GET", "POST"])
def application_response_modal_add(request):
    """AJAX view for adding new ApplicationResponse in modal"""
    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': False, 'error': 'AJAX request required'})
    
    if request.method == 'GET':
        form = ApplicationResponseForm()
        modal_html = render_to_string('core/modals/application_response_modal.html', {
            'form': form, 'object': None
        }, request=request)
        return JsonResponse({'success': True, 'html': modal_html})
    
    elif request.method == 'POST':
        form = ApplicationResponseForm(request.POST)
        if form.is_valid():
            new_response = form.save()
            row_html = render_to_string('core/partials/application_response_row.html', {
                'response': new_response
            }, request=request)
            return JsonResponse({
                'success': True,
                'message': f'Application response added successfully!',
                'object_id': new_response.application_response_id,
                'row_html': row_html,
                'action': 'add'
            })
        else:
            modal_html = render_to_string('core/modals/application_response_modal.html', {
                'form': form, 'object': None
            }, request=request)
            return JsonResponse({'success': False, 'html': modal_html, 'errors': form.errors})

# Order Option AJAX Views  
@csrf_exempt
@require_http_methods(["GET", "POST"])
def order_option_modal_edit(request, pk):
    """AJAX view for editing OrderOption in modal"""
    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': False, 'error': 'AJAX request required'})
    
    try:
        order_option = get_object_or_404(OrderOption, pk=pk)
    except OrderOption.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Order option not found'})

    if request.method == 'GET':
        form = OrderOptionForm(instance=order_option)
        modal_html = render_to_string('core/modals/order_option_modal.html', {
            'form': form, 'object': order_option
        }, request=request)
        return JsonResponse({'success': True, 'html': modal_html})
    
    elif request.method == 'POST':
        form = OrderOptionForm(request.POST, instance=order_option)
        if form.is_valid():
            updated_order_option = form.save()
            row_html = render_to_string('core/partials/order_option_row.html', {
                'order_option': updated_order_option
            }, request=request)
            return JsonResponse({
                'success': True,
                'message': f'Order option updated successfully!',
                'object_id': updated_order_option.order_option_id,
                'row_html': row_html
            })
        else:
            modal_html = render_to_string('core/modals/order_option_modal.html', {
                'form': form, 'object': order_option
            }, request=request)
            return JsonResponse({'success': False, 'html': modal_html, 'errors': form.errors})

@csrf_exempt
@require_http_methods(["GET", "POST"])
def order_option_modal_add(request):
    """AJAX view for adding new OrderOption in modal"""
    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': False, 'error': 'AJAX request required'})
    
    if request.method == 'GET':
        form = OrderOptionForm()
        modal_html = render_to_string('core/modals/order_option_modal.html', {
            'form': form, 'object': None
        }, request=request)
        return JsonResponse({'success': True, 'html': modal_html})
    
    elif request.method == 'POST':
        form = OrderOptionForm(request.POST)
        if form.is_valid():
            new_order_option = form.save()
            row_html = render_to_string('core/partials/order_option_row.html', {
                'order_option': new_order_option
            }, request=request)
            return JsonResponse({
                'success': True,
                'message': f'Order option added successfully!',
                'object_id': new_order_option.order_option_id,
                'row_html': row_html,
                'action': 'add'
            })
        else:
            modal_html = render_to_string('core/modals/order_option_modal.html', {
                'form': form, 'object': None
            }, request=request)
            return JsonResponse({'success': False, 'html': modal_html, 'errors': form.errors})

# Order Data Vert AJAX Views
@csrf_exempt
@require_http_methods(["GET", "POST"])
def order_data_vert_modal_edit(request, pk):
    """AJAX view for editing OrderDataVert in modal"""
    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': False, 'error': 'AJAX request required'})
    
    try:
        order_data_vert = get_object_or_404(OrderDataVert, pk=pk)
    except OrderDataVert.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Order data vert not found'})

    if request.method == 'GET':
        form = OrderDataVertForm(instance=order_data_vert)
        modal_html = render_to_string('core/modals/order_data_vert_modal.html', {
            'form': form, 'object': order_data_vert
        }, request=request)
        return JsonResponse({'success': True, 'html': modal_html})
    
    elif request.method == 'POST':
        form = OrderDataVertForm(request.POST, instance=order_data_vert)
        if form.is_valid():
            updated_order_data_vert = form.save()
            row_html = render_to_string('core/partials/order_data_vert_row.html', {
                'order_data_vert': updated_order_data_vert
            }, request=request)
            return JsonResponse({
                'success': True,
                'message': f'Order data vert updated successfully!',
                'object_id': updated_order_data_vert.order_date_vert_id,
                'row_html': row_html
            })
        else:
            modal_html = render_to_string('core/modals/order_data_vert_modal.html', {
                'form': form, 'object': order_data_vert
            }, request=request)
            return JsonResponse({'success': False, 'html': modal_html, 'errors': form.errors})

@csrf_exempt
@require_http_methods(["GET", "POST"])
def order_data_vert_modal_add(request):
    """AJAX view for adding new OrderDataVert in modal"""
    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': False, 'error': 'AJAX request required'})
    
    if request.method == 'GET':
        form = OrderDataVertForm()
        modal_html = render_to_string('core/modals/order_data_vert_modal.html', {
            'form': form, 'object': None
        }, request=request)
        return JsonResponse({'success': True, 'html': modal_html})
    
    elif request.method == 'POST':
        form = OrderDataVertForm(request.POST)
        if form.is_valid():
            new_order_data_vert = form.save()
            row_html = render_to_string('core/partials/order_data_vert_row.html', {
                'order_data_vert': new_order_data_vert
            }, request=request)
            return JsonResponse({
                'success': True,
                'message': f'Order data vert added successfully!',
                'object_id': new_order_data_vert.order_date_vert_id,
                'row_html': row_html,
                'action': 'add'
            })
        else:
            modal_html = render_to_string('core/modals/order_data_vert_modal.html', {
                'form': form, 'object': None
            }, request=request)
            return JsonResponse({'success': False, 'html': modal_html, 'errors': form.errors})

# Document Detail AJAX Views
@csrf_exempt
@require_http_methods(["GET", "POST"])
def document_detail_modal_edit(request, pk):
    """AJAX view for editing DocumentDetail in modal"""
    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': False, 'error': 'AJAX request required'})
    
    try:
        document_detail = get_object_or_404(DocumentDetail, pk=pk)
    except DocumentDetail.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Document detail not found'})

    if request.method == 'GET':
        form = DocumentDetailForm(instance=document_detail)
        modal_html = render_to_string('core/modals/document_detail_modal.html', {
            'form': form, 'object': document_detail
        }, request=request)
        return JsonResponse({'success': True, 'html': modal_html})
    
    elif request.method == 'POST':
        form = DocumentDetailForm(request.POST, instance=document_detail)
        if form.is_valid():
            updated_document_detail = form.save()
            row_html = render_to_string('core/partials/document_detail_row.html', {
                'document_detail': updated_document_detail
            }, request=request)
            return JsonResponse({
                'success': True,
                'message': f'Document detail updated successfully!',
                'object_id': updated_document_detail.document_detail_id,
                'row_html': row_html
            })
        else:
            modal_html = render_to_string('core/modals/document_detail_modal.html', {
                'form': form, 'object': document_detail
            }, request=request)
            return JsonResponse({'success': False, 'html': modal_html, 'errors': form.errors})

@csrf_exempt
@require_http_methods(["GET", "POST"])
def document_detail_modal_add(request):
    """AJAX view for adding new DocumentDetail in modal"""
    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': False, 'error': 'AJAX request required'})
    
    if request.method == 'GET':
        form = DocumentDetailForm()
        modal_html = render_to_string('core/modals/document_detail_modal.html', {
            'form': form, 'object': None
        }, request=request)
        return JsonResponse({'success': True, 'html': modal_html})
    
    elif request.method == 'POST':
        form = DocumentDetailForm(request.POST)
        if form.is_valid():
            new_document_detail = form.save()
            row_html = render_to_string('core/partials/document_detail_row.html', {
                'document_detail': new_document_detail
            }, request=request)
            return JsonResponse({
                'success': True,
                'message': f'Document detail added successfully!',
                'object_id': new_document_detail.document_detail_id,
                'row_html': row_html,
                'action': 'add'
            })
        else:
            modal_html = render_to_string('core/modals/document_detail_modal.html', {
                'form': form, 'object': None
            }, request=request)
            return JsonResponse({'success': False, 'html': modal_html, 'errors': form.errors})

# =============================================================================
# CATALOG AJAX MODAL VIEWS - Add these to your core/views.py file
# =============================================================================

# Add these imports to your existing imports section
from .forms import (
    # ... your existing imports ...
    ProductsForm, EmployeeFunctionForm
)

# Products AJAX Views
@csrf_exempt
@require_http_methods(["GET", "POST"])
def products_modal_edit(request, pk):
    """AJAX view for editing Products in modal"""
    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': False, 'error': 'AJAX request required'})
    
    try:
        product = get_object_or_404(Products, pk=pk)
    except Products.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Product not found'})

    if request.method == 'GET':
        form = ProductsForm(instance=product)
        modal_html = render_to_string('core/modals/products_modal.html', {
            'form': form, 'object': product
        }, request=request)
        return JsonResponse({'success': True, 'html': modal_html})
    
    elif request.method == 'POST':
        form = ProductsForm(request.POST, instance=product)
        if form.is_valid():
            updated_product = form.save()
            row_html = render_to_string('core/partials/products_row.html', {
                'product': updated_product
            }, request=request)
            return JsonResponse({
                'success': True,
                'message': f'Product "{updated_product.product_name}" updated successfully!',
                'object_id': updated_product.products_id,
                'row_html': row_html
            })
        else:
            modal_html = render_to_string('core/modals/products_modal.html', {
                'form': form, 'object': product
            }, request=request)
            return JsonResponse({'success': False, 'html': modal_html, 'errors': form.errors})

@csrf_exempt
@require_http_methods(["GET", "POST"])
def products_modal_add(request):
    """AJAX view for adding new Products in modal"""
    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': False, 'error': 'AJAX request required'})
    
    if request.method == 'GET':
        form = ProductsForm()
        modal_html = render_to_string('core/modals/products_modal.html', {
            'form': form, 'object': None
        }, request=request)
        return JsonResponse({'success': True, 'html': modal_html})
    
    elif request.method == 'POST':
        form = ProductsForm(request.POST)
        if form.is_valid():
            new_product = form.save()
            row_html = render_to_string('core/partials/products_row.html', {
                'product': new_product
            }, request=request)
            return JsonResponse({
                'success': True,
                'message': f'Product "{new_product.product_name}" added successfully!',
                'object_id': new_product.products_id,
                'row_html': row_html,
                'action': 'add'
            })
        else:
            modal_html = render_to_string('core/modals/products_modal.html', {
                'form': form, 'object': None
            }, request=request)
            return JsonResponse({'success': False, 'html': modal_html, 'errors': form.errors})

# Employee Function AJAX Views
@csrf_exempt
@require_http_methods(["GET", "POST"])
def employee_function_modal_edit(request, pk):
    """AJAX view for editing EmployeeFunction in modal"""
    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': False, 'error': 'AJAX request required'})
    
    try:
        function = get_object_or_404(EmployeeFunction, pk=pk)
    except EmployeeFunction.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Function not found'})

    if request.method == 'GET':
        form = EmployeeFunctionForm(instance=function)
        modal_html = render_to_string('core/modals/employee_function_modal.html', {
            'form': form, 'object': function
        }, request=request)
        return JsonResponse({'success': True, 'html': modal_html})
    
    elif request.method == 'POST':
        form = EmployeeFunctionForm(request.POST, instance=function)
        if form.is_valid():
            updated_function = form.save()
            row_html = render_to_string('core/partials/employee_function_row.html', {
                'function': updated_function
            }, request=request)
            return JsonResponse({
                'success': True,
                'message': f'Function "{updated_function.employee_function}" updated successfully!',
                'object_id': updated_function.employee_function_id,
                'row_html': row_html
            })
        else:
            modal_html = render_to_string('core/modals/employee_function_modal.html', {
                'form': form, 'object': function
            }, request=request)
            return JsonResponse({'success': False, 'html': modal_html, 'errors': form.errors})

@csrf_exempt
@require_http_methods(["GET", "POST"])
def employee_function_modal_add(request):
    """AJAX view for adding new EmployeeFunction in modal"""
    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': False, 'error': 'AJAX request required'})
    
    if request.method == 'GET':
        form = EmployeeFunctionForm()
        modal_html = render_to_string('core/modals/employee_function_modal.html', {
            'form': form, 'object': None
        }, request=request)
        return JsonResponse({'success': True, 'html': modal_html})
    
    elif request.method == 'POST':
        form = EmployeeFunctionForm(request.POST)
        if form.is_valid():
            new_function = form.save()
            row_html = render_to_string('core/partials/employee_function_row.html', {
                'function': new_function
            }, request=request)
            return JsonResponse({
                'success': True,
                'message': f'Function "{new_function.employee_function}" added successfully!',
                'object_id': new_function.employee_function_id,
                'row_html': row_html,
                'action': 'add'
            })
        else:
            modal_html = render_to_string('core/modals/employee_function_modal.html', {
                'form': form, 'object': None
            }, request=request)
            return JsonResponse({'success': False, 'html': modal_html, 'errors': form.errors})

# Note: Employee Contact already has AJAX views from workstation implementation