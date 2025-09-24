# claims/models.py

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal
from django.utils import timezone
import uuid

# Import your existing models
from applications.models import Application, Quote, Certificate, Company

class Claim(models.Model):
    CLAIM_STATUS = [
        ('FNOL', 'First Notice of Loss'),
        ('ASSIGNED', 'Assigned to Adjuster'),
        ('INVESTIGATING', 'Under Investigation'),
        ('DOCUMENTING', 'Gathering Documentation'),
        ('REVIEWING', 'Under Review'),
        ('APPROVED', 'Approved'),
        ('DENIED', 'Denied'),
        ('SETTLED', 'Settled'),
        ('CLOSED', 'Closed'),
        ('REOPENED', 'Reopened'),
    ]
    
    CLAIM_TYPE = [
        ('PROPERTY', 'Property Damage'),
        ('LIABILITY', 'General Liability'),
        ('AUTO', 'Auto'),
        ('PROFESSIONAL', 'Professional Liability'),
        ('WORKERS_COMP', 'Workers Compensation'),
        ('CYBER', 'Cyber Liability'),
        ('OTHER', 'Other'),
    ]
    
    SEVERITY = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('CATASTROPHIC', 'Catastrophic'),
    ]
    
    # Claim Identification
    claim_number = models.CharField(max_length=20, unique=True, editable=False)
    claim_type = models.CharField(max_length=20, choices=CLAIM_TYPE)
    claim_status = models.CharField(max_length=20, choices=CLAIM_STATUS, default='FNOL')
    severity = models.CharField(max_length=20, choices=SEVERITY, default='MEDIUM')
    
    # Related Insurance Documents
    quote = models.ForeignKey(Quote, on_delete=models.PROTECT, related_name='claims')
    certificate = models.ForeignKey(Certificate, on_delete=models.PROTECT, null=True, blank=True, related_name='claims')
    
    # Claimant Information
    claimant_name = models.CharField(max_length=200)
    claimant_phone = models.CharField(max_length=20)
    claimant_email = models.EmailField()
    claimant_address = models.TextField()
    is_insured = models.BooleanField(default=True)
    
    # Loss Information
    date_of_loss = models.DateField()
    time_of_loss = models.TimeField(null=True, blank=True)
    location_of_loss = models.TextField()
    loss_description = models.TextField()
    cause_of_loss = models.CharField(max_length=200)
    
    # Financial Information
    estimated_loss = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0'))])
    deductible = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0'), validators=[MinValueValidator(Decimal('0'))])
    reserve_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0'), validators=[MinValueValidator(Decimal('0'))])
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0'), validators=[MinValueValidator(Decimal('0'))])
    recovered_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0'), validators=[MinValueValidator(Decimal('0'))])
    
    # Adjuster Assignment
    adjuster = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_claims')
    assigned_date = models.DateTimeField(null=True, blank=True)
    
    # Important Dates
    reported_date = models.DateTimeField(default=timezone.now)
    approved_date = models.DateTimeField(null=True, blank=True)
    settled_date = models.DateTimeField(null=True, blank=True)
    closed_date = models.DateTimeField(null=True, blank=True)
    reopened_date = models.DateTimeField(null=True, blank=True)
    
    # Additional Information
    police_report_number = models.CharField(max_length=50, blank=True)
    injuries_reported = models.BooleanField(default=False)
    property_damage = models.BooleanField(default=False)
    subrogation_possible = models.BooleanField(default=False)
    litigation_pending = models.BooleanField(default=False)
    
    # Internal Notes
    internal_notes = models.TextField(blank=True)
    denial_reason = models.TextField(blank=True)
    
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_claims')
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-reported_date']
        indexes = [
            models.Index(fields=['-reported_date']),
            models.Index(fields=['claim_status']),
            models.Index(fields=['adjuster']),
        ]
    
    def __str__(self):
        return f"{self.claim_number} - {self.claimant_name}"
    
    def save(self, *args, **kwargs):
        if not self.claim_number:
            self.claim_number = self.generate_claim_number()
        super().save(*args, **kwargs)
    
    def generate_claim_number(self):
        year = timezone.now().year
        # Get the latest claim number for this year
        latest = Claim.objects.filter(
            claim_number__startswith=f'CLM{year}'
        ).order_by('-claim_number').first()
        
        if latest:
            sequence = int(latest.claim_number[-5:]) + 1
        else:
            sequence = 1
        
        return f'CLM{year}{sequence:05d}'
    
    @property
    def net_paid(self):
        return self.paid_amount - self.recovered_amount
    
    @property
    def outstanding_reserve(self):
        return self.reserve_amount - self.paid_amount


