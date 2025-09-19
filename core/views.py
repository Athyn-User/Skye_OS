# core/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.core.paginator import Paginator
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets
from rest_framework.decorators import api_view
from .models import (
    Venture, Drive, EmployeeLocation, GenerationJob, Parameter,
    DataSeed, GenerationLog, ModelParameter, TrainingJob, Products,
    GenerationModel, TrainingModel, InputOutput, EmployeeContact,
    Cover, EmployeeFunction, Paper, PaperDetail, Applications, ApplicationQuestion,
    ParameterMap, Document, Task, Coverage, Company, Options, CompanyLocation, 
    CompanyAlias, ApplicationResponse, OrderOption, OrderDataVert, DocumentDetail,
    CompanyContact, Workflow, WorkflowDetail, Orders
)
from .forms import (
    CompanyContactForm, ProductsForm, EmployeeFunctionForm, VentureForm,
    CoverageForm, DriveForm, EmployeeLocationForm, CompanyForm, OptionsForm,
    CompanyLocationForm, CompanyAliasForm, ApplicationResponseForm,
    OrderOptionForm, OrderDataVertForm, DocumentDetailForm
)

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
    
    # NEWEST sections - Parameter, ParameterMap, Document, Task
    parameters = Parameter.objects.all()
    parameter_maps = ParameterMap.objects.select_related('products', 'parameter').all()
    documents = Document.objects.select_related('product').all()
    tasks = Task.objects.all()
    
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
        # Add the 4 newest data sets
        'parameters': parameters,@csrf_exempt

@api_view(['GET', 'POST'])
def company_modal_edit(request, pk):
    """AJAX view for editing Company in modal"""
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
@api_view(['GET', 'POST'])  
def company_modal_add(request):
    """AJAX view for adding new Company in modal"""
    
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

@csrf_exempt
@api_view(['GET', 'POST'])
def options_modal_edit(request, pk):
    """AJAX view for editing Options in modal"""
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
@api_view(['GET', 'POST'])  
def options_modal_add(request):
    """AJAX view for adding new Options in modal"""
    
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

@csrf_exempt
@api_view(['GET', 'POST'])
def company_location_modal_edit(request, pk):
    """AJAX view for editing CompanyLocation in modal"""
    try:
        location = get_object_or_404(CompanyLocation, pk=pk)
    except CompanyLocation.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Company location not found'
        })

    if request.method == 'GET':
        form = CompanyLocationForm(instance=location)
        
        modal_html = render_to_string('core/modals/company_location_modal.html', {
            'form': form,
            'object': location
        }, request=request)
        
        return JsonResponse({
            'success': True,
            'html': modal_html
        })
    
    elif request.method == 'POST':
        form = CompanyLocationForm(request.POST, instance=location)
        
        if form.is_valid():
            updated_location = form.save()
            
            row_html = render_to_string('core/partials/company_location_row.html', {
                'location': updated_location
            }, request=request)
            
            return JsonResponse({
                'success': True,
                'message': 'Company location updated successfully!',
                'object_id': updated_location.company_location_id,
                'row_html': row_html
            })
        else:
            modal_html = render_to_string('core/modals/company_location_modal.html', {
                'form': form,
                'object': location
            }, request=request)
            
            return JsonResponse({
                'success': False,
                'html': modal_html,
                'errors': form.errors
            })

@csrf_exempt
@api_view(['GET', 'POST'])  
def company_location_modal_add(request):
    """AJAX view for adding new CompanyLocation in modal"""
    
    if request.method == 'GET':
        form = CompanyLocationForm()
        
        modal_html = render_to_string('core/modals/company_location_modal.html', {
            'form': form,
            'object': None
        }, request=request)
        
        return JsonResponse({
            'success': True,
            'html': modal_html
        })
    
    elif request.method == 'POST':
        form = CompanyLocationForm(request.POST)
        
        if form.is_valid():
            new_location = form.save()
            
            row_html = render_to_string('core/partials/company_location_row.html', {
                'location': new_location
            }, request=request)
            
            return JsonResponse({
                'success': True,
                'message': 'Company location added successfully!',
                'object_id': new_location.company_location_id,
                'row_html': row_html,
                'action': 'add'
            })
        else:
            modal_html = render_to_string('core/modals/company_location_modal.html', {
                'form': form,
                'object': None
            }, request=request)
            
            return JsonResponse({
                'success': False,
                'html': modal_html,
                'errors': form.errors
            })

@csrf_exempt
@api_view(['GET', 'POST'])
def company_alias_modal_edit(request, pk):
    """AJAX view for editing CompanyAlias in modal"""
    try:
        alias = get_object_or_404(CompanyAlias, pk=pk)
    except CompanyAlias.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Company alias not found'
        })

    if request.method == 'GET':
        form = CompanyAliasForm(instance=alias)
        
        modal_html = render_to_string('core/modals/company_alias_modal.html', {
            'form': form,
            'object': alias
        }, request=request)
        
        return JsonResponse({
            'success': True,
            'html': modal_html
        })
    
    elif request.method == 'POST':
        form = CompanyAliasForm(request.POST, instance=alias)
        
        if form.is_valid():
            updated_alias = form.save()
            
            row_html = render_to_string('core/partials/company_alias_row.html', {
                'alias': updated_alias
            }, request=request)
            
            return JsonResponse({
                'success': True,
                'message': f'Company alias "{updated_alias.company_alias_name}" updated successfully!',
                'object_id': updated_alias.company_alias_id,
                'row_html': row_html
            })
        else:
            modal_html = render_to_string('core/modals/company_alias_modal.html', {
                'form': form,
                'object': alias
            }, request=request)
            
            return JsonResponse({
                'success': False,
                'html': modal_html,
                'errors': form.errors
            })

@csrf_exempt
@api_view(['GET', 'POST'])  
def company_alias_modal_add(request):
    """AJAX view for adding new CompanyAlias in modal"""
    
    if request.method == 'GET':
        form = CompanyAliasForm()
        
        modal_html = render_to_string('core/modals/company_alias_modal.html', {
            'form': form,
            'object': None
        }, request=request)
        
        return JsonResponse({
            'success': True,
            'html': modal_html
        })
    
    elif request.method == 'POST':
        form = CompanyAliasForm(request.POST)
        
        if form.is_valid():
            new_alias = form.save()
            
            row_html = render_to_string('core/partials/company_alias_row.html', {
                'alias': new_alias
            }, request=request)
            
            return JsonResponse({
                'success': True,
                'message': f'Company alias "{new_alias.company_alias_name}" added successfully!',
                'object_id': new_alias.company_alias_id,
                'row_html': row_html,
                'action': 'add'
            })
        else:
            modal_html = render_to_string('core/modals/company_alias_modal.html', {
                'form': form,
                'object': None
            }, request=request)
            
            return JsonResponse({
                'success': False,
                'html': modal_html,
                'errors': form.errors
            })

