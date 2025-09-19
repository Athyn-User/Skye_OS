# Skye/views.py

import json
from django.shortcuts import redirect
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

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.paginator import Paginator
from django.apps import apps

from .config_parser import SkyeConfigParser
from .services import ForeignKeyResolver, ProgressiveDataLoader

from .models import (
    Venture, Coverage, Products, Company, CompanyContact, CompanyLocation,
    EmployeeLocation, EmployeeContact, Orders, Applications, Parameter,
    ApplicationQuestion, ApplicationResponse, Cover, Options, Limits,
    Retention, OrderOption, Document, Broker, BrokerLocation, BrokerContact,
    Stage, FlowOrigin, Workflow, Task, WorkflowDetail, ParameterType
)
from .forms import (
    CompanyForm, CompanyContactForm, ProductsForm, OrdersForm,
    ApplicationsForm, EmployeeContactForm, VentureForm
)

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

def load_section_data(section_name, section_config):
    """Helper function to load data for a single section"""
    table_name = section_config['table']
    
    try:
        # Get model class and data
        model_class = apps.get_model('Skye', table_name)
        
        # Get limited queryset (20 records)
        queryset = model_class.objects.all()[:20]
        
        # Convert to simple data structure
        data = []
        for obj in queryset:
            obj_data = {'pk': obj.pk}
            for column in section_config['columns']:
                field_name = column['db_column']
                if hasattr(obj, field_name):
                    value = getattr(obj, field_name)
                    # Handle foreign keys - show ID for now
                    if hasattr(value, 'pk'):
                        obj_data[field_name] = f"{value} (ID: {value.pk})"
                    else:
                        obj_data[field_name] = value if value is not None else ""
                else:
                    obj_data[field_name] = ""
            data.append(obj_data)
        
        return {
            'config': section_config,
            'data': data,
            'total_count': model_class.objects.count()
        }
        
    except Exception as e:
        print(f"Error loading {section_name}: {e}")
        return {
            'config': section_config,
            'data': [],
            'total_count': 0,
            'error': str(e)
        }

@login_required
def main_page_view(request, page_name):
    """
    Enhanced main page view that loads real data with progressive loading
    """
    valid_pages = ['IT', 'DocGen', 'Portfolio', 'Workstation', 'Catalog', 'Machine Learning']
    if page_name not in valid_pages:
        return render(request, '404.html', status=404)
    
    # For placeholder pages
    if page_name in ['IT', 'DocGen', 'Portfolio']:
        return render(request, 'main_pages/placeholder.html', {
            'page_name': page_name,
            'page_config': settings.SKYE_PAGES_CONFIG.get(page_name, {}),
        })
    
    # For Catalog - load real data with progressive loading
    if page_name == 'Catalog':
        page_config = SkyeConfigParser.generate_catalog_config()['Catalog']
        
        # Load first 3 sections with real data
        initial_sections = {}
        section_names = list(page_config.keys())
        
        # Load first 3 sections
        for section_name in section_names[:3]:
            initial_sections[section_name] = load_section_data(section_name, page_config[section_name])
        
        context = {
            'page_name': page_name,
            'page_config': settings.SKYE_PAGES_CONFIG.get(page_name, {}),
            'sections_config': page_config,
            'initial_sections': initial_sections,
            'has_more_sections': len(section_names) > 3,
            'next_section_index': 3,
            'total_sections': len(section_names)
        }
        print(f"DEBUG: Total sections in config: {len(page_config)}")
        print(f"DEBUG: Section names: {list(page_config.keys())}")

        return render(request, 'main_pages/main_page.html', context)
    
    # For other active pages (Workstation, Machine Learning)
    return render(request, 'main_pages/placeholder.html', {
        'page_name': page_name,
        'page_config': settings.SKYE_PAGES_CONFIG.get(page_name, {}),
    })

@csrf_exempt
@login_required
def load_more_sections(request, page_name):
    """
    AJAX endpoint for progressive loading of remaining sections
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)
    
    try:
        data = json.loads(request.body)
        start_index = data.get('start_index', 3)
        
        if page_name == 'Catalog':
            page_config = SkyeConfigParser.generate_catalog_config()['Catalog']
            section_names = list(page_config.keys())
            
            # Load next batch (3 sections at a time)
            batch_size = 3
            end_index = min(start_index + batch_size, len(section_names))
            batch_sections = section_names[start_index:end_index]
            
            sections_data = {}
            for section_name in batch_sections:
                sections_data[section_name] = load_section_data(section_name, page_config[section_name])
            
            return JsonResponse({
                'success': True,
                'sections': sections_data,
                'has_more': end_index < len(section_names),
                'next_index': end_index
            })
        
        return JsonResponse({'error': 'Invalid page'}, status=400)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@login_required
def load_more_sections(request, page_name):
    """
    AJAX endpoint for progressive loading of sections
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)
    
    try:
        data = json.loads(request.body)
        start_index = data.get('start_index', 0)
        batch_size = settings.PROGRESSIVE_LOADING['SECTION_BATCH_SIZE']
        
        page_config = get_page_config(page_name)
        section_names = list(page_config.keys())
        
        batch_data = ProgressiveDataLoader.load_sections_batch(
            page_config,
            section_names,
            start_index=start_index,
            batch_size=batch_size
        )
        
        return JsonResponse({
            'success': True,
            'sections': batch_data['sections'],
            'has_more': batch_data['has_more'],
            'next_index': batch_data['next_index']
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

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
    TODO: Replace with actual Excel parser
    """
    if page_name == 'Catalog':
        return SkyeConfigParser.generate_catalog_config()['Catalog']
    elif page_name == 'Workstation':
        # Placeholder config
        return {}
    elif page_name == 'Machine Learning':
        # Placeholder config  
        return {}
    else:
        return {}