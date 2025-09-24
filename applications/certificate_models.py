from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid

class CertificateTemplate(models.Model):
    TEMPLATE_TYPES = [
        ('standard', 'Standard Certificate'),
        ('contractor', 'Contractor Certificate'),
        ('vendor', 'Vendor Certificate'),
        ('tenant', 'Tenant Certificate'),
        ('auto', 'Auto Certificate'),
        ('workers_comp', 'Workers Compensation Certificate'),
        ('professional', 'Professional Liability Certificate'),
    ]
    
    template_id = models.AutoField(primary_key=True)
    template_name = models.CharField(max_length=100)
    template_type = models.CharField(max_length=20, choices=TEMPLATE_TYPES)
    description = models.TextField(blank=True, null=True)
    template_content = models.TextField(help_text='HTML template content')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        db_table = 'certificate_templates'

    def __str__(self):
        return f'{self.template_name} ({self.get_template_type_display()})'


class Certificate(models.Model):
    CERTIFICATE_STATUS = [
        ('draft', 'Draft'),
        ('issued', 'Issued'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired'),
        ('revised', 'Revised'),
    ]
    
    certificate_id = models.AutoField(primary_key=True)
    certificate_number = models.CharField(max_length=50, unique=True, blank=True)
    
    # Relations (adjust based on your existing models)
    quote_id = models.IntegerField(null=True, blank=True)
    policy_id = models.IntegerField(null=True, blank=True)
    template = models.ForeignKey(CertificateTemplate, on_delete=models.CASCADE)
    
    # Certificate holder information
    certificate_holder_name = models.CharField(max_length=255)
    certificate_holder_address_line1 = models.CharField(max_length=255)
    certificate_holder_address_line2 = models.CharField(max_length=255, blank=True, null=True)
    certificate_holder_city = models.CharField(max_length=100)
    certificate_holder_state = models.CharField(max_length=50)
    certificate_holder_zip_code = models.CharField(max_length=20)
    
    # Insured information
    insured_name = models.CharField(max_length=255)
    insured_address_line1 = models.CharField(max_length=255)
    insured_address_line2 = models.CharField(max_length=255, blank=True, null=True)
    insured_city = models.CharField(max_length=100)
    insured_state = models.CharField(max_length=50)
    insured_zip_code = models.CharField(max_length=20)
    
    # Certificate details
    status = models.CharField(max_length=20, choices=CERTIFICATE_STATUS, default='draft')
    issue_date = models.DateField(default=timezone.now)
    effective_date = models.DateField()
    expiration_date = models.DateField()
    description_of_operations = models.TextField(blank=True, null=True)
    
    # Additional insured information
    additional_insured = models.TextField(blank=True, null=True)
    special_provisions = models.TextField(blank=True, null=True)
    
    # Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    issued_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='issued_certificates')

    class Meta:
        db_table = 'certificates'

    def __str__(self):
        return f'Certificate {self.certificate_number} - {self.certificate_holder_name}'

    def save(self, *args, **kwargs):
        if not self.certificate_number:
            self.certificate_number = f'CERT-{uuid.uuid4().hex[:8].upper()}'
        super().save(*args, **kwargs)


class CertificateCoverage(models.Model):
    COVERAGE_TYPES = [
        ('general_liability', 'General Liability'),
        ('auto_liability', 'Automobile Liability'),
        ('workers_comp', 'Workers Compensation'),
        ('professional', 'Professional Liability'),
        ('property', 'Property Insurance'),
        ('umbrella', 'Umbrella/Excess Liability'),
    ]
    
    coverage_id = models.AutoField(primary_key=True)
    certificate = models.ForeignKey(Certificate, on_delete=models.CASCADE, related_name='coverages')
    coverage_type = models.CharField(max_length=50, choices=COVERAGE_TYPES)
    
    # Policy information
    policy_number = models.CharField(max_length=100)
    policy_effective_date = models.DateField()
    policy_expiration_date = models.DateField()
    
    # Limits
    each_occurrence = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    general_aggregate = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    products_aggregate = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    combined_single_limit = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    bodily_injury_per_person = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    bodily_injury_per_accident = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    property_damage = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    
    # Deductibles
    deductible = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    
    # Additional fields
    waiver_of_subrogation = models.BooleanField(default=False)
    additional_insured = models.BooleanField(default=False)
    primary_non_contributory = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'certificate_coverages'

    def __str__(self):
        return f'{self.get_coverage_type_display()} - {self.policy_number}'