@csrf_exempt
@api_view(['GET', 'POST'])
def application_response_modal_edit(request, pk):
    """AJAX view for editing ApplicationResponse in modal"""
    try:
        response = get_object_or_404(ApplicationResponse, pk=pk)
    except ApplicationResponse.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Application response not found'
        })

    if request.method == 'GET':
        form = ApplicationResponseForm(instance=response)
        
        modal_html = render_to_string('core/modals/application_response_modal.html', {
            'form': form,
            'object': response
        }, request=request)
        
        return JsonResponse({
            'success': True,
            'html': modal_html
        })
    
    elif request.method == 'POST':
        form = ApplicationResponseForm(request.POST, instance=response)
        
        if form.is_valid():
            updated_response = form.save()
            
            row_html = render_to_string('core/partials/application_response_row.html', {
                'response': updated_response
            }, request=request)
            
            return JsonResponse({
                'success': True,
                'message': 'Application response updated successfully!',
                'object_id': updated_response.application_response_id,
                'row_html': row_html
            })
        else:
            modal_html = render_to_string('core/modals/application_response_modal.html', {
                'form': form,
                'object': response
            }, request=request)
            
            return JsonResponse({
                'success': False,
                'html': modal_html,
                'errors': form.errors
            })

@csrf_exempt
@api_view(['GET', 'POST'])  
def application_response_modal_add(request):
    """AJAX view for adding new ApplicationResponse in modal"""
    
    if request.method == 'GET':
        form = ApplicationResponseForm()
        
        modal_html = render_to_string('core/modals/application_response_modal.html', {
            'form': form,
            'object': None
        }, request=request)
        
        return JsonResponse({
            'success': True,
            'html': modal_html
        })
    
    elif request.method == 'POST':
        form = ApplicationResponseForm(request.POST)
        
        if form.is_valid():
            new_response = form.save()
            
            row_html = render_to_string('core/partials/application_response_row.html', {
                'response': new_response
            }, request=request)
            
            return JsonResponse({
                'success': True,
                'message': 'Application response added successfully!',
                'object_id': new_response.application_response_id,
                'row_html': row_html,
                'action': 'add'
            })
        else:
            modal_html = render_to_string('core/modals/application_response_modal.html', {
                'form': form,
                'object': None
            }, request=request)
            
            return JsonResponse({
                'success': False,
                'html': modal_html,
                'errors': form.errors
            })

@csrf_exempt
@api_view(['GET', 'POST'])
def order_option_modal_edit(request, pk):
    """AJAX view for editing OrderOption in modal"""
    try:
        order_option = get_object_or_404(OrderOption, pk=pk)
    except OrderOption.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Order option not found'
        })

    if request.method == 'GET':
        form = OrderOptionForm(instance=order_option)
        
        modal_html = render_to_string('core/modals/order_option_modal.html', {
            'form': form,
            'object': order_option
        }, request=request)
        
        return JsonResponse({
            'success': True,
            'html': modal_html
        })
    
    elif request.method == 'POST':
        form = OrderOptionForm(request.POST, instance=order_option)
        
        if form.is_valid():
            updated_order_option = form.save()
            
            row_html = render_to_string('core/partials/order_option_row.html', {
                'order_option': updated_order_option
            }, request=request)
            
            return JsonResponse({
                'success': True,
                'message': 'Order option updated successfully!',
                'object_id': updated_order_option.order_option_id,
                'row_html': row_html
            })
        else:
            modal_html = render_to_string('core/modals/order_option_modal.html', {
                'form': form,
                'object': order_option
            }, request=request)
            
            return JsonResponse({
                'success': False,
                'html': modal_html,
                'errors': form.errors
            })

@csrf_exempt
@api_view(['GET', 'POST'])  
def order_option_modal_add(request):
    """AJAX view for adding new OrderOption in modal"""
    
    if request.method == 'GET':
        form = OrderOptionForm()
        
        modal_html = render_to_string('core/modals/order_option_modal.html', {
            'form': form,
            'object': None
        }, request=request)
        
        return JsonResponse({
            'success': True,
            'html': modal_html
        })
    
    elif request.method == 'POST':
        form = OrderOptionForm(request.POST)
        
        if form.is_valid():
            new_order_option = form.save()
            
            row_html = render_to_string('core/partials/order_option_row.html', {
                'order_option': new_order_option
            }, request=request)
            
            return JsonResponse({
                'success': True,
                'message': 'Order option added successfully!',
                'object_id': new_order_option.order_option_id,
                'row_html': row_html,
                'action': 'add'
            })
        else:
            modal_html = render_to_string('core/modals/order_option_modal.html', {
                'form': form,
                'object': None
            }, request=request)
            
            return JsonResponse({
                'success': False,
                'html': modal_html,
                'errors': form.errors
            })

@csrf_exempt
@api_view(['GET', 'POST'])
def order_data_vert_modal_edit(request, pk):
    """AJAX view for editing OrderDataVert in modal"""
    try:
        order_data_vert = get_object_or_404(OrderDataVert, pk=pk)
    except OrderDataVert.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Order data vert not found'
        })

    if request.method == 'GET':
        form = OrderDataVertForm(instance=order_data_vert)
        
        modal_html = render_to_string('core/modals/order_data_vert_modal.html', {
            'form': form,
            'object': order_data_vert
        }, request=request)
        
        return JsonResponse({
            'success': True,
            'html': modal_html
        })
    
    elif request.method == 'POST':
        form = OrderDataVertForm(request.POST, instance=order_data_vert)
        
        if form.is_valid():
            updated_order_data_vert = form.save()
            
            row_html = render_to_string('core/partials/order_data_vert_row.html', {
                'order_data_vert': updated_order_data_vert
            }, request=request)
            
            return JsonResponse({
                'success': True,
                'message': 'Order data vert updated successfully!',
                'object_id': updated_order_data_vert.order_date_vert_id,
                'row_html': row_html
            })
        else:
            modal_html = render_to_string('core/modals/order_data_vert_modal.html', {
                'form': form,
                'object': order_data_vert
            }, request=request)
            
            return JsonResponse({
                'success': False,
                'html': modal_html,
                'errors': form.errors
            })

