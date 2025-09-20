# Skye/views.py

import json
import logging
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.conf import settings
from django.apps import apps
from django.core.exceptions import ObjectDoesNotExist

from .config_parser import SkyeConfigParser
from .services import ForeignKeyResolver, ProgressiveDataLoader

from .utilities.field_generator import FieldGenerator

from .models import (
    Venture, Coverage, Products, Company, CompanyContact, CompanyLocation,
    EmployeeLocation, EmployeeContact, Orders, Applications, Parameter,
    ApplicationQuestion, ApplicationResponse, Cover, Options, Limits,
    Retention, OrderOption, Document, Broker, BrokerLocation, BrokerContact,
    Stage, FlowOrigin, Workflow, Task, WorkflowDetail, ParameterType,
    GenerationJob, GenerationLog, ModelParameter, TrainingJob,
    GenerationModel, DataSeed, TrainingModel, InputOutput
)
from .forms import (
    CompanyForm, CompanyContactForm, ProductsForm, OrdersForm,
    ApplicationsForm, EmployeeContactForm, VentureForm
)

# Setup logging
logger = logging.getLogger(__name__)

# Dashboard View
@login_required
def dashboard(request):
    """Dashboard now redirects to Catalog main page"""
    return redirect('main_page', 'Catalog')


# Company CRUD Views
@method_decorator(login_required, name='dispatch')
class CompanyListView(ListView):
    model = Company
    template_name = 'companies/list.html'
    context_object_name = 'companies'
    paginate_by = 25

    def get_queryset(self):
        queryset = Company.objects.all()
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(company_name__icontains=search)
            )
        return queryset.order_by('company_name')


@method_decorator(login_required, name='dispatch')
class CompanyDetailView(DetailView):
    model = Company
    template_name = 'companies/detail.html'
    context_object_name = 'company'
    pk_url_kwarg = 'company_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['contacts'] = CompanyContact.objects.filter(company=self.object)
        context['locations'] = CompanyLocation.objects.filter(company=self.object)
        context['orders'] = Orders.objects.filter(company=self.object).order_by('-orders_id')[:10]
        return context


@method_decorator(login_required, name='dispatch')
class CompanyCreateView(CreateView):
    model = Company
    form_class = CompanyForm
    template_name = 'companies/form.html'
    
    def get_success_url(self):
        return reverse_lazy('company_detail', kwargs={'company_id': self.object.company_id})


@method_decorator(login_required, name='dispatch')
class CompanyUpdateView(UpdateView):
    model = Company
    form_class = CompanyForm
    template_name = 'companies/form.html'
    pk_url_kwarg = 'company_id'
    
    def get_success_url(self):
        return reverse_lazy('company_detail', kwargs={'company_id': self.object.company_id})


@method_decorator(login_required, name='dispatch')
class CompanyDeleteView(DeleteView):
    model = Company
    template_name = 'companies/confirm_delete.html'
    pk_url_kwarg = 'company_id'
    success_url = reverse_lazy('company_list')


# Products CRUD Views
@method_decorator(login_required, name='dispatch')
class ProductsListView(ListView):
    model = Products
    template_name = 'products/list.html'
    context_object_name = 'products'
    paginate_by = 25

    def get_queryset(self):
        queryset = Products.objects.select_related('venture', 'coverage')
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(product_name__icontains=search) |
                Q(product_code__icontains=search)
            )
        return queryset.order_by('product_name')


@method_decorator(login_required, name='dispatch')
class ProductsDetailView(DetailView):
    model = Products
    template_name = 'products/detail.html'
    context_object_name = 'product'
    pk_url_kwarg = 'products_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['covers'] = Cover.objects.filter(product=self.object)
        context['applications'] = Applications.objects.filter(product=self.object)
        context['documents'] = Document.objects.filter(product=self.object)
        return context


@method_decorator(login_required, name='dispatch')
class ProductsCreateView(CreateView):
    model = Products
    form_class = ProductsForm
    template_name = 'products/form.html'
    
    def get_success_url(self):
        return reverse_lazy('products_detail', kwargs={'products_id': self.object.products_id})


@method_decorator(login_required, name='dispatch')
class ProductsUpdateView(UpdateView):
    model = Products
    form_class = ProductsForm
    template_name = 'products/form.html'
    pk_url_kwarg = 'products_id'
    
    def get_success_url(self):
        return reverse_lazy('products_detail', kwargs={'products_id': self.object.products_id})


@method_decorator(login_required, name='dispatch')
class ProductsDeleteView(DeleteView):
    model = Products
    template_name = 'products/confirm_delete.html'
    pk_url_kwarg = 'products_id'
    success_url = reverse_lazy('products_list')


