import os
import shutil
from datetime import datetime
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import User

class PortalDocumentManager(models.Manager):
    """Custom manager for portal documents"""
    
    def visible_to_client(self, company):
        """Get documents visible to client"""
        return self.filter(
            company=company,
            client_visible=True,
            status__in=['approved', 'uploaded', 'verified']
        )
    
    def all_for_company(self, company):
        """Get all documents for company (internal view)"""
        return self.filter(company=company)


class PortalDocument(models.Model):
    """Model for portal_documents table with dual storage"""
    
    DOCUMENT_TYPES = [
        ('loss_run', 'Loss Run'),
        ('application', 'Application'),
        ('financial', 'Financial Statement'),
        ('dec_page', 'Dec Page'),
        ('certificate', 'Certificate'),
        ('general', 'General'),
        ('claim', 'Claim Document'),
    ]
    
    STATUS_CHOICES = [
        ('uploaded', 'Uploaded'),
        ('verified', 'Verified'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    # Existing fields from database
    document_id = models.AutoField(primary_key=True)
    document_name = models.CharField(max_length=255)
    document_type = models.CharField(max_length=30, choices=DOCUMENT_TYPES)
    file = models.CharField(max_length=500)
    file_size = models.BigIntegerField(blank=True, null=True)
    file_type = models.CharField(max_length=50, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    internal_notes = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='uploaded')
    reviewed_date = models.DateTimeField(blank=True, null=True)
    rejection_reason = models.TextField(blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_verified = models.BooleanField(default=False)
    scan_status = models.CharField(max_length=20, blank=True, null=True)
    
    # Foreign keys
    application = models.ForeignKey('applications.Application', on_delete=models.SET_NULL, null=True, blank=True)
    claim = models.ForeignKey('claims.Claim', on_delete=models.SET_NULL, null=True, blank=True)
    company = models.ForeignKey('applications.Company', on_delete=models.CASCADE)
    policy = models.ForeignKey('applications.Policy', on_delete=models.SET_NULL, null=True, blank=True)
    quote = models.ForeignKey('applications.Quote', on_delete=models.SET_NULL, null=True, blank=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_portal_docs')
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='uploaded_portal_docs')
    
    # New dual storage fields
    client_visible = models.BooleanField(default=True)
    client_removed_date = models.DateTimeField(null=True, blank=True)
    client_removed_reason = models.TextField(blank=True, null=True)
    archive_path = models.CharField(max_length=500, null=True, blank=True)
    archive_created_date = models.DateTimeField(null=True, blank=True)
    original_file_path = models.CharField(max_length=500, null=True, blank=True)
    retention_period_days = models.IntegerField(default=2555)
    compliance_hold = models.BooleanField(default=False)
    permanent_record = models.BooleanField(default=True)
    
    objects = PortalDocumentManager()
    
    class Meta:
        managed = False
        db_table = 'portal_documents'
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.document_name} - {self.company}"
    
    def get_active_path(self):
        """Get path for client-visible file"""
        if self.original_file_path:
            return os.path.join(settings.MEDIA_ROOT, self.original_file_path)
        return os.path.join(settings.MEDIA_ROOT, self.file)
    
    def get_archive_path(self):
        """Get path for archive copy"""
        if self.archive_path:
            return os.path.join(settings.MEDIA_ROOT, self.archive_path)
        return None
    
    def remove_from_client_view(self, reason=''):
        """Soft delete - hide from client but keep archive"""
        self.client_visible = False
        self.client_removed_date = timezone.now()
        self.client_removed_reason = reason
        
        # Move file to removed folder
        if self.original_file_path:
            old_path = self.get_active_path()
            new_path = old_path.replace('\\active\\', '\\removed\\')
            
            if os.path.exists(old_path):
                os.makedirs(os.path.dirname(new_path), exist_ok=True)
                shutil.move(old_path, new_path)
                self.file = self.file.replace('/active/', '/removed/')
        
        self.save()
    
    def create_archive_copy(self):
        """Create permanent archive copy"""
        if not self.archive_path and self.file:
            source_path = self.get_active_path()
            
            # Build archive path
            date_part = datetime.now().strftime('%Y\\%m')
            archive_dir = f"company-archive\\company-{self.company_id}\\{date_part}"
            archive_full_dir = os.path.join(settings.MEDIA_ROOT, archive_dir)
            os.makedirs(archive_full_dir, exist_ok=True)
            
            # Copy file to archive
            filename = os.path.basename(self.file)
            archive_file_path = os.path.join(archive_dir, filename)
            archive_full_path = os.path.join(settings.MEDIA_ROOT, archive_file_path)
            
            if os.path.exists(source_path):
                shutil.copy2(source_path, archive_full_path)
                self.archive_path = archive_file_path
                self.archive_created_date = timezone.now()
                self.save()