@csrf_exempt
@api_view(['GET', 'POST'])  
def order_data_vert_modal_add(request):
    """AJAX view for adding new OrderDataVert in modal"""
    
    if request.method == 'GET':
        form = OrderDataVertForm()
        
        modal_html = render_to_string('core/modals/order_data_vert_modal.html', {
            'form': form,
            'object': None
        }, request=request)
        
        return JsonResponse({
            'success': True,
            'html': modal_html
        })
    
    elif request.method == 'POST':
        form = OrderDataVertForm(request.POST)
        
        if form.is_valid():
            new_order_data_vert = form.save()
            
            row_html = render_to_string('core/partials/order_data_vert_row.html', {
                'order_data_vert': new_order_data_vert
            }, request=request)
            
            return JsonResponse({
                'success': True,
                'message': 'Order data vert added successfully!',
                'object_id': new_order_data_vert.order_date_vert_id,
                'row_html': row_html,
                'action': 'add'
            })
        else:
            modal_html = render_to_string('core/modals/order_data_vert_modal.html', {
                'form': form,
                'object': None
            }, request=request)
            
            return JsonResponse({
                'success': False,
                'html': modal_html,
                'errors': form.errors
            })

@csrf_exempt
@api_view(['GET', 'POST'])
def document_detail_modal_edit(request, pk):
    """AJAX view for editing DocumentDetail in modal"""
    try:
        document_detail = get_object_or_404(DocumentDetail, pk=pk)
    except DocumentDetail.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Document detail not found'
        })

    if request.method == 'GET':
        form = DocumentDetailForm(instance=document_detail)
        
        modal_html = render_to_string('core/modals/document_detail_modal.html', {
            'form': form,
            'object': document_detail
        }, request=request)
        
        return JsonResponse({
            'success': True,
            'html': modal_html
        })
    
    elif request.method == 'POST':
        form = DocumentDetailForm(request.POST, instance=document_detail)
        
        if form.is_valid():
            updated_document_detail = form.save()
            
            row_html = render_to_string('core/partials/document_detail_row.html', {
                'document_detail': updated_document_detail
            }, request=request)
            
            return JsonResponse({
                'success': True,
                'message': 'Document detail updated successfully!',
                'object_id': updated_document_detail.document_detail_id,
                'row_html': row_html
            })
        else:
            modal_html = render_to_string('core/modals/document_detail_modal.html', {
                'form': form,
                'object': document_detail
            }, request=request)
            
            return JsonResponse({
                'success': False,
                'html': modal_html,
                'errors': form.errors
            })

@csrf_exempt
@api_view(['GET', 'POST'])  
def document_detail_modal_add(request):
    """AJAX view for adding new DocumentDetail in modal"""
    
    if request.method == 'GET':
        form = DocumentDetailForm()
        
        modal_html = render_to_string('core/modals/document_detail_modal.html', {
            'form': form,
            'object': None
        }, request=request)
        
        return JsonResponse({
            'success': True,
            'html': modal_html
        })
    
    elif request.method == 'POST':
        form = DocumentDetailForm(request.POST)
        
        if form.is_valid():
            new_document_detail = form.save()
            
            row_html = render_to_string('core/partials/document_detail_row.html', {
                'document_detail': new_document_detail
            }, request=request)
            
            return JsonResponse({
                'success': True,
                'message': 'Document detail added successfully!',
                'object_id': new_document_detail.document_detail_id,
                'row_html': row_html,
                'action': 'add'
            })
        else:
            modal_html = render_to_string('core/modals/document_detail_modal.html', {
                'form': form,
                'object': None
            }, request=request)
            
            return JsonResponse({
                'success': False,
                'html': modal_html,
                'errors': form.errors
            })
        'parameter_maps': parameter_maps,
        'documents': documents,
        'tasks': tasks,
    }
    return render(request, 'core/catalog.html', context)

def dashboard_view(request):
    """Main dashboard view"""
    return render(request, 'core/dashboard.html')

# =============================================================================
# MACHINE LEARNING SECTION
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
# GENERIC CRUD OPERATIONS (for future extensibility)
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
# PAPER SECTION
# =============================================================================

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
    
    context = {
        'object': paper,
        'title': f'Paper: {paper.paper_name or f"Paper {paper.paper_id}"}',
        'list_url': 'core:paper_list',
    }
    return render(request, 'core/paper_detail.html', context)

# =============================================================================
# PAPER DETAIL SECTION  
# =============================================================================

def paper_detail_list(request):
    """List all paper details"""
    search_query = request.GET.get('search', '')
    
    paper_details = PaperDetail.objects.select_related('products', 'paper').all()
    
    if search_query:
        paper_details = paper_details.filter(
            paper__paper_name__icontains=search_query
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
        'title': f'Paper Detail {paper_detail.paper_detail_id}',
        'list_url': 'core:paper_detail_list',
    }
    return render(request, 'core/paper_detail_detail.html', context)

# =============================================================================
# APPLICATION SECTION
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
    
    context = {
        'object': application,
        'title': f'Application: {application.application_name or f"Application {application.application_id}"}',
        'list_url': 'core:application_list',
    }
    return render(request, 'core/application_detail.html', context)

# =============================================================================
# APPLICATION QUESTION SECTION
# =============================================================================

def application_question_list(request):
    """List all application questions"""
    search_query = request.GET.get('search', '')
    
    questions = ApplicationQuestion.objects.select_related('application', 'parameter').all()
    
    if search_query:
        questions = questions.filter(
            custom_question__icontains=search_query
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
        'title': f'Application Question {question.application_question_id}',
        'list_url': 'core:application_question_list',
    }
    return render(request, 'core/application_question_detail.html', context)

# =============================================================================
# PARAMETER SECTION
# =============================================================================

def parameter_list(request):
    """List all parameters"""
    search_query = request.GET.get('search', '')
    
    parameters = Parameter.objects.all()
    
    if search_query:
        parameters = parameters.filter(
            parameter_name__icontains=search_query
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
    
    context = {
        'object': parameter,
        'title': f'Parameter: {parameter.parameter_name or f"Parameter {parameter.parameter_id}"}',
        'list_url': 'core:parameter_list',
    }
    return render(request, 'core/parameter_detail.html', context)

# =============================================================================
# PARAMETER MAP SECTION  
# =============================================================================

def parameter_map_list(request):
    """List all parameter maps"""
    search_query = request.GET.get('search', '')
    
    parameter_maps = ParameterMap.objects.select_related('products', 'parameter').all()
    
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
        'title': f'Parameter Map {parameter_map.parameter_map_id}',
        'list_url': 'core:parameter_map_list',
    }
    return render(request, 'core/parameter_map_detail.html', context)

# =============================================================================
# DOCUMENT SECTION
# =============================================================================

