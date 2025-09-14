# Skye_OS/views.py

from django.shortcuts import render
from django.http import JsonResponse
from rest_framework import viewsets
from rest_framework.decorators import api_view
from .models import Venture, Drive, EmployeeLocation, GenerationJob, Parameter

def catalog_view(request):
    """Main catalog page view"""
    ventures = Venture.objects.all()
    drives = Drive.objects.select_related('venture').all()
    employee_locations = EmployeeLocation.objects.select_related('venture').all()
    
    context = {
        'ventures': ventures,
        'drives': drives,
        'employee_locations': employee_locations,
    }
    return render(request, 'Skye_OS/catalog.html', context)

def machine_learning_view(request):
    """Machine learning page view"""
    generation_jobs = GenerationJob.objects.all()
    parameters = Parameter.objects.all()
    
    context = {
        'generation_jobs': generation_jobs,
        'parameters': parameters,
    }
    return render(request, 'Skye_OS/machine_learning.html', context)

def dashboard_view(request):
    """Main dashboard view"""
    return render(request, 'Skye_OS/dashboard.html')

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