# Orders CRUD Views
@method_decorator(login_required, name='dispatch')
class OrdersListView(ListView):
    model = Orders
    template_name = 'orders/list.html'
    context_object_name = 'orders'
    paginate_by = 25

    def get_queryset(self):
        queryset = Orders.objects.select_related(
            'company', 'products', 'employee', 'stage'
        )
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(company__company_name__icontains=search) |
                Q(products__product_name__icontains=search)
            )
        return queryset.order_by('-orders_id')


@method_decorator(login_required, name='dispatch')
class OrdersDetailView(DetailView):
    model = Orders
    template_name = 'orders/detail.html'
    context_object_name = 'order'
    pk_url_kwarg = 'orders_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['order_options'] = OrderOption.objects.filter(orders=self.object)
        context['application_responses'] = ApplicationResponse.objects.filter(order=self.object)
        return context


@method_decorator(login_required, name='dispatch')
class OrdersCreateView(CreateView):
    model = Orders
    form_class = OrdersForm
    template_name = 'orders/form.html'
    
    def get_success_url(self):
        return reverse_lazy('orders_detail', kwargs={'orders_id': self.object.orders_id})


@method_decorator(login_required, name='dispatch')
class OrdersUpdateView(UpdateView):
    model = Orders
    form_class = OrdersForm
    template_name = 'orders/form.html'
    pk_url_kwarg = 'orders_id'
    
    def get_success_url(self):
        return reverse_lazy('orders_detail', kwargs={'orders_id': self.object.orders_id})


@method_decorator(login_required, name='dispatch')
class OrdersDeleteView(DeleteView):
    model = Orders
    template_name = 'orders/confirm_delete.html'
    pk_url_kwarg = 'orders_id'
    success_url = reverse_lazy('orders_list')


# Applications CRUD Views
@method_decorator(login_required, name='dispatch')
class ApplicationsListView(ListView):
    model = Applications
    template_name = 'applications/list.html'
    context_object_name = 'applications'
    paginate_by = 25

    def get_queryset(self):
        queryset = Applications.objects.select_related('product')
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(application_name__icontains=search) |
                Q(product__product_name__icontains=search)
            )
        return queryset.order_by('application_name')


@method_decorator(login_required, name='dispatch')
class ApplicationsDetailView(DetailView):
    model = Applications
    template_name = 'applications/detail.html'
    context_object_name = 'application'
    pk_url_kwarg = 'application_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['questions'] = ApplicationQuestion.objects.filter(application=self.object)
        context['responses'] = ApplicationResponse.objects.filter(application=self.object)
        return context


@method_decorator(login_required, name='dispatch')
class ApplicationsCreateView(CreateView):
    model = Applications
    form_class = ApplicationsForm
    template_name = 'applications/form.html'
    
    def get_success_url(self):
        return reverse_lazy('applications_detail', kwargs={'application_id': self.object.application_id})


@method_decorator(login_required, name='dispatch')
class ApplicationsUpdateView(UpdateView):
    model = Applications
    form_class = ApplicationsForm
    template_name = 'applications/form.html'
    pk_url_kwarg = 'application_id'
    
    def get_success_url(self):
        return reverse_lazy('applications_detail', kwargs={'application_id': self.object.application_id})


@method_decorator(login_required, name='dispatch')
class ApplicationsDeleteView(DeleteView):
    model = Applications
    template_name = 'applications/confirm_delete.html'
    pk_url_kwarg = 'application_id'
    success_url = reverse_lazy('applications_list')


# Employee Contact CRUD Views
@method_decorator(login_required, name='dispatch')
class EmployeeContactListView(ListView):
    model = EmployeeContact
    template_name = 'employees/list.html'
    context_object_name = 'employees'
    paginate_by = 25

    def get_queryset(self):
        queryset = EmployeeContact.objects.select_related('employee_location')
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(employee_name_first__icontains=search) |
                Q(employee_name_last__icontains=search) |
                Q(employee_email__icontains=search)
            )
        return queryset.order_by('employee_name_last', 'employee_name_first')


@method_decorator(login_required, name='dispatch')
class EmployeeContactDetailView(DetailView):
    model = EmployeeContact
    template_name = 'employees/detail.html'
    context_object_name = 'employee'
    pk_url_kwarg = 'employee_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['orders'] = Orders.objects.filter(employee=self.object).order_by('-orders_id')[:10]
        return context


@method_decorator(login_required, name='dispatch')
class EmployeeContactCreateView(CreateView):
    model = EmployeeContact
    form_class = EmployeeContactForm
    template_name = 'employees/form.html'
    
    def get_success_url(self):
        return reverse_lazy('employee_detail', kwargs={'employee_id': self.object.employee_id})


@method_decorator(login_required, name='dispatch')
class EmployeeContactUpdateView(UpdateView):
    model = EmployeeContact
    form_class = EmployeeContactForm
    template_name = 'employees/form.html'
    pk_url_kwarg = 'employee_id'
    
    def get_success_url(self):
        return reverse_lazy('employee_detail', kwargs={'employee_id': self.object.employee_id})