def document_list(request):
    """List all documents"""
    search_query = request.GET.get('search', '')
    
    documents = Document.objects.select_related('product').all()
    
    if search_query:
        documents = documents.filter(
            document_name__icontains=search_query
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
# TASK SECTION
# =============================================================================

def task_list(request):
    """List all tasks"""
    search_query = request.GET.get('search', '')
    
    tasks = Task.objects.all()
    
    if search_query:
        tasks = tasks.filter(
            task_name__icontains=search_query
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
    
    context = {
        'object': workflow,
        'title': f'Workflow: {workflow.workflow_name or f"Workflow {workflow.workflow_id}"}',
        'list_url': 'core:workflow_list',
    }
    return render(request, 'core/workflow_detail.html', context)

# =============================================================================
# WORKFLOW DETAIL SECTION  
# =============================================================================

def workflow_detail_list(request):
    """List all workflow details"""
    workflow_details = WorkflowDetail.objects.select_related('workflow', 'task').all()
    
    paginator = Paginator(workflow_details, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'title': 'Workflow Details',
        'total_count': workflow_details.count(),
    }
    return render(request, 'core/workflow_detail_list.html', context)

def workflow_detail_detail(request, pk):
    """View individual workflow detail"""
    workflow_detail = get_object_or_404(WorkflowDetail, pk=pk)
    
    context = {
        'object': workflow_detail,
        'title': f'Workflow Detail {workflow_detail.workflow_detail_id}',
        'list_url': 'core:workflow_detail_list',
    }
    return render(request, 'core/workflow_detail_detail.html', context)

# =============================================================================
# WORKSTATION VIEWS
# =============================================================================

def workstation_view(request):
    """Workstation main page"""
    return render(request, 'core/workstation.html')

# =============================================================================
# COMPANY MANAGEMENT VIEWS
# =============================================================================

def company_list(request):
    """List all companies"""
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
    """View individual company"""
    company = get_object_or_404(Company, pk=pk)
    
    context = {
        'object': company,
        'title': f'Company: {company.company_name or f"Company {company.company_id}"}',
        'list_url': 'core:company_list',
    }
    return render(request, 'core/company_detail.html', context)

def options_list(request):
    """List all options"""
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

# Add placeholder functions for other missing views referenced in URLs
# You can implement these later as needed

def company_location_list(request):
    return render(request, 'core/company_location_list.html', {'page_obj': [], 'title': 'Company Locations'})

def company_location_detail(request, pk):
    return render(request, 'core/company_location_detail.html', {'object': None, 'title': 'Company Location'})

def company_contact_list(request):
    return render(request, 'core/company_contact_list.html', {'page_obj': [], 'title': 'Company Contacts'})

def company_contact_detail(request, pk):
    return render(request, 'core/company_contact_detail.html', {'object': None, 'title': 'Company Contact'})

def company_alias_list(request):
    return render(request, 'core/company_alias_list.html', {'page_obj': [], 'title': 'Company Aliases'})

def company_alias_detail(request, pk):
    return render(request, 'core/company_alias_detail.html', {'object': None, 'title': 'Company Alias'})

def application_response_list(request):
    return render(request, 'core/application_response_list.html', {'page_obj': [], 'title': 'Application Responses'})

def application_response_detail(request, pk):
    return render(request, 'core/application_response_detail.html', {'object': None, 'title': 'Application Response'})

def order_option_list(request):
    return render(request, 'core/order_option_list.html', {'page_obj': [], 'title': 'Order Options'})

def order_option_detail(request, pk):
    return render(request, 'core/order_option_detail.html', {'object': None, 'title': 'Order Option'})

def order_data_vert_list(request):
    return render(request, 'core/order_data_vert_list.html', {'page_obj': [], 'title': 'Order Data Verts'})

def order_data_vert_detail(request, pk):
    return render(request, 'core/order_data_vert_detail.html', {'object': None, 'title': 'Order Data Vert'})

def document_detail_list(request):
    return render(request, 'core/document_detail_list.html', {'page_obj': [], 'title': 'Document Details'})

def document_detail_detail(request, pk):
    return render(request, 'core/document_detail_detail.html', {'object': None, 'title': 'Document Detail'})

# Placeholder for missing sections
def attachment_list(request):
    return render(request, 'core/attachment_list.html', {'page_obj': [], 'title': 'Attachments'})

def attachment_detail(request, pk):
    return render(request, 'core/attachment_detail.html', {'object': None, 'title': 'Attachment'})

def attachment_detail_list(request):
    return render(request, 'core/attachment_detail_list.html', {'page_obj': [], 'title': 'Attachment Details'})

def attachment_detail_detail(request, pk):
    return render(request, 'core/attachment_detail_detail.html', {'object': None, 'title': 'Attachment Detail'})

def limits_list(request):
    return render(request, 'core/limits_list.html', {'page_obj': [], 'title': 'Limits'})

def limits_detail(request, pk):
    return render(request, 'core/limits_detail.html', {'object': None, 'title': 'Limit'})

def retention_list(request):
    return render(request, 'core/retention_list.html', {'page_obj': [], 'title': 'Retentions'})

def retention_detail(request, pk):
    return render(request, 'core/retention_detail.html', {'object': None, 'title': 'Retention'})

def sublimit_list(request):
    return render(request, 'core/sublimit_list.html', {'page_obj': [], 'title': 'Sublimits'})

def sublimit_detail(request, pk):
    return render(request, 'core/sublimit_detail.html', {'object': None, 'title': 'Sublimit'})

# =============================================================================
# AJAX MODAL VIEWS - NEW CATALOG SECTIONS
# =============================================================================

@csrf_exempt
@api_view(['GET', 'POST'])
def venture_modal_edit(request, pk):
    """AJAX view for editing Venture in modal"""
    try:
        venture = get_object_or_404(Venture, pk=pk)
    except Venture.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Venture not found'
        })

    if request.method == 'GET':
        form = VentureForm(instance=venture)
        
        modal_html = render_to_string('core/modals/venture_modal.html', {
            'form': form,
            'object': venture
        }, request=request)
        
        return JsonResponse({
            'success': True,
            'html': modal_html
        })
    
    elif request.method == 'POST':
        form = VentureForm(request.POST, instance=venture)
        
        if form.is_valid():
            updated_venture = form.save()
            
            row_html = render_to_string('core/partials/venture_row.html', {
                'venture': updated_venture
            }, request=request)
            
            return JsonResponse({
                'success': True,
                'message': f'Venture "{updated_venture.venture_name}" updated successfully!',
                'object_id': updated_venture.venture_id,
                'row_html': row_html
            })
        else:
            modal_html = render_to_string('core/modals/venture_modal.html', {
                'form': form,
                'object': venture
            }, request=request)
            
            return JsonResponse({
                'success': False,
                'html': modal_html,
                'errors': form.errors
            })

