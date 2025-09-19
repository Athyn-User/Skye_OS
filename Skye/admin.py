# Skye/admin.py

from django.contrib import admin
from .models import (
    Venture, Coverage, Products, Company, CompanyContact, CompanyLocation,
    EmployeeLocation, EmployeeContact, Orders, Applications, Parameter,
    ApplicationQuestion, ApplicationResponse, Cover, Options, Limits,
    Retention, OrderOption, Document, Broker, BrokerLocation, BrokerContact,
    Stage, FlowOrigin, Workflow, Task, WorkflowDetail, ParameterType
)


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('company_id', 'company_name')
    search_fields = ('company_name',)
    list_filter = ('company_name',)


@admin.register(CompanyContact)
class CompanyContactAdmin(admin.ModelAdmin):
    list_display = ('company_contact_id', 'company', 'company_contact_first', 'company_contact_last', 'company_contact_email')
    search_fields = ('company_contact_first', 'company_contact_last', 'company_contact_email')
    list_filter = ('company',)


@admin.register(CompanyLocation)
class CompanyLocationAdmin(admin.ModelAdmin):
    list_display = ('company_location_id', 'company', 'company_location_city', 'company_location_state', 'company_mailing')
    search_fields = ('company_location_city', 'company_location_state')
    list_filter = ('company', 'company_mailing')


@admin.register(Venture)
class VentureAdmin(admin.ModelAdmin):
    list_display = ('venture_id', 'venture_name', 'venture_city', 'venture_state')
    search_fields = ('venture_name', 'venture_city')
    list_filter = ('venture_state',)


@admin.register(Coverage)
class CoverageAdmin(admin.ModelAdmin):
    list_display = ('coverage_id', 'coverage_name')
    search_fields = ('coverage_name',)


@admin.register(Products)
class ProductsAdmin(admin.ModelAdmin):
    list_display = ('products_id', 'product_name', 'venture', 'coverage', 'product_code')
    search_fields = ('product_name', 'product_code')
    list_filter = ('venture', 'coverage')


@admin.register(EmployeeLocation)
class EmployeeLocationAdmin(admin.ModelAdmin):
    list_display = ('employee_location_id', 'venture', 'employee_location_name', 'employee_location_city')
    search_fields = ('employee_location_name', 'employee_location_city')
    list_filter = ('venture',)


@admin.register(EmployeeContact)
class EmployeeContactAdmin(admin.ModelAdmin):
    list_display = ('employee_id', 'employee_name_first', 'employee_name_last', 'employee_email', 'employee_location')
    search_fields = ('employee_name_first', 'employee_name_last', 'employee_email')
    list_filter = ('employee_location',)


@admin.register(Stage)
class StageAdmin(admin.ModelAdmin):
    list_display = ('stage_id', 'stage_name')
    search_fields = ('stage_name',)


@admin.register(FlowOrigin)
class FlowOriginAdmin(admin.ModelAdmin):
    list_display = ('flow_origin_id', 'flow_origin_name')
    search_fields = ('flow_origin_name',)


@admin.register(Workflow)
class WorkflowAdmin(admin.ModelAdmin):
    list_display = ('workflow_id', 'workflow_name', 'workflow_type')
    search_fields = ('workflow_name',)
    list_filter = ('workflow_type',)


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('task_id', 'task_name', 'task_display')
    search_fields = ('task_name', 'task_description')


@admin.register(WorkflowDetail)
class WorkflowDetailAdmin(admin.ModelAdmin):
    list_display = ('workflow_detail_id', 'workflow', 'stage', 'task', 'workflow_sequence', 'man_auto')
    list_filter = ('workflow', 'stage', 'man_auto')


@admin.register(Orders)
class OrdersAdmin(admin.ModelAdmin):
    list_display = ('orders_id', 'company', 'products', 'stage', 'employee', 'order_created')
    search_fields = ('company__company_name', 'products__product_name')
    list_filter = ('stage', 'venture', 'flow_origin')
    date_hierarchy = None  # order_created is TimeField, not DateTimeField


@admin.register(Applications)
class ApplicationsAdmin(admin.ModelAdmin):
    list_display = ('application_id', 'application_name', 'product')
    search_fields = ('application_name',)
    list_filter = ('product',)


@admin.register(ParameterType)
class ParameterTypeAdmin(admin.ModelAdmin):
    list_display = ('parameter_type_id', 'parameter_type_name')
    search_fields = ('parameter_type_name',)


@admin.register(Parameter)
class ParameterAdmin(admin.ModelAdmin):
    list_display = ('parameter_id', 'parameter_name', 'parameter_type', 'parameter_quote', 'parameter_binder', 'parameter_policy')
    search_fields = ('parameter_name',)
    list_filter = ('parameter_type', 'parameter_quote', 'parameter_binder', 'parameter_policy')


@admin.register(ApplicationQuestion)
class ApplicationQuestionAdmin(admin.ModelAdmin):
    list_display = ('application_question_id', 'application', 'parameter')
    list_filter = ('application', 'parameter')


@admin.register(ApplicationResponse)
class ApplicationResponseAdmin(admin.ModelAdmin):
    list_display = ('application_response_id', 'application', 'application_question', 'order')
    list_filter = ('application', 'order')


@admin.register(Cover)
class CoverAdmin(admin.ModelAdmin):
    list_display = ('cover_id', 'cover_name', 'product')
    search_fields = ('cover_name',)
    list_filter = ('product',)


@admin.register(Options)
class OptionsAdmin(admin.ModelAdmin):
    list_display = ('options_id', 'option_name')
    search_fields = ('option_name',)


@admin.register(Limits)
class LimitsAdmin(admin.ModelAdmin):
    list_display = ('limits_id', 'product', 'cover', 'limit_text', 'limit_pc_number', 'limit_ag_number')
    list_filter = ('product', 'cover')


@admin.register(Retention)
class RetentionAdmin(admin.ModelAdmin):
    list_display = ('retention_id', 'products', 'cover', 'retention_text', 'retention_pc_number', 'retention_ag_number')
    list_filter = ('products', 'cover')


@admin.register(OrderOption)
class OrderOptionAdmin(admin.ModelAdmin):
    list_display = ('order_option_id', 'orders', 'options', 'cover', 'order_option_include', 'premium', 'bound')
    list_filter = ('order_option_include', 'bound', 'options', 'cover')


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('document_id', 'document_name', 'product', 'document_number', 'default_document')
    search_fields = ('document_name', 'document_number')
    list_filter = ('product', 'default_document')


@admin.register(Broker)
class BrokerAdmin(admin.ModelAdmin):
    list_display = ('broker_id', 'broker_name')
    search_fields = ('broker_name',)


@admin.register(BrokerLocation)
class BrokerLocationAdmin(admin.ModelAdmin):
    list_display = ('broker_location_id', 'broker', 'broker_city', 'broker_state_id', 'broker_zip')
    search_fields = ('broker_city',)
    list_filter = ('broker', 'broker_state_id')


@admin.register(BrokerContact)
class BrokerContactAdmin(admin.ModelAdmin):
    list_display = ('broker_contact_id', 'broker_location', 'broker_first_name', 'broker_last_name', 'broker_email')
    search_fields = ('broker_first_name', 'broker_last_name', 'broker_email')
    list_filter = ('broker_location',)


# Customize the admin site header
admin.site.site_header = "Skye OS Administration"
admin.site.site_title = "Skye OS Admin"
admin.site.index_title = "Welcome to Skye OS Administration"