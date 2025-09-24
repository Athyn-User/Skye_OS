# File: applications/document_models.py
# Cloud-ready document management system for easy migration to GCP/Azure

from django.db import models
from django.conf import settings
from datetime import datetime
import os
import json

class DocumentTemplate(models.Model):
    """
    Master template repository for all document types
    Cloud-ready: Uses abstract storage paths instead of FileField
    """
    TEMPLATE_TYPES = [
        ('declaration', 'Declaration Page'),
        ('policy_form', 'Policy Form'),
        ('endorsement', 'Endorsement'),
        ('state_form', 'State Mandatory Form'),
        ('schedule', 'Schedule'),
        ('notice', 'Notice'),
        ('certificate', 'Certificate'),
    ]
    
    TEMPLATE_FORMATS = [
        ('dynamic', 'Dynamic (Generated)'),
        ('static', 'Static (PDF/Word)'),
        ('hybrid', 'Hybrid (Fillable)'),
    ]
    
    template_id = models.AutoField(primary_key=True)
    template_code = models.CharField(max_length=50, unique=True)  # e.g., "DEC-WCP-001", "END-ADD-INSURED"
    template_name = models.CharField(max_length=200)
    template_type = models.CharField(max_length=20, choices=TEMPLATE_TYPES)
    template_format = models.CharField(max_length=20, choices=TEMPLATE_FORMATS)
    
    # Product association
    product = models.ForeignKey('Product', on_delete=models.CASCADE, null=True, blank=True)
    
    # State-specific forms
    applicable_states = models.CharField(max_length=500, blank=True, null=True)  # Comma-separated state codes
    is_state_mandatory = models.BooleanField(default=False)
    
    # Template storage (cloud-agnostic)
    storage_path = models.CharField(max_length=500, blank=True, null=True)  # Path in storage bucket
    storage_bucket = models.CharField(max_length=100, default='default')  # Bucket/container name
    html_template = models.TextField(blank=True, null=True)  # For dynamic templates
    merge_fields = models.JSONField(default=dict, blank=True)  # Field mappings for variables
    
    # Metadata
    version = models.CharField(max_length=10, default='1.0')
    effective_date = models.DateField()
    expiration_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    # Sequencing
    default_sequence = models.IntegerField(default=100)  # Order in document package
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True)
    
    class Meta:
        db_table = 'document_templates'
        ordering = ['template_type', 'default_sequence', 'template_name']
        indexes = [
            models.Index(fields=['template_code']),
            models.Index(fields=['product', 'template_type']),
        ]
        
    def __str__(self):
        return f"{self.template_code} - {self.template_name}"
    
    def is_applicable_to_state(self, state_code):
        """Check if template applies to a given state"""
        if not self.applicable_states:
            return not self.is_state_mandatory
        return state_code.upper() in [s.strip().upper() for s in self.applicable_states.split(',')]
    
    def get_storage_url(self):
        """Get cloud storage URL - will work with GCS, Azure, or S3"""
        base_url = getattr(settings, 'DOCUMENT_STORAGE_URL', '/media/documents/')
        return f"{base_url}{self.storage_bucket}/{self.storage_path}"


class PolicyDocumentPackage(models.Model):
    """
    Complete document package for a policy
    """
    PACKAGE_STATUS = [
        ('draft', 'Draft'),
        ('generated', 'Generated'),
        ('issued', 'Issued'),
        ('reissued', 'Reissued'),
        ('superseded', 'Superseded'),
    ]
    
    package_id = models.AutoField(primary_key=True)
    policy = models.ForeignKey('Policy', on_delete=models.CASCADE, related_name='document_packages')
    
    # Package identification
    package_number = models.CharField(max_length=50, unique=True)  # e.g., "POL-WCP-000001-00-DOC-01"
    package_version = models.IntegerField(default=0)  # For reissued policies
    
    # Status tracking
    package_status = models.CharField(max_length=20, choices=PACKAGE_STATUS, default='draft')
    is_current = models.BooleanField(default=True)  # Most recent version
    
    # Generation details
    generated_date = models.DateTimeField(auto_now_add=True)
    issued_date = models.DateTimeField(null=True, blank=True)
    
    # Combined PDF storage (cloud-agnostic)
    combined_pdf_path = models.CharField(max_length=500, null=True, blank=True)
    combined_pdf_bucket = models.CharField(max_length=100, default='policy-packages')
    total_pages = models.IntegerField(default=0)
    file_size = models.BigIntegerField(default=0)  # In bytes
    
    # Metadata
    generation_data = models.JSONField(default=dict)  # Snapshot of data used for generation
    state_code = models.CharField(max_length=2, blank=True, null=True)  # For state-specific forms
    
    created_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True)
    
    class Meta:
        db_table = 'policy_document_packages'
        ordering = ['-package_version', '-generated_date']
        indexes = [
            models.Index(fields=['policy', 'is_current']),
            models.Index(fields=['package_status', 'generated_date']),
        ]
        
    def __str__(self):
        return f"{self.package_number} - {self.policy.policy_number}"
    
    def generate_package_number(self):
        """Generate package number with version for reissued policies"""
        base = self.policy.policy_number
        if self.package_version == 0:
            return f"{base}-DOC"
        else:
            # Reissued policy: POL-WCP-000001-00-01 (policy reissue version)
            return f"{base}-{self.package_version:02d}"
    
    def get_storage_url(self):
        """Get cloud storage URL for combined PDF"""
        base_url = getattr(settings, 'DOCUMENT_STORAGE_URL', '/media/documents/')
        return f"{base_url}{self.combined_pdf_bucket}/{self.combined_pdf_path}"