@method_decorator(login_required, name='dispatch')
class EmployeeContactDeleteView(DeleteView):
    model = EmployeeContact
    template_name = 'employees/confirm_delete.html'
    pk_url_kwarg = 'employee_id'
    success_url = reverse_lazy('employee_list')


# Venture CRUD Views
@method_decorator(login_required, name='dispatch')
class VentureListView(ListView):
    model = Venture
    template_name = 'ventures/list.html'
    context_object_name = 'ventures'
    paginate_by = 25

    def get_queryset(self):
        queryset = Venture.objects.all()
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(venture_name__icontains=search) |
                Q(venture_city__icontains=search)
            )
        return queryset.order_by('venture_name')


@method_decorator(login_required, name='dispatch')
class VentureDetailView(DetailView):
    model = Venture
    template_name = 'ventures/detail.html'
    context_object_name = 'venture'
    pk_url_kwarg = 'venture_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['products'] = Products.objects.filter(venture=self.object)
        context['employee_locations'] = EmployeeLocation.objects.filter(venture=self.object)
        return context


@method_decorator(login_required, name='dispatch')
class VentureCreateView(CreateView):
    model = Venture
    form_class = VentureForm
    template_name = 'ventures/form.html'
    
    def get_success_url(self):
        return reverse_lazy('venture_detail', kwargs={'venture_id': self.object.venture_id})


@method_decorator(login_required, name='dispatch')
class VentureUpdateView(UpdateView):
    model = Venture
    form_class = VentureForm
    template_name = 'ventures/form.html'
    pk_url_kwarg = 'venture_id'
    
    def get_success_url(self):
        return reverse_lazy('venture_detail', kwargs={'venture_id': self.object.venture_id})


@method_decorator(login_required, name='dispatch')
class VentureDeleteView(DeleteView):
    model = Venture
    template_name = 'ventures/confirm_delete.html'
    pk_url_kwarg = 'venture_id'
    success_url = reverse_lazy('venture_list')

@login_required
def main_page_view(request, page_name):
    """
    Enhanced main page view with Machine Learning support
    """
    valid_pages = ['IT', 'DocGen', 'Portfolio', 'Workstation', 'Catalog', 'Machine Learning']
    if page_name not in valid_pages:
        return render(request, '404.html', status=404)
    
    # For placeholder pages (REMOVED Machine Learning from this list)
    if page_name in ['IT', 'DocGen', 'Portfolio']:
        return render(request, 'main_pages/placeholder.html', {
            'page_name': page_name,
            'page_config': settings.SKYE_PAGES_CONFIG.get(page_name, {}),
        })
    
    # For Workstation - also placeholder for now
    if page_name == 'Workstation':
        return render(request, 'main_pages/placeholder.html', {
            'page_name': page_name,
            'page_config': settings.SKYE_PAGES_CONFIG.get(page_name, {}),
        })
    
    # For Catalog - load real data with progressive loading
    if page_name == 'Catalog':
        try:
            page_config = SkyeConfigParser.generate_catalog_config()['Catalog']
            section_names = list(page_config.keys())
            
            # Load first 3 sections with real data
            initial_sections = {}
            initial_count = min(3, len(section_names))
            
            for i in range(initial_count):
                section_name = section_names[i]
                initial_sections[section_name] = load_section_data(
                    section_name, 
                    page_config[section_name]
                )
            
            context = {
                'page_name': page_name,
                'page_config': settings.SKYE_PAGES_CONFIG.get(page_name, {}),
                'sections_config': page_config,
                'initial_sections': initial_sections,
                'has_more_sections': len(section_names) > initial_count,
                'next_section_index': initial_count,
                'total_sections': len(section_names)
            }
            
            logger.info(f"Catalog page loaded with {len(initial_sections)} initial sections, "
                       f"{len(section_names) - initial_count} remaining")
            
            return render(request, 'main_pages/main_page.html', context)
            
        except Exception as e:
            logger.error(f"Error loading Catalog page: {e}")
            return render(request, 'main_pages/placeholder.html', {
                'page_name': page_name,
                'error': f'Error loading {page_name}: {str(e)}'
            })
    
    # For Machine Learning - load real data with progressive loading (FIXED)
    if page_name == 'Machine Learning':
        print(f"DEBUG: Attempting to load Machine Learning page")  # Debug line
        try:
            print(f"DEBUG: Trying to get ML config...")  # Debug line
            page_config = SkyeConfigParser.generate_machine_learning_config()['Machine Learning']
            print(f"DEBUG: ML config loaded successfully, sections: {list(page_config.keys())}")  # Debug line
            
            section_names = list(page_config.keys())
            
            # Load first 3 sections with real data
            initial_sections = {}
            initial_count = min(3, len(section_names))
            
            for i in range(initial_count):
                section_name = section_names[i]
                print(f"DEBUG: Loading section {section_name}")  # Debug line
                initial_sections[section_name] = load_section_data(
                    section_name, 
                    page_config[section_name]
                )
            
            context = {
                'page_name': page_name,
                'page_config': settings.SKYE_PAGES_CONFIG.get(page_name, {}),
                'sections_config': page_config,
                'initial_sections': initial_sections,
                'has_more_sections': len(section_names) > initial_count,
                'next_section_index': initial_count,
                'total_sections': len(section_names)
            }
            
            print(f"DEBUG: Rendering main_page.html template")  # Debug line
            logger.info(f"Machine Learning page loaded with {len(initial_sections)} initial sections, "
                       f"{len(section_names) - initial_count} remaining")
            
            return render(request, 'main_pages/main_page.html', context)
            
        except Exception as e:
            print(f"DEBUG: Error loading Machine Learning page: {e}")  # Debug line
            print(f"DEBUG: Error type: {type(e)}")  # Debug line
            import traceback
            print(f"DEBUG: Traceback: {traceback.format_exc()}")  # Debug line
            logger.error(f"Error loading Machine Learning page: {e}")
            return render(request, 'main_pages/placeholder.html', {
                'page_name': page_name,
                'error': f'Error loading {page_name}: {str(e)}'
            })
    
    # Fallback for any other pages
    return render(request, 'main_pages/placeholder.html', {
        'page_name': page_name,
        'page_config': settings.SKYE_PAGES_CONFIG.get(page_name, {}),
    })