@csrf_exempt
@api_view(['GET', 'POST'])  
def venture_modal_add(request):
    """AJAX view for adding new Venture in modal"""
    
    if request.method == 'GET':
        form = VentureForm()
        
        modal_html = render_to_string('core/modals/venture_modal.html', {
            'form': form,
            'object': None
        }, request=request)
        
        return JsonResponse({
            'success': True,
            'html': modal_html
        })
    
    elif request.method == 'POST':
        form = VentureForm(request.POST)
        
        if form.is_valid():
            new_venture = form.save()
            
            row_html = render_to_string('core/partials/venture_row.html', {
                'venture': new_venture
            }, request=request)
            
            return JsonResponse({
                'success': True,
                'message': f'Venture "{new_venture.venture_name}" added successfully!',
                'object_id': new_venture.venture_id,
                'row_html': row_html,
                'action': 'add'
            })
        else:
            modal_html = render_to_string('core/modals/venture_modal.html', {
                'form': form,
                'object': None
            }, request=request)
            
            return JsonResponse({
                'success': False,
                'html': modal_html,
                'errors': form.errors
            })

@csrf_exempt
@api_view(['GET', 'POST'])
def coverage_modal_edit(request, pk):
    """AJAX view for editing Coverage in modal"""
    try:
        coverage = get_object_or_404(Coverage, pk=pk)
    except Coverage.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Coverage not found'
        })

    if request.method == 'GET':
        form = CoverageForm(instance=coverage)
        
        modal_html = render_to_string('core/modals/coverage_modal.html', {
            'form': form,
            'object': coverage
        }, request=request)
        
        return JsonResponse({
            'success': True,
            'html': modal_html
        })
    
    elif request.method == 'POST':
        form = CoverageForm(request.POST, instance=coverage)
        
        if form.is_valid():
            updated_coverage = form.save()
            
            row_html = render_to_string('core/partials/coverage_row.html', {
                'coverage': updated_coverage
            }, request=request)
            
            return JsonResponse({
                'success': True,
                'message': f'Coverage "{updated_coverage.coverage_name}" updated successfully!',
                'object_id': updated_coverage.coverage_id,
                'row_html': row_html
            })
        else:
            modal_html = render_to_string('core/modals/coverage_modal.html', {
                'form': form,
                'object': coverage
            }, request=request)
            
            return JsonResponse({
                'success': False,
                'html': modal_html,
                'errors': form.errors
            })

@csrf_exempt
@api_view(['GET', 'POST'])  
def coverage_modal_add(request):
    """AJAX view for adding new Coverage in modal"""
    
    if request.method == 'GET':
        form = CoverageForm()
        
        modal_html = render_to_string('core/modals/coverage_modal.html', {
            'form': form,
            'object': None
        }, request=request)
        
        return JsonResponse({
            'success': True,
            'html': modal_html
        })
    
    elif request.method == 'POST':
        form = CoverageForm(request.POST)
        
        if form.is_valid():
            new_coverage = form.save()
            
            row_html = render_to_string('core/partials/coverage_row.html', {
                'coverage': new_coverage
            }, request=request)
            
            return JsonResponse({
                'success': True,
                'message': f'Coverage "{new_coverage.coverage_name}" added successfully!',
                'object_id': new_coverage.coverage_id,
                'row_html': row_html,
                'action': 'add'
            })
        else:
            modal_html = render_to_string('core/modals/coverage_modal.html', {
                'form': form,
                'object': None
            }, request=request)
            
            return JsonResponse({
                'success': False,
                'html': modal_html,
                'errors': form.errors
            })

@csrf_exempt
@api_view(['GET', 'POST'])
def drive_modal_edit(request, pk):
    """AJAX view for editing Drive in modal"""
    try:
        drive = get_object_or_404(Drive, pk=pk)
    except Drive.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Drive not found'
        })

    if request.method == 'GET':
        form = DriveForm(instance=drive)
        
        modal_html = render_to_string('core/modals/drive_modal.html', {
            'form': form,
            'object': drive
        }, request=request)
        
        return JsonResponse({
            'success': True,
            'html': modal_html
        })
    
    elif request.method == 'POST':
        form = DriveForm(request.POST, instance=drive)
        
        if form.is_valid():
            updated_drive = form.save()
            
            row_html = render_to_string('core/partials/drive_row.html', {
                'drive': updated_drive
            }, request=request)
            
            return JsonResponse({
                'success': True,
                'message': f'Drive "{updated_drive.drive_name}" updated successfully!',
                'object_id': updated_drive.drive_id,
                'row_html': row_html
            })
        else:
            modal_html = render_to_string('core/modals/drive_modal.html', {
                'form': form,
                'object': drive
            }, request=request)
            
            return JsonResponse({
                'success': False,
                'html': modal_html,
                'errors': form.errors
            })

@csrf_exempt
@api_view(['GET', 'POST'])  
def drive_modal_add(request):
    """AJAX view for adding new Drive in modal"""
    
    if request.method == 'GET':
        form = DriveForm()
        
        modal_html = render_to_string('core/modals/drive_modal.html', {
            'form': form,
            'object': None
        }, request=request)
        
        return JsonResponse({
            'success': True,
            'html': modal_html
        })
    
    elif request.method == 'POST':
        form = DriveForm(request.POST)
        
        if form.is_valid():
            new_drive = form.save()
            
            row_html = render_to_string('core/partials/drive_row.html', {
                'drive': new_drive
            }, request=request)
            
            return JsonResponse({
                'success': True,
                'message': f'Drive "{new_drive.drive_name}" added successfully!',
                'object_id': new_drive.drive_id,
                'row_html': row_html,
                'action': 'add'
            })
        else:
            modal_html = render_to_string('core/modals/drive_modal.html', {
                'form': form,
                'object': None
            }, request=request)
            
            return JsonResponse({
                'success': False,
                'html': modal_html,
                'errors': form.errors
            })

@csrf_exempt
@api_view(['GET', 'POST'])
def employee_location_modal_edit(request, pk):
    """AJAX view for editing EmployeeLocation in modal"""
    try:
        location = get_object_or_404(EmployeeLocation, pk=pk)
    except EmployeeLocation.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Employee location not found'
        })

    if request.method == 'GET':
        form = EmployeeLocationForm(instance=location)
        
        modal_html = render_to_string('core/modals/employee_location_modal.html', {
            'form': form,
            'object': location
        }, request=request)
        
        return JsonResponse({
            'success': True,
            'html': modal_html
        })
    
    elif request.method == 'POST':
        form = EmployeeLocationForm(request.POST, instance=location)
        
        if form.is_valid():
            updated_location = form.save()
            
            row_html = render_to_string('core/partials/employee_location_row.html', {
                'location': updated_location
            }, request=request)
            
            return JsonResponse({
                'success': True,
                'message': f'Location "{updated_location.employee_location_name}" updated successfully!',
                'object_id': updated_location.employee_location_id,
                'row_html': row_html
            })
        else:
            modal_html = render_to_string('core/modals/employee_location_modal.html', {
                'form': form,
                'object': location
            }, request=request)
            
            return JsonResponse({
                'success': False,
                'html': modal_html,
                'errors': form.errors
            })