class DocumentComponent(models.Model):
    """
    Individual components within a document package
    """
    COMPONENT_STATUS = [
        ('pending', 'Pending Generation'),
        ('generated', 'Generated'),
        ('error', 'Generation Error'),
    ]
    
    component_id = models.AutoField(primary_key=True)
    package = models.ForeignKey(PolicyDocumentPackage, on_delete=models.CASCADE, related_name='components')
    template = models.ForeignKey(DocumentTemplate, on_delete=models.CASCADE, null=True, blank=True)
    
    # Component details
    component_type = models.CharField(max_length=20)  # declaration, form, endorsement, etc.
    component_name = models.CharField(max_length=200)
    sequence_order = models.IntegerField()  # Order within package
    
    # Generated file storage (cloud-agnostic)
    file_path = models.CharField(max_length=500, null=True, blank=True)
    file_bucket = models.CharField(max_length=100, default='policy-components')
    page_count = models.IntegerField(default=0)
    file_size = models.IntegerField(default=0)
    
    # Generation tracking
    component_status = models.CharField(max_length=20, choices=COMPONENT_STATUS, default='pending')
    component_data = models.JSONField(default=dict)  # Merged data for this component
    error_message = models.TextField(blank=True, null=True)
    
    # Pagination for standalone documents
    page_numbering = models.CharField(max_length=50, blank=True)  # e.g., "Page 1 of 10"
    
    generated_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'document_components'
        ordering = ['package', 'sequence_order']
        indexes = [
            models.Index(fields=['package', 'sequence_order']),
        ]
        
    def __str__(self):
        return f"{self.component_name} - {self.package.package_number}"
    
    def get_storage_url(self):
        """Get cloud storage URL for component"""
        base_url = getattr(settings, 'DOCUMENT_STORAGE_URL', '/media/documents/')
        return f"{base_url}{self.file_bucket}/{self.file_path}"


class EndorsementDocument(models.Model):
    """
    Specific endorsement documents linked to policy amendments
    """
    endorsement_id = models.AutoField(primary_key=True)
    policy = models.ForeignKey('Policy', on_delete=models.CASCADE, related_name='endorsements')
    template = models.ForeignKey(DocumentTemplate, on_delete=models.CASCADE)
    
    # Endorsement numbering: END-WCP-000001-01 (sequence for multiple endorsements)
    endorsement_number = models.CharField(max_length=50, unique=True)
    endorsement_sequence = models.IntegerField(default=1)
    
    # Endorsement details
    endorsement_title = models.CharField(max_length=200)
    effective_date = models.DateField()
    
    # Document storage (cloud-agnostic)
    document_path = models.CharField(max_length=500, null=True, blank=True)
    document_bucket = models.CharField(max_length=100, default='endorsements')
    
    # Variable data for the endorsement
    endorsement_data = models.JSONField(default=dict)
    
    # Link to policy amendment if applicable
    policy_transaction = models.ForeignKey('PolicyTransaction', on_delete=models.SET_NULL, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True)
    
    class Meta:
        db_table = 'endorsement_documents'
        ordering = ['policy', 'endorsement_sequence']
        indexes = [
            models.Index(fields=['policy', 'effective_date']),
        ]
        
    def __str__(self):
        return f"{self.endorsement_number} - {self.endorsement_title}"
    
    def generate_endorsement_number(self):
        """Generate endorsement number with sequence"""
        base = self.policy.policy_number.replace('POL', 'END')
        return f"{base}-{self.endorsement_sequence:02d}"
    
    def get_storage_url(self):
        """Get cloud storage URL for endorsement"""
        base_url = getattr(settings, 'DOCUMENT_STORAGE_URL', '/media/documents/')
        return f"{base_url}{self.document_bucket}/{self.document_path}"


class DocumentDelivery(models.Model):
    """
    Track document delivery to customers
    """
    DELIVERY_METHODS = [
        ('email', 'Email'),
        ('portal', 'Customer Portal'),
        ('download', 'Direct Download'),
        ('print', 'Printed'),
    ]
    
    DELIVERY_STATUS = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('viewed', 'Viewed'),
        ('failed', 'Failed'),
    ]
    
    delivery_id = models.AutoField(primary_key=True)
    package = models.ForeignKey(PolicyDocumentPackage, on_delete=models.CASCADE, null=True, blank=True)
    endorsement = models.ForeignKey(EndorsementDocument, on_delete=models.CASCADE, null=True, blank=True)
    
    # Delivery details
    delivery_method = models.CharField(max_length=20, choices=DELIVERY_METHODS)
    delivery_status = models.CharField(max_length=20, choices=DELIVERY_STATUS, default='pending')
    recipient_email = models.EmailField(blank=True, null=True)
    
    # Tracking
    sent_date = models.DateTimeField(null=True, blank=True)
    delivered_date = models.DateTimeField(null=True, blank=True)
    viewed_date = models.DateTimeField(null=True, blank=True)
    
    # Portal access
    portal_access_token = models.CharField(max_length=100, blank=True, null=True, unique=True)
    portal_access_expires = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    delivery_metadata = models.JSONField(default=dict)  # Email tracking, etc.
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'document_deliveries'
        indexes = [
            models.Index(fields=['delivery_status', 'created_at']),
            models.Index(fields=['portal_access_token']),
        ]
        
    def __str__(self):
        doc = self.package or self.endorsement
        return f"{self.get_delivery_method_display()} - {doc}"