# API Views for AJAX requests
@csrf_exempt
def search_companies(request):
    """API endpoint for company search autocomplete"""
    if request.method == 'GET':
        query = request.GET.get('q', '')
        companies = Company.objects.filter(
            company_name__icontains=query
        )[:10]
        
        data = [{
            'id': company.company_id,
            'text': company.company_name
        } for company in companies]
        
        return JsonResponse({'results': data})


@csrf_exempt
def search_products(request):
    """API endpoint for product search autocomplete"""
    if request.method == 'GET':
        query = request.GET.get('q', '')
        products = Products.objects.filter(
            product_name__icontains=query
        )[:10]
        
        data = [{
            'id': product.products_id,
            'text': product.product_name
        } for product in products]
        
        return JsonResponse({'results': data})


@csrf_exempt
def search_employees(request):
    """API endpoint for employee search autocomplete"""
    if request.method == 'GET':
        query = request.GET.get('q', '')
        employees = EmployeeContact.objects.filter(
            Q(employee_name_first__icontains=query) |
            Q(employee_name_last__icontains=query)
        )[:10]
        
        data = [{
            'id': employee.employee_id,
            'text': f"{employee.employee_name_first} {employee.employee_name_last}"
        } for employee in employees]
        
        return JsonResponse({'results': data})


# Additional utility views
@login_required
def reports_dashboard(request):
    """Reports and analytics dashboard"""
    context = {
        'orders_by_stage': {},
        'products_by_venture': {},
        'monthly_orders': {},
    }
    
    # Add your reporting logic here
    return render(request, 'reports/dashboard.html', context)


@login_required
def export_data(request):
    """Export data to CSV/Excel"""
    # Add export functionality here
    pass

