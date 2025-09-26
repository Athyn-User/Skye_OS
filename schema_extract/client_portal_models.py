# client_portal/models.py

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from applications.models import Company, Quote, Certificate
from claims.models import Claim
import uuid


class ClientProfile(models.Model):
    """Extended profile for client portal users"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='client_profile')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='client_users')
    
    # Contact preferences
    phone = models.CharField(max_length=20, blank=True)
    mobile_phone = models.CharField(max_length=20, blank=True)
    receive_emails = models.BooleanField(default=True)
    receive_sms = models.BooleanField(default=False)
    
    # Security
    portal_access_enabled = models.BooleanField(default=True)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    last_login_date = models.DateTimeField(null=True, blank=True)
    password_reset_token = models.CharField(max_length=100, blank=True)
    password_reset_date = models.DateTimeField(null=True, blank=True)
    
    # Additional info
    position = models.CharField(max_length=100, blank=True)
    department = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['company', 'user__last_name', 'user__first_name']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.company.company_name}"
    
    @property
    def can_view_claims(self):
        """Check if user has permission to view claims"""
        return self.portal_access_enabled
    
    @property
    def can_submit_claims(self):
        """Check if user has permission to submit claims"""
        return self.portal_access_enabled
    
    @property
    def can_make_payments(self):
        """Check if user has permission to make payments"""
        return self.portal_access_enabled


class ClientDocument(models.Model):
    """Documents available to clients in the portal"""
    DOCUMENT_TYPE = [
        ('POLICY', 'Policy Document'),
        ('CERTIFICATE', 'Certificate of Insurance'),
        ('INVOICE', 'Invoice'),
        ('RECEIPT', 'Payment Receipt'),
        ('CLAIM', 'Claim Document'),
        ('CORRESPONDENCE', 'Correspondence'),
        ('OTHER', 'Other'),
    ]
    
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='portal_documents')
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPE)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to='client_portal/documents/%Y/%m/')
    
    # Related records
    quote = models.ForeignKey(Quote, on_delete=models.SET_NULL, null=True, blank=True)
    certificate = models.ForeignKey(Certificate, on_delete=models.SET_NULL, null=True, blank=True)
    claim = models.ForeignKey(Claim, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Visibility
    is_visible = models.BooleanField(default=True)
    visible_from = models.DateField(null=True, blank=True)
    visible_until = models.DateField(null=True, blank=True)
    
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    uploaded_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-uploaded_date']
    
    def __str__(self):
        return f"{self.name} - {self.company.company_name}"
    
    def is_currently_visible(self):
        """Check if document should be visible based on date range"""
        today = timezone.now().date()
        if not self.is_visible:
            return False
        if self.visible_from and today < self.visible_from:
            return False
        if self.visible_until and today > self.visible_until:
            return False
        return True


class PaymentRequest(models.Model):
    """Payment requests visible in client portal"""
    PAYMENT_STATUS = [
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    PAYMENT_TYPE = [
        ('PREMIUM', 'Premium Payment'),
        ('DEDUCTIBLE', 'Deductible'),
        ('RENEWAL', 'Renewal'),
        ('ADDITIONAL', 'Additional Premium'),
        ('OTHER', 'Other'),
    ]
    
    request_id = models.CharField(max_length=50, unique=True, editable=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='payment_requests')
    quote = models.ForeignKey(Quote, on_delete=models.CASCADE, related_name='payment_requests')
    
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='PENDING')
    paid_date = models.DateTimeField(null=True, blank=True)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Payment details
    payment_method = models.CharField(max_length=50, blank=True)
    transaction_id = models.CharField(max_length=100, blank=True)
    payment_notes = models.TextField(blank=True)
    
    # Portal access
    show_in_portal = models.BooleanField(default=True)
    allow_online_payment = models.BooleanField(default=True)
    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['due_date', '-created_date']
    
    def __str__(self):
        return f"{self.request_id} - {self.company.company_name} - ${self.amount}"
    
    def save(self, *args, **kwargs):
        if not self.request_id:
            self.request_id = self.generate_request_id()
        super().save(*args, **kwargs)
    
    def generate_request_id(self):
        """Generate unique payment request ID"""
        year = timezone.now().year
        month = timezone.now().month
        
        # Get the latest request for this month
        latest = PaymentRequest.objects.filter(
            request_id__startswith=f'PAY{year}{month:02d}'
        ).order_by('-request_id').first()
        
        if latest:
            sequence = int(latest.request_id[-4:]) + 1
        else:
            sequence = 1
        
        return f'PAY{year}{month:02d}{sequence:04d}'
    
    @property
    def is_overdue(self):
        """Check if payment is overdue"""
        if self.status in ['COMPLETED', 'CANCELLED']:
            return False
        return timezone.now().date() > self.due_date


class ClientActivity(models.Model):
    """Track client portal activity for audit and analytics"""
    ACTIVITY_TYPE = [
        ('LOGIN', 'Login'),
        ('LOGOUT', 'Logout'),
        ('VIEW_POLICY', 'Viewed Policy'),
        ('VIEW_CERTIFICATE', 'Viewed Certificate'),
        ('VIEW_CLAIM', 'Viewed Claim'),
        ('SUBMIT_CLAIM', 'Submitted Claim'),
        ('DOWNLOAD_DOCUMENT', 'Downloaded Document'),
        ('UPDATE_PROFILE', 'Updated Profile'),
        ('MAKE_PAYMENT', 'Made Payment'),
        ('PASSWORD_RESET', 'Password Reset'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='portal_activities')
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPE)
    description = models.CharField(max_length=255)
    
    # Optional related objects
    quote = models.ForeignKey(Quote, on_delete=models.SET_NULL, null=True, blank=True)
    certificate = models.ForeignKey(Certificate, on_delete=models.SET_NULL, null=True, blank=True)
    claim = models.ForeignKey(Claim, on_delete=models.SET_NULL, null=True, blank=True)
    document = models.ForeignKey(ClientDocument, on_delete=models.SET_NULL, null=True, blank=True)
    
    ip_address = models.GenericIPAddressField()
    user_agent = models.CharField(max_length=255, blank=True)
    session_key = models.CharField(max_length=100, blank=True)
    
    created_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_date']
        verbose_name_plural = 'Client activities'
    
    def __str__(self):
        return f"{self.user} - {self.activity_type} - {self.created_date}"


class ClientMessage(models.Model):
    """Messages between clients and insurance company"""
    MESSAGE_STATUS = [
        ('UNREAD', 'Unread'),
        ('READ', 'Read'),
        ('REPLIED', 'Replied'),
        ('CLOSED', 'Closed'),
    ]
    
    MESSAGE_PRIORITY = [
        ('LOW', 'Low'),
        ('NORMAL', 'Normal'),
        ('HIGH', 'High'),
        ('URGENT', 'Urgent'),
    ]
    
    # Sender/Recipient
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_portal_messages')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_portal_messages', null=True, blank=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='portal_messages')
    
    # Message content
    subject = models.CharField(max_length=200)
    message = models.TextField()
    priority = models.CharField(max_length=10, choices=MESSAGE_PRIORITY, default='NORMAL')
    status = models.CharField(max_length=10, choices=MESSAGE_STATUS, default='UNREAD')
    
    # Related to
    quote = models.ForeignKey(Quote, on_delete=models.SET_NULL, null=True, blank=True)
    claim = models.ForeignKey(Claim, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Threading
    parent_message = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    
    # Timestamps
    sent_date = models.DateTimeField(auto_now_add=True)
    read_date = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-sent_date']
    
    def __str__(self):
        return f"{self.subject} - {self.from_user} to {self.to_user or 'Support'}"