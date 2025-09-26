# Path: applications/additional_insured_models.py
# Models for managing additional insureds on policies

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal

class AdditionalInsured(models.Model):
    """Represents an additional insured entity on a policy"""
    
    AI_TYPE_CHOICES = [
        ('landlord', 'Landlord'),
        ('vendor', 'Vendor'),
        ('lender', 'Lender/Mortgagee'),
        ('general_contractor', 'General Contractor'),
        ('other', 'Other'),
    ]
    
    CERTIFICATE_FREQUENCY_CHOICES = [
        ('none', 'Not Required'),
        ('one_time', 'One-Time'),
        ('annual', 'Annual'),
        ('per_project', 'Per Project'),
    ]
    
    # Primary Keys and Relationships
    additional_insured_id = models.AutoField(primary_key=True)
    policy = models.ForeignKey('Policy', on_delete=models.CASCADE, related_name='additional_insureds')
    
    # Unique Identifier
    ai_number = models.CharField(
        max_length=10,
        help_text="Unique identifier (e.g., AI-001)"
    )
    
    # Basic Information
    ai_type = models.CharField(
        max_length=20,
        choices=AI_TYPE_CHOICES,
        default='vendor'
    )
    name = models.CharField(max_length=200)
    
    # Address Information
    address_line_1 = models.CharField(max_length=200)
    address_line_2 = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=2)
    zip_code = models.CharField(max_length=10)
    
    # Contact Information
    contact_name = models.CharField(max_length=100, blank=True)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)
    
    # Certificate Requirements
    certificate_required = models.BooleanField(default=True)
    certificate_frequency = models.CharField(
        max_length=20,
        choices=CERTIFICATE_FREQUENCY_CHOICES,
        default='annual'
    )
    
    # Coverage Types
    coverage_gl = models.BooleanField(
        default=False,
        verbose_name="General Liability"
    )
    coverage_auto = models.BooleanField(
        default=False,
        verbose_name="Auto Liability"
    )
    coverage_property = models.BooleanField(
        default=False,
        verbose_name="Property"
    )
    coverage_umbrella = models.BooleanField(
        default=False,
        verbose_name="Umbrella/Excess"
    )
    
    # Additional Requirements
    waiver_of_subrogation = models.BooleanField(default=False)
    primary_non_contributory = models.BooleanField(default=False)
    additional_requirements = models.TextField(blank=True)
    
    # Dates
    effective_date = models.DateField()
    expiration_date = models.DateField(null=True, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Audit Fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='additional_insureds_created'
    )
    
    class Meta:
        ordering = ['ai_number']
        unique_together = ['policy', 'ai_number']
        indexes = [
            models.Index(fields=['policy', 'is_active']),
            models.Index(fields=['policy', 'ai_type']),
        ]
    
    def __str__(self):
        return f"{self.ai_number}: {self.name} ({self.get_ai_type_display()})"
    
    @property
    def full_address(self):
        """Return complete formatted address"""
        lines = [self.address_line_1]
        if self.address_line_2:
            lines.append(self.address_line_2)
        lines.append(f"{self.city}, {self.state} {self.zip_code}")
        return '\n'.join(lines)
    
    @property
    def coverage_types_list(self):
        """Return list of coverage types required"""
        coverages = []
        if self.coverage_gl:
            coverages.append('GL')
        if self.coverage_auto:
            coverages.append('Auto')
        if self.coverage_property:
            coverages.append('Property')
        if self.coverage_umbrella:
            coverages.append('Umbrella')
        return coverages
    
    def get_latest_certificate(self):
        """Get the most recent certificate for this AI"""
        return self.certificates.filter(
            certificate__certificate_status='issued'
        ).order_by('-issued_date').first()


class AdditionalInsuredCertificate(models.Model):
    """Links additional insureds to certificates (1:1 relationship)"""
    
    ai_certificate_id = models.AutoField(primary_key=True)
    additional_insured = models.ForeignKey(
        AdditionalInsured,
        on_delete=models.CASCADE,
        related_name='certificates'
    )
    certificate = models.ForeignKey(
        'Certificate',
        on_delete=models.CASCADE,
        related_name='additional_insured_cert'
    )
    
    # Certificate Details
    issued_date = models.DateField(auto_now_add=True)
    expiration_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    
    # Audit
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    class Meta:
        ordering = ['-issued_date']
        # Ensure one AI has only one active certificate at a time
        unique_together = ['additional_insured', 'certificate']
    
    def __str__(self):
        return f"Certificate for {self.additional_insured.name} - {self.issued_date}"


class AdditionalInsuredSchedule(models.Model):
    """Groups additional insureds for bulk operations"""
    
    SCHEDULE_TYPE_CHOICES = [
        ('all', 'All Additional Insureds'),
        ('by_type', 'By Type'),
        ('selected', 'Selected AIs'),
        ('certificate_required', 'Certificate Required Only'),
    ]
    
    schedule_id = models.AutoField(primary_key=True)
    policy = models.ForeignKey('Policy', on_delete=models.CASCADE, related_name='ai_schedules')
    
    # Schedule Information
    schedule_name = models.CharField(max_length=200)
    schedule_type = models.CharField(
        max_length=30,
        choices=SCHEDULE_TYPE_CHOICES,
        default='all'
    )
    
    # Filter Criteria
    filter_types = models.CharField(
        max_length=200,
        blank=True,
        help_text="Comma-separated AI types"
    )
    
    # Related AIs
    additional_insureds = models.ManyToManyField(
        AdditionalInsured,
        related_name='schedules'
    )
    
    # Totals
    total_ais = models.IntegerField(default=0)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    class Meta:
        ordering = ['schedule_name']
    
    def __str__(self):
        return f"{self.schedule_name} ({self.total_ais} AIs)"
    
    def calculate_totals(self):
        """Update the count of AIs in this schedule"""
        self.total_ais = self.additional_insureds.filter(is_active=True).count()
        self.save(update_fields=['total_ais'])
    
    def add_ais_by_criteria(self):
        """Add AIs based on schedule criteria"""
        ais = self.policy.additional_insureds.filter(is_active=True)
        
        if self.schedule_type == 'all':
            self.additional_insureds.set(ais)
        elif self.schedule_type == 'by_type' and self.filter_types:
            types = [t.strip() for t in self.filter_types.split(',')]
            filtered = ais.filter(ai_type__in=types)
            self.additional_insureds.set(filtered)
        elif self.schedule_type == 'certificate_required':
            filtered = ais.filter(certificate_required=True)
            self.additional_insureds.set(filtered)
        
        self.calculate_totals()