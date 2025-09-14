# Skye_OS/admin.py

from django.contrib import admin
from .models import Venture, Drive, EmployeeLocation, GenerationJob, Parameter

@admin.register(Venture)
class VentureAdmin(admin.ModelAdmin):
    list_display = ['venture_id', 'venture_name', 'venture_city', 'venture_state']
    search_fields = ['venture_name', 'venture_city']

@admin.register(Drive)
class DriveAdmin(admin.ModelAdmin):
    list_display = ['drive_id', 'drive_name', 'venture']
    list_filter = ['venture']

@admin.register(EmployeeLocation)
class EmployeeLocationAdmin(admin.ModelAdmin):
    list_display = ['employee_location_id', 'employee_location_name', 'venture', 'employee_location_city']
    list_filter = ['venture', 'employee_location_state']

@admin.register(GenerationJob)
class GenerationJobAdmin(admin.ModelAdmin):
    list_display = ['generation_job_id', 'generator_model_id', 'product_id', 'data_seed_id']

@admin.register(Parameter)
class ParameterAdmin(admin.ModelAdmin):
    list_display = ['parameter_id', 'parameter_name', 'parameter_type_id']
    search_fields = ['parameter_name']