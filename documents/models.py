from django.db import models
from django.contrib.auth.models import User
from django.core.files.storage import default_storage
from django.urls import reverse
import os

class DocumentCategory(models.Model):
    document_category_id = models.AutoField(primary_key=True)
    category_name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'document_categories'
        verbose_name_plural = 'Document Categories'

    def __str__(self):
        return self.category_name

class Document(models.Model):
    STATUS_CHOICES = [
        ('uploaded', 'Uploaded'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('archived', 'Archived'),
    ]
    
    ACCESS_LEVELS = [
        ('public', 'Public'),
        ('internal', 'Internal'),
        ('restricted', 'Restricted'),
        ('confidential', 'Confidential'),
    ]

    document_id = models.AutoField(primary_key=True)
    document_category = models.ForeignKey(DocumentCategory, on_delete=models.CASCADE, db_column='document_category_id')
    
    # Relationships to other entities
    application = models.ForeignKey('applications.Application', on_delete=models.SET_NULL, null=True, blank=True, db_column='application_id')
    quote = models.ForeignKey('applications.Quote', on_delete=models.SET_NULL, null=True, blank=True, db_column='quote_id')
    company = models.ForeignKey('applications.Company', on_delete=models.SET_NULL, null=True, blank=True, db_column='company_id')
    
    # Document metadata
    document_name = models.CharField(max_length=255)
    original_filename = models.CharField(max_length=255)
    file_path = models.CharField(max_length=500)
    file_size_bytes = models.BigIntegerField()
    mime_type = models.CharField(max_length=100)
    file_extension = models.CharField(max_length=10, blank=True, null=True)
    
    # Version control
    version_number = models.IntegerField(default=1)
    is_current_version = models.BooleanField(default=True)
    parent_document = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, db_column='parent_document_id')
    
    # Status and workflow
    document_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='uploaded')
    upload_date = models.DateTimeField(auto_now_add=True)
    
    # Security and access
    is_confidential = models.BooleanField(default=False)
    access_level = models.CharField(max_length=20, choices=ACCESS_LEVELS, default='internal')
    
    # Audit trail (using User model for simplicity)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='uploaded_documents')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_documents')
    approved_date = models.DateTimeField(null=True, blank=True)
    
    # Additional metadata
    description = models.TextField(blank=True, null=True)
    tags = models.JSONField(default=list, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'documents'
        ordering = ['-upload_date']

    def __str__(self):
        return f"{self.document_name} (v{self.version_number})"

    def get_absolute_url(self):
        return reverse('documents:document_detail', kwargs={'pk': self.pk})

    def get_download_url(self):
        return reverse('documents:document_download', kwargs={'pk': self.pk})

    @property
    def file_size_mb(self):
        return round(self.file_size_bytes / (1024 * 1024), 2)

    @property
    def is_image(self):
        return self.mime_type.startswith('image/')

    @property
    def is_pdf(self):
        return self.mime_type == 'application/pdf'

class DocumentAccessLog(models.Model):
    ACCESS_TYPES = [
        ('view', 'View'),
        ('download', 'Download'),
        ('edit', 'Edit'),
        ('delete', 'Delete'),
    ]

    access_log_id = models.AutoField(primary_key=True)
    document = models.ForeignKey(Document, on_delete=models.CASCADE, db_column='document_id')
    accessed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    access_type = models.CharField(max_length=10, choices=ACCESS_TYPES)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, null=True)
    access_timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'document_access_log'
        ordering = ['-access_timestamp']

    def __str__(self):
        return f"{self.document.document_name} - {self.access_type} by {self.accessed_by}"
