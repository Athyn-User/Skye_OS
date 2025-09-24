from django.contrib import admin
from .models import Company, Broker, Product, Application, Quote

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['company_name', 'company_type', 'annual_revenue', 'employee_count', 'is_active', 'created_at']
    list_filter = ['company_type', 'is_active', 'created_at']
    search_fields = ['company_name', 'tax_id', 'industry_description']
    ordering = ['-created_at']

@admin.register(Broker)
class BrokerAdmin(admin.ModelAdmin):
    list_display = ['broker_name', 'broker_code', 'broker_type', 'is_active', 'created_at']
    list_filter = ['broker_type', 'is_active']
    search_fields = ['broker_name', 'broker_code']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['product_name', 'product_code', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['product_name', 'product_code', 'description']

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ['application_number', 'company', 'broker', 'product', 'application_status', 'estimated_premium', 'submission_date']
    list_filter = ['application_status', 'product', 'submission_date']
    search_fields = ['application_number', 'company__company_name', 'broker__broker_name']
    date_hierarchy = 'submission_date'
    ordering = ['-submission_date']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('application_number', 'company', 'broker', 'product')
        }),
        ('Dates', {
            'fields': ('submission_date', 'target_effective_date')
        }),
        ('Status & Pricing', {
            'fields': ('application_status', 'estimated_premium', 'quoted_premium', 'bound_premium')
        }),
        ('Notes', {
            'fields': ('underwriting_notes',),
            'classes': ('collapse',)
        }),
    )

@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
    list_display = ['quote_number', 'application', 'quote_status', 'total_premium', 'quote_date', 'effective_date']
    list_filter = ['quote_status', 'quote_date']
    search_fields = ['quote_number', 'application__application_number', 'application__company__company_name']
    date_hierarchy = 'quote_date'
    ordering = ['-quote_date']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('quote_number', 'application', 'quote_version')
        }),
        ('Dates', {
            'fields': ('quote_date', 'effective_date', 'expiration_date')
        }),
        ('Pricing', {
            'fields': ('quote_status', 'total_premium', 'commission_amount')
        }),
        ('Special Conditions', {
            'fields': ('special_conditions',),
            'classes': ('collapse',)
        }),
    )

from .models import Certificate, CertificateTemplate, CertificateCoverage

@admin.register(CertificateTemplate)
class CertificateTemplateAdmin(admin.ModelAdmin):
    list_display = ['template_name', 'template_type', 'is_active', 'created_at']
    list_filter = ['template_type', 'is_active']
    search_fields = ['template_name', 'description']

@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ['certificate_number', 'certificate_holder_name', 'quote', 'certificate_status', 'effective_date', 'expiration_date']
    list_filter = ['certificate_status', 'effective_date', 'template']
    search_fields = ['certificate_number', 'certificate_holder_name', 'quote__quote_number']
    date_hierarchy = 'effective_date'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('certificate_number', 'quote', 'template', 'certificate_status')
        }),
        ('Certificate Holder', {
            'fields': ('certificate_holder_name', 'certificate_holder_address')
        }),
        ('Additional Insured', {
            'fields': ('additional_insured_name', 'additional_insured_address'),
            'classes': ('collapse',)
        }),
        ('Project Information', {
            'fields': ('project_description', 'project_location'),
            'classes': ('collapse',)
        }),
        ('Dates', {
            'fields': ('effective_date', 'expiration_date')
        }),
        ('Special Provisions', {
            'fields': ('waiver_of_subrogation', 'primary_and_noncontributory', 'special_provisions')
        }),
    )

@admin.register(CertificateCoverage)
class CertificateCoverageAdmin(admin.ModelAdmin):
    list_display = ['certificate', 'coverage_type', 'each_occurrence', 'general_aggregate', 'policy_effective_date']
    list_filter = ['coverage_type', 'policy_effective_date']
    search_fields = ['certificate__certificate_number', 'policy_number']