@csrf_exempt
@api_view(['GET', 'POST'])  
def employee_location_modal_add(request):
    """AJAX view for adding new EmployeeLocation in modal"""
    
    if request.method == 'GET':
        form = EmployeeLocationForm()
        
        modal_html = render_to_string('core/modals/employee_location_modal.html', {
            'form': form,
            'object': None
        }, request=request)
        
        return JsonResponse({
            'success': True,
            'html': modal_html
        })
    
    elif request.method == 'POST':
        form = EmployeeLocationForm(request.POST)
        
        if form.is_valid():
            new_location = form.save()
            
            row_html = render_to_string('core/partials/employee_location_row.html', {
                'location': new_location
            }, request=request)
            
            return JsonResponse({
                'success': True,
                'message': f'Location "{new_location.employee_location_name}" added successfully!',
                'object_id': new_location.employee_location_id,
                'row_html': row_html,
                'action': 'add'
            })
        else:
            modal_html = render_to_string('core/modals/employee_location_modal.html', {
                'form': form,
                'object': None
            }, request=request)
            
            return JsonResponse({
                'success': False,
                'html': modal_html,
                'errors': form.errors
            })

# =============================================================================
# EXISTING AJAX MODAL VIEWS (Referenced in URLs)
# =============================================================================

@csrf_exempt
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
        form = CompanyContactForm(request.POST, instance=contact)
        
        if form.is_valid():
            updated_contact = form.save()
            
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
            modal_html = render_to_string('core/modals/company_contact_modal.html', {
                'form': form,
                'object': contact
            }, request=request)
            
            return JsonResponse({
                'success': False,
                'html': modal_html,
                'errors': form.errors
            })

@csrf_exempt
@api_view(['GET', 'POST'])  
def company_contact_modal_add(request):
    """AJAX view for adding new CompanyContact in modal"""
    
    if request.method == 'GET':
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
        form = CompanyContactForm(request.POST)
        
        if form.is_valid():
            new_contact = form.save()
            
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
            modal_html = render_to_string('core/modals/company_contact_modal.html', {
                'form': form,
                'object': None
            }, request=request)
            
            return JsonResponse({
                'success': False,
                'html': modal_html,
                'errors': form.errors
            })

@csrf_exempt
@api_view(['GET', 'POST'])
def products_modal_edit(request, pk):
    """AJAX view for editing Products in modal"""
    try:
        product = get_object_or_404(Products, pk=pk)
    except Products.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Product not found'
        })

    if request.method == 'GET':
        form = ProductsForm(instance=product)
        
        modal_html = render_to_string('core/modals/products_modal.html', {
            'form': form,
            'object': product
        }, request=request)
        
        return JsonResponse({
            'success': True,
            'html': modal_html
        })
    
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
                'form': form,
                'object': product
            }, request=request)
            
            return JsonResponse({
                'success': False,
                'html': modal_html,
                'errors': form.errors
            })

@csrf_exempt
@api_view(['GET', 'POST'])  
def products_modal_add(request):
    """AJAX view for adding new Products in modal"""
    
    if request.method == 'GET':
        form = ProductsForm()
        
        modal_html = render_to_string('core/modals/products_modal.html', {
            'form': form,
            'object': None
        }, request=request)
        
        return JsonResponse({
            'success': True,
            'html': modal_html
        })
    
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
                'form': form,
                'object': None
            }, request=request)
            
            return JsonResponse({
                'success': False,
                'html': modal_html,
                'errors': form.errors
            })

@csrf_exempt
@api_view(['GET', 'POST'])
def employee_function_modal_edit(request, pk):
    """AJAX view for editing EmployeeFunction in modal"""
    try:
        function = get_object_or_404(EmployeeFunction, pk=pk)
    except EmployeeFunction.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Employee function not found'
        })

    if request.method == 'GET':
        form = EmployeeFunctionForm(instance=function)
        
        modal_html = render_to_string('core/modals/employee_function_modal.html', {
            'form': form,
            'object': function
        }, request=request)
        
        return JsonResponse({
            'success': True,
            'html': modal_html
        })
    
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
                'form': form,
                'object': function
            }, request=request)
            
            return JsonResponse({
                'success': False,
                'html': modal_html,
                'errors': form.errors
            })

@csrf_exempt
@api_view(['GET', 'POST'])  
def employee_function_modal_add(request):
    """AJAX view for adding new EmployeeFunction in modal"""
    
    if request.method == 'GET':
        form = EmployeeFunctionForm()
        
        modal_html = render_to_string('core/modals/employee_function_modal.html', {
            'form': form,
            'object': None
        }, request=request)
        
        return JsonResponse({
            'success': True,
            'html': modal_html
        })
    
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
                'form': form,
                'object': None
            }, request=request)
            
            return JsonResponse({
                'success': False,
                'html': modal_html,
                'errors': form.errors
            })

# Add other existing modal views referenced in URLs...
# (company_modal_edit, options_modal_edit, etc. - following the same pattern)

# API Views for AJAX operations
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

@csrf_exempt
@api_view(['GET', 'POST'])
def company_modal_edit(request, pk):
    """AJAX view for editing Company in modal"""
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
@api_view(['GET', 'POST'])  
def company_modal_add(request):
    """AJAX view for adding new Company in modal"""
    
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

@csrf_exempt
@api_view(['GET', 'POST'])
def options_modal_edit(request, pk):
    """AJAX view for editing Options in modal"""
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
@api_view(['GET', 'POST'])  
def options_modal_add(request):
    """AJAX view for adding new Options in modal"""
    
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

@csrf_exempt
@api_view(['GET', 'POST'])
def company_location_modal_edit(request, pk):
    """AJAX view for editing CompanyLocation in modal"""
    try:
        location = get_object_or_404(CompanyLocation, pk=pk)
    except CompanyLocation.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Company location not found'
        })

    if request.method == 'GET':
        form = CompanyLocationForm(instance=location)
        
        modal_html = render_to_string('core/modals/company_location_modal.html', {
            'form': form,
            'object': location
        }, request=request)
        
        return JsonResponse({
            'success': True,
            'html': modal_html
        })
    
    elif request.method == 'POST':
        form = CompanyLocationForm(request.POST, instance=location)
        
        if form.is_valid():
            updated_location = form.save()
            
            row_html = render_to_string('core/partials/company_location_row.html', {
                'location': updated_location
            }, request=request)
            
            return JsonResponse({
                'success': True,
                'message': 'Company location updated successfully!',
                'object_id': updated_location.company_location_id,
                'row_html': row_html
            })
        else:
            modal_html = render_to_string('core/modals/company_location_modal.html', {
                'form': form,
                'object': location
            }, request=request)
            
            return JsonResponse({
                'success': False,
                'html': modal_html,
                'errors': form.errors
            })

