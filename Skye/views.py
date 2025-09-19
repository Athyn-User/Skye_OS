# Skye/views.py

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
    """Main dashboard with key metrics and recent activity"""
    context = {
        'total_companies': Company.objects.count(),
        'total_products': Products.objects.count(),
        'total_orders': Orders.objects.count(),
        'total_applications': Applications.objects.count(),
        'recent_orders': Orders.objects.select_related('company', 'products').order_by('-orders_id')[:10],
        'recent_companies': Company.objects.order_by('-company_id')[:5],
    }
    return render(request, 'dashboard.html', context)


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