@csrf_exempt
@login_required
def get_section_data(request, page_name, section_name):
    """
    Get full data for a specific section (when "View All" is clicked)
    """
    page_config = get_page_config(page_name)
    
    if section_name not in page_config:
        return JsonResponse({'error': 'Section not found'}, status=404)
    
    section_config = page_config[section_name]
    table_name = section_config['table']
    
    try:
        # Get model class
        model_class = apps.get_model('Skye', table_name)
        
        # Handle pagination
        page = request.GET.get('page', 1)
        paginator = Paginator(model_class.objects.all(), 50)  # 50 records per page
        page_obj = paginator.get_page(page)
        
        # Resolve foreign keys
        resolved_data = ForeignKeyResolver.resolve_foreign_keys(page_obj.object_list, table_name)
        
        return JsonResponse({
            'success': True,
            'data': resolved_data,
            'pagination': {
                'current_page': page_obj.number,
                'total_pages': paginator.num_pages,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous(),
                'total_count': paginator.count
            }
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@login_required  
def edit_record(request, page_name, section_name, record_id):
    """
    Handle record editing via modal forms
    """
    page_config = get_page_config(page_name)
    
    if section_name not in page_config:
        return JsonResponse({'error': 'Section not found'}, status=404)
    
    section_config = page_config[section_name]
    table_name = section_config['table']
    
    try:
        model_class = apps.get_model('Skye', table_name)
        
        if request.method == 'GET':
            # Return record data for editing
            record = model_class.objects.get(pk=record_id)
            record_data = {}
            
            for field in model_class._meta.get_fields():
                if not field.is_relation:
                    record_data[field.name] = getattr(record, field.name, None)
                else:
                    # Handle foreign keys
                    fk_obj = getattr(record, field.name, None)
                    record_data[field.name] = fk_obj.pk if fk_obj else None
            
            return JsonResponse({
                'success': True,
                'data': record_data,
                'fields': section_config['columns']
            })
            
        elif request.method == 'POST':
            # Update record
            data = json.loads(request.body)
            record = model_class.objects.get(pk=record_id)
            
            for field_name, value in data.items():
                if hasattr(record, field_name):
                    setattr(record, field_name, value)
            
            record.save()
            
            return JsonResponse({'success': True, 'message': 'Record updated successfully'})
            
    except model_class.DoesNotExist:
        return JsonResponse({'error': 'Record not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@login_required
def add_record(request, page_name, section_name):
    """
    Handle adding new records via modal forms
    """
    page_config = get_page_config(page_name)
    
    if section_name not in page_config:
        return JsonResponse({'error': 'Section not found'}, status=404)
    
    section_config = page_config[section_name]
    table_name = section_config['table']
    
    try:
        model_class = apps.get_model('Skye', table_name)
        
        if request.method == 'GET':
            # Return field structure for new record form
            return JsonResponse({
                'success': True,
                'fields': section_config['columns']
            })
            
        elif request.method == 'POST':
            # Create new record
            data = json.loads(request.body)
            record = model_class(**data)
            record.save()
            
            return JsonResponse({'success': True, 'message': 'Record created successfully', 'id': record.pk})
            
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@login_required
def search_sections(request, page_name):
    """
    Search across all sections in a page
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)
    
    try:
        data = json.loads(request.body)
        search_query = data.get('query', '').strip()
        
        if not search_query:
            return JsonResponse({'error': 'Search query required'}, status=400)
        
        page_config = get_page_config(page_name)
        results = {}
        
        for section_name, section_config in page_config.items():
            table_name = section_config['table']
            
            try:
                model_class = apps.get_model('Skye', table_name)
                
                # Build search filter across searchable columns
                from django.db.models import Q
                search_filter = Q()
                
                for column in section_config['columns']:
                    if column.get('searchable', True):
                        field_name = column['db_column']
                        if hasattr(model_class, field_name):
                            search_filter |= Q(**{f"{field_name}__icontains": search_query})
                
                if search_filter:
                    queryset = model_class.objects.filter(search_filter)[:10]  # Limit results
                    resolved_data = ForeignKeyResolver.resolve_foreign_keys(queryset, table_name)
                    
                    if resolved_data:
                        results[section_name] = {
                            'data': resolved_data,
                            'count': len(resolved_data)
                        }
                        
            except Exception as e:
                continue  # Skip sections with errors
        
        return JsonResponse({
            'success': True,
            'results': results,
            'query': search_query
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def get_page_config(page_name):
    """
    Get configuration for a specific page
    """
    if page_name == 'Catalog':
        return SkyeConfigParser.generate_catalog_config()['Catalog']
    elif page_name == 'Machine Learning':
        return SkyeConfigParser.generate_machine_learning_config()['Machine Learning']
    elif page_name == 'Workstation':
        # Placeholder config
        return {}
    else:
        return {}

def load_section_data(section_name, section_config, limit=20):
    """
    UPDATED: Enhanced helper function to load data using ForeignKeyResolver consistently
    """
    table_name = section_config['table']
    
    # DEBUG: Add this debug output
    print(f"\n=== DEBUG load_section_data ===")
    print(f"Section: {section_name}")
    print(f"Table: {table_name}")
    
    try:
        # Try to get the model class
        model_class = None
        
        # Try different model name variations
        possible_names = [
            table_name,  # e.g., 'venture'
            table_name.title(),  # e.g., 'Venture'
            ''.join(word.title() for word in table_name.split('_')),  # e.g., 'EmployeeContact'
        ]
        
        for model_name in possible_names:
            try:
                model_class = apps.get_model('Skye', model_name)
                print(f"DEBUG: Found model class: {model_class}")
                break
            except LookupError:
                print(f"DEBUG: Model not found: {model_name}")
                continue
        
        if not model_class:
            logger.warning(f"Model not found for table: {table_name}")
            return {
                'config': section_config,
                'data': [],
                'total_count': 0,
                'error': f'Model {table_name} not implemented yet'
            }
        
        # Get limited queryset with select_related for better FK performance
        queryset = model_class.objects.all()[:limit]
        total_count = model_class.objects.count()
        
        print(f"DEBUG: Queryset count: {len(queryset)}")
        if queryset:
            sample_obj = queryset[0]
            print(f"DEBUG: Sample object: {sample_obj}")
            print(f"DEBUG: Sample object fields: {[f.name for f in model_class._meta.fields]}")
            
            # Check for foreign key fields
            fk_fields = []
            for field in model_class._meta.get_fields():
                if hasattr(field, 'related_model') and field.related_model:
                    fk_value = getattr(sample_obj, field.name, None)
                    fk_fields.append({
                        'field_name': field.name,
                        'related_model': field.related_model._meta.model_name,
                        'current_value': fk_value,
                        'current_value_type': type(fk_value).__name__
                    })
            print(f"DEBUG: FK fields found: {fk_fields}")
        
        # Use ForeignKeyResolver for consistent FK resolution
        print(f"DEBUG: Calling ForeignKeyResolver.resolve_foreign_keys...")
        resolved_data = ForeignKeyResolver.resolve_foreign_keys(queryset, table_name)
        print(f"DEBUG: Resolved data count: {len(resolved_data)}")
        if resolved_data:
            print(f"DEBUG: First resolved record: {resolved_data[0]}")
        
        logger.info(f"Loaded {len(resolved_data)} records for {section_name} using ForeignKeyResolver")
        
        return {
            'config': section_config,
            'data': resolved_data,
            'total_count': total_count
        }
        
    except Exception as e:
        print(f"DEBUG: Exception in load_section_data: {e}")
        import traceback
        print(f"DEBUG: Traceback: {traceback.format_exc()}")
        logger.error(f"Error loading {section_name}: {e}")
        return {
            'config': section_config,
            'data': [],
            'total_count': 0,
            'error': str(e)
        }
        
        # Get limited queryset with select_related for better FK performance
        queryset = model_class.objects.all()[:limit]
        total_count = model_class.objects.count()
        
        # Use ForeignKeyResolver for consistent FK resolution
        resolved_data = ForeignKeyResolver.resolve_foreign_keys(queryset, table_name)
        
        logger.info(f"Loaded {len(resolved_data)} records for {section_name} using ForeignKeyResolver")
        
        return {
            'config': section_config,
            'data': resolved_data,
            'total_count': total_count
        }
        
    except Exception as e:
        logger.error(f"Error loading {section_name}: {e}")
        return {
            'config': section_config,
            'data': [],
            'total_count': 0,
            'error': str(e)
        }

@csrf_exempt
@login_required
def load_more_sections(request, page_name):
    """
    UPDATED: Enhanced AJAX endpoint for progressive loading with consistent ForeignKeyResolver usage
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)
    
    try:
        data = json.loads(request.body)
        start_index = data.get('start_index', 3)
        batch_size = getattr(settings, 'PROGRESSIVE_LOADING', {}).get('SECTION_BATCH_SIZE', 3)
        
        logger.info(f"Loading more sections for {page_name}, start_index: {start_index}")
        
        if page_name == 'Catalog':
            page_config = SkyeConfigParser.generate_catalog_config()['Catalog']
        elif page_name == 'Machine Learning':
            page_config = SkyeConfigParser.generate_machine_learning_config()['Machine Learning']
        else:
            return JsonResponse({'error': f'Progressive loading not supported for {page_name}'}, status=400)
        
        section_names = list(page_config.keys())
        
        # Calculate batch boundaries
        end_index = min(start_index + batch_size, len(section_names))
        batch_sections = section_names[start_index:end_index]
        
        logger.info(f"Loading sections {start_index} to {end_index-1}: {batch_sections}")
        
        # Load batch sections using updated load_section_data (which now uses ForeignKeyResolver)
        sections_data = {}
        for section_name in batch_sections:
            sections_data[section_name] = load_section_data(
                section_name, 
                page_config[section_name]
            )
        
        return JsonResponse({
            'success': True,
            'sections': sections_data,
            'has_more': end_index < len(section_names),
            'next_index': end_index,
            'loaded_count': len(sections_data),
            'total_count': len(section_names)
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON in request body'}, status=400)
    except Exception as e:
        logger.error(f"Error in load_more_sections: {e}")
        return JsonResponse({'error': str(e)}, status=500)
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON in request body'}, status=400)
    except Exception as e:
        logger.error(f"Error in load_more_sections: {e}")
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@login_required
def search_sections(request, page_name):
    """
    UPDATED: Enhanced search across all sections with consistent ForeignKeyResolver usage
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)
    
    try:
        data = json.loads(request.body)
        search_query = data.get('query', '').strip()
        
        if not search_query:
            return JsonResponse({'error': 'Search query required'}, status=400)
        
        logger.info(f"Searching {page_name} for: {search_query}")
        
        if page_name == 'Catalog':
            page_config = SkyeConfigParser.generate_catalog_config()['Catalog']
        elif page_name == 'Machine Learning':
            page_config = SkyeConfigParser.generate_machine_learning_config()['Machine Learning']
        else:
            return JsonResponse({'error': f'Search not supported for {page_name}'}, status=400)
        
        results = {}
        
        for section_name, section_config in page_config.items():
            table_name = section_config['table']
            
            try:
                # Try to get model class
                model_class = None
                possible_names = [
                    table_name,
                    table_name.title(),
                    ''.join(word.title() for word in table_name.split('_')),
                ]
                
                for model_name in possible_names:
                    try:
                        model_class = apps.get_model('Skye', model_name)
                        break
                    except LookupError:
                        continue
                
                if not model_class:
                    continue
                
                # Build search filter across searchable columns
                from django.db.models import Q
                search_filter = Q()
                
                for column in section_config['columns']:
                    if column.get('searchable', True):
                        field_name = column['db_column']
                        if hasattr(model_class, field_name):
                            search_filter |= Q(**{f"{field_name}__icontains": search_query})
                
                if search_filter:
                    queryset = model_class.objects.filter(search_filter)[:10]
                    
                    if queryset.exists():
                        # Use ForeignKeyResolver for consistent FK resolution
                        resolved_data = ForeignKeyResolver.resolve_foreign_keys(queryset, table_name)
                        
                        results[section_name] = {
                            'config': section_config,
                            'data': resolved_data,
                            'count': len(resolved_data)
                        }
                        
            except Exception as e:
                logger.warning(f"Error searching section {section_name}: {e}")
                continue
        
        return JsonResponse({
            'success': True,
            'results': results,
            'query': search_query,
            'sections_found': len(results)
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON in request body'}, status=400)
    except Exception as e:
        logger.error(f"Error in search_sections: {e}")
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@login_required
def get_section_data(request, page_name, section_name):
    """
    UPDATED: Get full data for a specific section with consistent ForeignKeyResolver usage
    """
    try:
        if page_name == 'Catalog':
            page_config = SkyeConfigParser.generate_catalog_config()['Catalog']
        elif page_name == 'Machine Learning':
            page_config = SkyeConfigParser.generate_machine_learning_config()['Machine Learning']
        else:
            return JsonResponse({'error': f'Section data not supported for {page_name}'}, status=400)
        
        if section_name not in page_config:
            return JsonResponse({'error': 'Section not found'}, status=404)
        
        section_config = page_config[section_name]
        table_name = section_config['table']
        
        # Try to get model class
        model_class = None
        possible_names = [
            table_name,
            table_name.title(),
            ''.join(word.title() for word in table_name.split('_')),
        ]
        
        for model_name in possible_names:
            try:
                model_class = apps.get_model('Skye', model_name)
                break
            except LookupError:
                continue
        
        if not model_class:
            return JsonResponse({'error': f'Model {table_name} not found'}, status=404)
        
        # Handle pagination
        from django.core.paginator import Paginator
        page = request.GET.get('page', 1)
        paginator = Paginator(model_class.objects.all(), 50)
        page_obj = paginator.get_page(page)
        
        # Use ForeignKeyResolver for consistent FK resolution
        resolved_data = ForeignKeyResolver.resolve_foreign_keys(page_obj.object_list, table_name)
        
        return JsonResponse({
            'success': True,
            'data': resolved_data,
            'config': section_config,
            'pagination': {
                'current_page': page_obj.number,
                'total_pages': paginator.num_pages,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous(),
                'total_count': paginator.count
            }
        })
        
    except Exception as e:
        logger.error(f"Error in get_section_data: {e}")
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@login_required
def get_form_fields(request, page_name, section_name):
    """
    Get form field metadata for creating new records
    """
    if request.method != 'GET':
        return JsonResponse({'error': 'GET method required'}, status=405)
    
    try:
        page_config = get_page_config(page_name)
        
        if section_name not in page_config:
            return JsonResponse({'error': 'Section not found'}, status=404)
        
        section_config = page_config[section_name]
        table_name = section_config['table']
        
        # Get field metadata using FieldGenerator
        field_data = FieldGenerator.get_model_fields(section_name, table_name)
        
        if 'error' in field_data:
            return JsonResponse({
                'success': False,
                'error': field_data['error']
            })
        
        return JsonResponse({
            'success': True,
            'section_name': section_name,
            'table_name': table_name,
            'fields': field_data['fields'],
            'model_name': field_data['model_name']
        })
        
    except Exception as e:
        logger.error(f"Error getting form fields for {section_name}: {e}")
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@login_required
def create_record(request, page_name, section_name):
    """
    Create a new record using form data
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)
    
    try:
        page_config = get_page_config(page_name)
        
        if section_name not in page_config:
            return JsonResponse({'error': 'Section not found'}, status=404)
        
        section_config = page_config[section_name]
        table_name = section_config['table']
        
        # Parse form data
        form_data = json.loads(request.body)
        
        # Create record using FieldGenerator
        result = FieldGenerator.create_record(table_name, form_data)
        
        if result['success']:
            logger.info(f"Successfully created {section_name} record: {result['display_value']}")
            return JsonResponse({
                'success': True,
                'message': result['message'],
                'id': result['id'],
                'display_value': result['display_value']
            })
        else:
            return JsonResponse({
                'success': False,
                'error': result['error']
            })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON in request body'}, status=400)
    except Exception as e:
        logger.error(f"Error creating record for {section_name}: {e}")
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@login_required
def update_record(request, page_name, section_name, record_id):
    """
    Update an existing record using form data
    """
    if request.method == 'GET':
        # Return existing record data for editing
        try:
            page_config = get_page_config(page_name)
            
            if section_name not in page_config:
                return JsonResponse({'error': 'Section not found'}, status=404)
            
            section_config = page_config[section_name]
            table_name = section_config['table']
            
            # Get model class
            model_class = FieldGenerator._get_model_class(table_name)
            if not model_class:
                return JsonResponse({'error': 'Model not found'}, status=404)
            
            # Get the record
            try:
                record = model_class.objects.get(pk=record_id)
            except model_class.DoesNotExist:
                return JsonResponse({'error': 'Record not found'}, status=404)
            
            # Convert record to data structure
            record_data = {}
            for field in model_class._meta.get_fields():
                if not field.is_relation or hasattr(field, 'related_model'):
                    try:
                        value = getattr(record, field.name, None)
                        if hasattr(value, 'pk'):
                            record_data[field.name] = value.pk
                        else:
                            record_data[field.name] = value
                    except Exception:
                        record_data[field.name] = None
            
            return JsonResponse({
                'success': True,
                'data': record_data
            })
            
        except Exception as e:
            logger.error(f"Error getting record {record_id} for {section_name}: {e}")
            return JsonResponse({'error': str(e)}, status=500)
    
    elif request.method == 'POST':
        # Update the record
        try:
            page_config = get_page_config(page_name)
            
            if section_name not in page_config:
                return JsonResponse({'error': 'Section not found'}, status=404)
            
            section_config = page_config[section_name]
            table_name = section_config['table']
            
            # Get model class
            model_class = FieldGenerator._get_model_class(table_name)
            if not model_class:
                return JsonResponse({'error': 'Model not found'}, status=404)
            
            # Get the record
            try:
                record = model_class.objects.get(pk=record_id)
            except model_class.DoesNotExist:
                return JsonResponse({'error': 'Record not found'}, status=404)
            
            # Parse form data
            form_data = json.loads(request.body)
            
            # Process and update fields
            processed_data = FieldGenerator._process_form_data(model_class, form_data)
            
            for field_name, value in processed_data.items():
                if hasattr(record, field_name):
                    setattr(record, field_name, value)
            
            # Validate and save
            record.full_clean()
            record.save()
            
            logger.info(f"Successfully updated {section_name} record {record_id}")
            return JsonResponse({
                'success': True,
                'message': f'{model_class.__name__} updated successfully',
                'id': record.pk,
                'display_value': str(record)
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON in request body'}, status=400)
        except Exception as e:
            logger.error(f"Error updating record {record_id} for {section_name}: {e}")
            return JsonResponse({'error': str(e)}, status=500)
    
    else:
        return JsonResponse({'error': 'GET or POST method required'}, status=405)


@csrf_exempt
@login_required
def get_foreign_key_options(request, page_name, section_name, field_name):
    """
    Get options for a specific foreign key field (for dynamic loading)
    """
    if request.method != 'GET':
        return JsonResponse({'error': 'GET method required'}, status=405)
    
    try:
        page_config = get_page_config(page_name)
        
        if section_name not in page_config:
            return JsonResponse({'error': 'Section not found'}, status=404)
        
        section_config = page_config[section_name]
        table_name = section_config['table']
        
        # Get model class
        model_class = FieldGenerator._get_model_class(table_name)
        if not model_class:
            return JsonResponse({'error': 'Model not found'}, status=404)
        
        # Find the field
        try:
            field = model_class._meta.get_field(field_name)
        except:
            return JsonResponse({'error': 'Field not found'}, status=404)
        
        # Process foreign key field
        if hasattr(field, 'related_model'):
            fk_info = FieldGenerator._process_foreign_key(field)
            
            return JsonResponse({
                'success': True,
                'field_name': field_name,
                'options': fk_info['options'],
                'empty_label': fk_info['empty_label']
            })
        else:
            return JsonResponse({'error': 'Field is not a foreign key'}, status=400)
        
    except Exception as e:
        logger.error(f"Error getting FK options for {field_name}: {e}")
        return JsonResponse({'error': str(e)}, status=500)