@csrf_exempt
@api_view(['GET', 'POST'])  
def company_location_modal_add(request):
    """AJAX view for adding new CompanyLocation in modal"""
    
    if request.method == 'GET':
        form = CompanyLocationForm()
        
        modal_html = render_to_string('core/modals/company_location_modal.html', {
            'form': form,
            'object': None
        }, request=request)
        
        return JsonResponse({
            'success': True,
            'html': modal_html
        })
    
    elif request.method == 'POST':
        form = CompanyLocationForm(request.POST)
        
        if form.is_valid():
            new_location = form.save()
            
            row_html = render_to_string('core/partials/company_location_row.html', {
                'location': new_location
            }, request=request)
            
            return JsonResponse({
                'success': True,
                'message': 'Company location added successfully!',
                'object_id': new_location.company_location_id,
                'row_html': row_html,
                'action': 'add'
            })
        else:
            modal_html = render_to_string('core/modals/company_location_modal.html', {
                'form': form,
                'object': None
            }, request=request)
            
            return JsonResponse({
                'success': False,
                'html': modal_html,
                'errors': form.errors
            })

@csrf_exempt
@api_view(['GET', 'POST'])
def company_alias_modal_edit(request, pk):
    """AJAX view for editing CompanyAlias in modal"""
    try:
        alias = get_object_or_404(CompanyAlias, pk=pk)
    except CompanyAlias.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Company alias not found'
        })

    if request.method == 'GET':
        form = CompanyAliasForm(instance=alias)
        
        modal_html = render_to_string('core/modals/company_alias_modal.html', {
            'form': form,
            'object': alias
        }, request=request)
        
        return JsonResponse({
            'success': True,
            'html': modal_html
        })
    
    elif request.method == 'POST':
        form = CompanyAliasForm(request.POST, instance=alias)
        
        if form.is_valid():
            updated_alias = form.save()
            
            row_html = render_to_string('core/partials/company_alias_row.html', {
                'alias': updated_alias
            }, request=request)
            
            return JsonResponse({
                'success': True,
                'message': f'Company alias "{updated_alias.company_alias_name}" updated successfully!',
                'object_id': updated_alias.company_alias_id,
                'row_html': row_html
            })
        else:
            modal_html = render_to_string('core/modals/company_alias_modal.html', {
                'form': form,
                'object': alias
            }, request=request)
            
            return JsonResponse({
                'success': False,
                'html': modal_html,
                'errors': form.errors
            })

@csrf_exempt
@api_view(['GET', 'POST'])  
def company_alias_modal_add(request):
    """AJAX view for adding new CompanyAlias in modal"""
    
    if request.method == 'GET':
        form = CompanyAliasForm()
        
        modal_html = render_to_string('core/modals/company_alias_modal.html', {
            'form': form,
            'object': None
        }, request=request)
        
        return JsonResponse({
            'success': True,
            'html': modal_html
        })
    
    elif request.method == 'POST':
        form = CompanyAliasForm(request.POST)
        
        if form.is_valid():
            new_alias = form.save()
            
            row_html = render_to_string('core/partials/company_alias_row.html', {
                'alias': new_alias
            }, request=request)
            
            return JsonResponse({
                'success': True,
                'message': f'Company alias "{new_alias.company_alias_name}" added successfully!',
                'object_id': new_alias.company_alias_id,
                'row_html': row_html,
                'action': 'add'
            })
        else:
            modal_html = render_to_string('core/modals/company_alias_modal.html', {
                'form': form,
                'object': None
            }, request=request)
            
            return JsonResponse({
                'success': False,
                'html': modal_html,
                'errors': form.errors
            })

@csrf_exempt
@api_view(['GET', 'POST'])
def application_response_modal_edit(request, pk):
    """AJAX view for editing ApplicationResponse in modal"""
    try:
        response = get_object_or_404(ApplicationResponse, pk=pk)
    except ApplicationResponse.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Application response not found'
        })

    if request.method == 'GET':
        form = ApplicationResponseForm(instance=response)
        
        modal_html = render_to_string('core/modals/application_response_modal.html', {
            'form': form,
            'object': response
        }, request=request)
        
        return JsonResponse({
            'success': True,
            'html': modal_html
        })
    
    elif request.method == 'POST':
        form = ApplicationResponseForm(request.POST, instance=response)
        
        if form.is_valid():
            updated_response = form.save()
            
            row_html = render_to_string('core/partials/application_response_row.html', {
                'response': updated_response
            }, request=request)
            
            return JsonResponse({
                'success': True,
                'message': 'Application response updated successfully!',
                'object_id': updated_response.application_response_id,
                'row_html': row_html
            })
        else:
            modal_html = render_to_string('core/modals/application_response_modal.html', {
                'form': form,
                'object': response
            }, request=request)
            
            return JsonResponse({
                'success': False,
                'html': modal_html,
                'errors': form.errors
            })

@csrf_exempt
@api_view(['GET', 'POST'])  
def application_response_modal_add(request):
    """AJAX view for adding new ApplicationResponse in modal"""
    
    if request.method == 'GET':
        form = ApplicationResponseForm()
        
        modal_html = render_to_string('core/modals/application_response_modal.html', {
            'form': form,
            'object': None
        }, request=request)
        
        return JsonResponse({
            'success': True,
            'html': modal_html
        })
    
    elif request.method == 'POST':
        form = ApplicationResponseForm(request.POST)
        
        if form.is_valid():
            new_response = form.save()
            
            row_html = render_to_string('core/partials/application_response_row.html', {
                'response': new_response
            }, request=request)
            
            return JsonResponse({
                'success': True,
                'message': 'Application response added successfully!',
                'object_id': new_response.application_response_id,
                'row_html': row_html,
                'action': 'add'
            })
        else:
            modal_html = render_to_string('core/modals/application_response_modal.html', {
                'form': form,
                'object': None
            }, request=request)
            
            return JsonResponse({
                'success': False,
                'html': modal_html,
                'errors': form.errors
            })

@csrf_exempt
@api_view(['GET', 'POST'])
def order_option_modal_edit(request, pk):
    """AJAX view for editing OrderOption in modal"""
    try:
        order_option = get_object_or_404(OrderOption, pk=pk)
    except OrderOption.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Order option not found'
        })

    if request.method == 'GET':
        form = OrderOptionForm(instance=order_option)
        
        modal_html = render_to_string('core/modals/order_option_modal.html', {
            'form': form,
            'object': order_option
        }, request=request)
        
        return JsonResponse({
            'success': True,
            'html': modal_html
        })
    
    elif request.method == 'POST':
        form = OrderOptionForm(request.POST, instance=order_option)
        
        if form.is_valid():
            updated_order_option = form.save()
            
            row_html = render_to_string('core/partials/order_option_row.html', {
                'order_option': updated_order_option
            }, request=request)
            
            return JsonResponse({
                'success': True,
                'message': 'Order option updated successfully!',
                'object_id': updated_order_option.order_option_id,
                'row_html': row_html
            })
        else:
            modal_html = render_to_string('core/modals/order_option_modal.html', {
                'form': form,
                'object': order_option
            }, request=request)
            
            return JsonResponse({
                'success': False,
                'html': modal_html,
                'errors': form.errors
            })