class ClaimDocument(models.Model):
    DOCUMENT_TYPE = [
        ('FNOL', 'First Notice of Loss'),
        ('POLICE_REPORT', 'Police Report'),
        ('MEDICAL_REPORT', 'Medical Report'),
        ('INVOICE', 'Invoice/Receipt'),
        ('ESTIMATE', 'Repair Estimate'),
        ('PHOTO', 'Photograph'),
        ('CORRESPONDENCE', 'Correspondence'),
        ('LEGAL', 'Legal Document'),
        ('INVESTIGATION', 'Investigation Report'),
        ('OTHER', 'Other'),
    ]
    
    claim = models.ForeignKey(Claim, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPE)
    document_name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to='claims/documents/%Y/%m/')
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    uploaded_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-uploaded_date']
    
    def __str__(self):
        return f"{self.document_name} - {self.claim.claim_number}"


class ClaimNote(models.Model):
    NOTE_TYPE = [
        ('GENERAL', 'General Note'),
        ('PHONE', 'Phone Call'),
        ('EMAIL', 'Email'),
        ('MEETING', 'Meeting'),
        ('INVESTIGATION', 'Investigation'),
        ('LEGAL', 'Legal'),
        ('SETTLEMENT', 'Settlement'),
        ('INTERNAL', 'Internal'),
    ]
    
    claim = models.ForeignKey(Claim, on_delete=models.CASCADE, related_name='notes')
    note_type = models.CharField(max_length=20, choices=NOTE_TYPE, default='GENERAL')
    subject = models.CharField(max_length=200)
    content = models.TextField()
    is_public = models.BooleanField(default=False)  # Whether visible to client
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_date']
    
    def __str__(self):
        return f"{self.subject} - {self.claim.claim_number}"


class ClaimPayment(models.Model):
    PAYMENT_TYPE = [
        ('INDEMNITY', 'Indemnity'),
        ('MEDICAL', 'Medical'),
        ('EXPENSE', 'Expense'),
        ('LEGAL', 'Legal Fees'),
        ('DEDUCTIBLE', 'Deductible'),
        ('RECOVERY', 'Recovery/Subrogation'),
    ]
    
    PAYMENT_METHOD = [
        ('CHECK', 'Check'),
        ('ACH', 'ACH Transfer'),
        ('WIRE', 'Wire Transfer'),
        ('CREDIT_CARD', 'Credit Card'),
    ]
    
    claim = models.ForeignKey(Claim, on_delete=models.CASCADE, related_name='payments')
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD)
    payee_name = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    check_number = models.CharField(max_length=50, blank=True)
    payment_date = models.DateField()
    cleared_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='approved_payments')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_payments')
    created_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-payment_date']
    
    def __str__(self):
        return f"${self.amount} to {self.payee_name} - {self.claim.claim_number}"


class ClaimReserve(models.Model):
    RESERVE_TYPE = [
        ('INITIAL', 'Initial Reserve'),
        ('ADJUSTMENT', 'Reserve Adjustment'),
        ('SUPPLEMENTAL', 'Supplemental Reserve'),
    ]
    
    claim = models.ForeignKey(Claim, on_delete=models.CASCADE, related_name='reserves')
    reserve_type = models.CharField(max_length=20, choices=RESERVE_TYPE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    reason = models.TextField()
    effective_date = models.DateField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-effective_date', '-created_date']
    
    def __str__(self):
        return f"${self.amount} - {self.reserve_type} - {self.claim.claim_number}"