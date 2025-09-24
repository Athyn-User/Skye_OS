from django.contrib import admin
from .models import DocumentCategory, Document, DocumentAccessLog

@admin.register(DocumentCategory)
class DocumentCategoryAdmin(admin.ModelAdmin):
    list_display = ['category_name', 'description', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['category_name', 'description']

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['document_name', 'document_category', 'document_status', 'file_size_mb', 'upload_date', 'uploaded_by']
    list_filter = ['document_category', 'document_status', 'access_level', 'is_confidential', 'upload_date']
    search_fields = ['document_name', 'original_filename', 'description']
    readonly_fields = ['file_size_bytes', 'file_path', 'upload_date', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('document_name', 'document_category', 'description')
        }),
        ('File Information', {
            'fields': ('original_filename', 'file_path', 'file_size_bytes', 'mime_type')
        }),
        ('Relationships', {
            'fields': ('application', 'quote', 'company')
        }),
        ('Status & Security', {
            'fields': ('document_status', 'access_level', 'is_confidential')
        }),
        ('Version Control', {
            'fields': ('version_number', 'is_current_version', 'parent_document')
        }),
    )

@admin.register(DocumentAccessLog)
class DocumentAccessLogAdmin(admin.ModelAdmin):
    list_display = ['document', 'access_type', 'accessed_by', 'access_timestamp']
    list_filter = ['access_type', 'access_timestamp']
    readonly_fields = ['access_timestamp']