@csrf_exempt
@api_view(['GET', 'POST'])  
def order_option_modal_add(request):
    """AJAX view for adding new OrderOption in modal"""
    
    if request.method == 'GET':
        form = OrderOptionForm()
        
        modal_html = render_to_string('core/modals/order_option_modal.html', {
            'form': form,
            'object': None
        }, request=request)
        
        return JsonResponse({
            'success': True,
            'html': modal_html
        })
    
    elif request.method == 'POST':
        form = OrderOptionForm(request.POST)
        
        if form.is_valid():
            new_order_option = form.save()
            
            row_html = render_to_string('core/partials/order_option_row.html', {
                'order_option': new_order_option
            }, request=request)
            
            return JsonResponse({
                'success': True,
                'message': 'Order option added successfully!',
                'object_id': new_order_option.order_option_id,
                'row_html': row_html,
                'action': 'add'
            })
        else:
            modal_html = render_to_string('core/modals/order_option_modal.html', {
                'form': form,
                'object': None
            }, request=request)
            
            return JsonResponse({
                'success': False,
                'html': modal_html,
                'errors': form.errors
            })

@csrf_exempt
@api_view(['GET', 'POST'])
def order_data_vert_modal_edit(request, pk):
    """AJAX view for editing OrderDataVert in modal"""
    try:
        order_data_vert = get_object_or_404(OrderDataVert, pk=pk)
    except OrderDataVert.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Order data vert not found'
        })

    if request.method == 'GET':
        form = OrderDataVertForm(instance=order_data_vert)
        
        modal_html = render_to_string('core/modals/order_data_vert_modal.html', {
            'form': form,
            'object': order_data_vert
        }, request=request)
        
        return JsonResponse({
            'success': True,
            'html': modal_html
        })
    
    elif request.method == 'POST':
        form = OrderDataVertForm(request.POST, instance=order_data_vert)
        
        if form.is_valid():
            updated_order_data_vert = form.save()
            
            row_html = render_to_string('core/partials/order_data_vert_row.html', {
                'order_data_vert': updated_order_data_vert
            }, request=request)
            
            return JsonResponse({
                'success': True,
                'message': 'Order data vert updated successfully!',
                'object_id': updated_order_data_vert.order_date_vert_id,
                'row_html': row_html
            })
        else:
            modal_html = render_to_string('core/modals/order_data_vert_modal.html', {
                'form': form,
                'object': order_data_vert
            }, request=request)
            
            return JsonResponse({
                'success': False,
                'html': modal_html,
                'errors': form.errors
            })

@csrf_exempt
@api_view(['GET', 'POST'])  
def order_data_vert_modal_add(request):
    """AJAX view for adding new OrderDataVert in modal"""
    
    if request.method == 'GET':
        form = OrderDataVertForm()
        
        modal_html = render_to_string('core/modals/order_data_vert_modal.html', {
            'form': form,
            'object': None
        }, request=request)
        
        return JsonResponse({
            'success': True,
            'html': modal_html
        })
    
    elif request.method == 'POST':
        form = OrderDataVertForm(request.POST)
        
        if form.is_valid():
            new_order_data_vert = form.save()
            
            row_html = render_to_string('core/partials/order_data_vert_row.html', {
                'order_data_vert': new_order_data_vert
            }, request=request)
            
            return JsonResponse({
                'success': True,
                'message': 'Order data vert added successfully!',
                'object_id': new_order_data_vert.order_date_vert_id,
                'row_html': row_html,
                'action': 'add'
            })
        else:
            modal_html = render_to_string('core/modals/order_data_vert_modal.html', {
                'form': form,
                'object': None
            }, request=request)
            
            return JsonResponse({
                'success': False,
                'html': modal_html,
                'errors': form.errors
            })

@csrf_exempt
@api_view(['GET', 'POST'])
def document_detail_modal_edit(request, pk):
    """AJAX view for editing DocumentDetail in modal"""
    try:
        document_detail = get_object_or_404(DocumentDetail, pk=pk)
    except DocumentDetail.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Document detail not found'
        })

    if request.method == 'GET':
        form = DocumentDetailForm(instance=document_detail)
        
        modal_html = render_to_string('core/modals/document_detail_modal.html', {
            'form': form,
            'object': document_detail
        }, request=request)
        
        return JsonResponse({
            'success': True,
            'html': modal_html
        })
    
    elif request.method == 'POST':
        form = DocumentDetailForm(request.POST, instance=document_detail)
        
        if form.is_valid():
            updated_document_detail = form.save()
            
            row_html = render_to_string('core/partials/document_detail_row.html', {
                'document_detail': updated_document_detail
            }, request=request)
            
            return JsonResponse({
                'success': True,
                'message': 'Document detail updated successfully!',
                'object_id': updated_document_detail.document_detail_id,
                'row_html': row_html
            })
        else:
            modal_html = render_to_string('core/modals/document_detail_modal.html', {
                'form': form,
                'object': document_detail
            }, request=request)
            
            return JsonResponse({
                'success': False,
                'html': modal_html,
                'errors': form.errors
            })

@csrf_exempt
@api_view(['GET', 'POST'])  
def document_detail_modal_add(request):
    """AJAX view for adding new DocumentDetail in modal"""
    
    if request.method == 'GET':
        form = DocumentDetailForm()
        
        modal_html = render_to_string('core/modals/document_detail_modal.html', {
            'form': form,
            'object': None
        }, request=request)
        
        return JsonResponse({
            'success': True,
            'html': modal_html
        })
    
    elif request.method == 'POST':
        form = DocumentDetailForm(request.POST)
        
        if form.is_valid():
            new_document_detail = form.save()
            
            row_html = render_to_string('core/partials/document_detail_row.html', {
                'document_detail': new_document_detail
            }, request=request)
            
            return JsonResponse({
                'success': True,
                'message': 'Document detail added successfully!',
                'object_id': new_document_detail.document_detail_id,
                'row_html': row_html,
                'action': 'add'
            })
        else:
            modal_html = render_to_string('core/modals/document_detail_modal.html', {
                'form': form,
                'object': None
            }, request=request)
            
            return JsonResponse({
                'success': False,
                'html': modal_html,
                'errors': form.errors
            })