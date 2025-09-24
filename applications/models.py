# File: applications/models.py
# Complete updated file with Quote class added and 6-digit numbering

from django.db import models
from datetime import date
from django.contrib.auth.models import User
import uuid

class Company(models.Model):
    company_id = models.AutoField(primary_key=True)
    company_name = models.TextField()
    dba_name = models.TextField(blank=True, null=True)
    tax_id = models.TextField(blank=True, null=True)
    company_type = models.TextField(blank=True, null=True)
    industry_code = models.TextField(blank=True, null=True)
    industry_description = models.TextField(blank=True, null=True)
    annual_revenue = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    employee_count = models.IntegerField(blank=True, null=True)
    website = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'companies'
        verbose_name_plural = 'Companies'

    def __str__(self):
        return self.company_name

class Broker(models.Model):
    broker_id = models.AutoField(primary_key=True)
    broker_name = models.TextField()
    broker_code = models.TextField(unique=True, blank=True, null=True)
    broker_type = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'brokers'

    def __str__(self):
        return self.broker_name

class Product(models.Model):
    product_id = models.AutoField(primary_key=True)
    venture_id = models.IntegerField(null=True, blank=True)
    coverage_type_id = models.IntegerField(null=True, blank=True)
    product_name = models.TextField()
    product_code = models.TextField(unique=True)
    document_code = models.CharField(max_length=3, blank=True, null=True)  # 3-char codes
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'products'

    def __str__(self):
        return self.product_name

class Application(models.Model):
    STATUS_CHOICES = [
        ('received', 'Received'),
        ('in_progress', 'In Progress'),
        ('quoted', 'Quoted'),
        ('bound', 'Bound'),
        ('declined', 'Declined'),
        ('expired', 'Expired'),
        ('withdrawn', 'Withdrawn'),
    ]

    application_id = models.AutoField(primary_key=True)
    application_number = models.TextField(unique=True, blank=True, null=True)
    
    # Fields for structured numbering (6-digit base)
    base_number = models.CharField(max_length=6, blank=True, null=True)  # "000001"
    sequence_number = models.IntegerField(default=0)  # 0 for original
    version_number = models.IntegerField(blank=True, null=True)  # null for original, 1+ for revisions
    parent_application = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='revisions')
    
    company = models.ForeignKey(Company, on_delete=models.CASCADE, db_column='company_id')
    broker = models.ForeignKey(Broker, on_delete=models.CASCADE, blank=True, null=True, db_column='broker_id')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, db_column='product_id')
    submission_date = models.DateField(auto_now_add=True)
    target_effective_date = models.DateField(blank=True, null=True)
    application_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='received')
    estimated_premium = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    quoted_premium = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    bound_premium = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    underwriting_notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'applications'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.application_number or 'APP-TBD'} - {self.company.company_name}"
    
    def get_display_number(self):
        """Generate the display number with proper formatting"""
        if not self.base_number:
            return self.application_number or 'APP-TBD'
        
        product_code = self.product.document_code or 'GEN'
        number = f"APP-{product_code}-{self.base_number}-{self.sequence_number:02d}"
        
        if self.version_number:
            number += f"-{self.version_number:02d}"
        
        return number
    
    def save(self, *args, **kwargs):
        """Override save to handle number generation"""
        from .number_generator import NumberGenerator
        
        # Check if this is a new application (no application_id yet)
        is_new = self.application_id is None
        
        # Generate number for new applications
        if is_new and not self.application_number:
            # Generate the application number
            number, base = NumberGenerator.generate_application_number(
                product=self.product,
                sequence_number=self.sequence_number,
                version_number=self.version_number
            )
            self.application_number = number
            self.base_number = base
            
            # Confirm the number after successful save
            product_code = self.product.document_code or 'GEN'
            super().save(*args, **kwargs)
            NumberGenerator.confirm_number(product_code, base)
        else:
            # Update the application_number if components changed
            if self.base_number:
                self.application_number = self.get_display_number()
            
            super().save(*args, **kwargs)

class Quote(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('presented', 'Presented'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
        ('expired', 'Expired'),
        ('superseded', 'Superseded'),
    ]

    quote_id = models.AutoField(primary_key=True)
    application = models.ForeignKey(Application, on_delete=models.CASCADE, db_column='application_id')
    quote_number = models.TextField(unique=True, blank=True, null=True)
    
    # Fields for structured numbering (6-digit)
    base_number = models.CharField(max_length=6, blank=True, null=True)  # "000001"
    sequence_number = models.IntegerField(default=0)  # 0 for original
    version_number = models.IntegerField(blank=True, null=True)  # null for original, 1+ for revisions
    parent_quote = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='revisions')
    
    quote_version = models.IntegerField(default=1)  # Keep for backward compatibility
    quote_date = models.DateField(auto_now_add=True)
    effective_date = models.DateField()
    expiration_date = models.DateField()
    quote_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    total_premium = models.DecimalField(max_digits=12, decimal_places=2)
    commission_amount = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    special_conditions = models.TextField(blank=True, null=True)
    
    # Track if this quote has been sent to customer (for auto-versioning)
    presented_to_customer = models.BooleanField(default=False)
    presented_date = models.DateTimeField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'quotes'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.quote_number or 'QTE-TBD'} - {self.application.company.company_name}"
    
    def get_display_number(self):
        """Generate the display number with proper formatting"""
        if not self.base_number:
            return self.quote_number or 'QTE-TBD'
        
        product_code = self.application.product.document_code or 'GEN'
        number = f"QTE-{product_code}-{self.base_number}-{self.sequence_number:02d}"
        
        if self.version_number:
            number += f"-{self.version_number:02d}"
        
        return number
    
    def needs_new_version(self):
        """Check if changes require a new version"""
        return self.presented_to_customer and self.quote_status == 'draft'
    
    def save(self, *args, **kwargs):
        """Override save to handle number generation and versioning"""
        from .number_generator import NumberGenerator
        from django.utils import timezone
        
        # Check if this is a new quote (no quote_id yet)
        is_new = self.quote_id is None
        
        # Check if we need to create a new version
        if not is_new and self.presented_to_customer:
            # Check if significant fields have changed
            original = Quote.objects.get(quote_id=self.quote_id)
            
            # If premium or status changed after presentation, create new version
            if (original.total_premium != self.total_premium or 
                original.quote_status != self.quote_status) and original.presented_to_customer:
                
                # Create a new version instead of updating
                new_version = self.create_version()
                return new_version
        
        # Generate number for new quotes
        if is_new and not self.quote_number:
            # Check if this is a subsequent quote for the same application
            existing_quotes = Quote.objects.filter(
                application=self.application,
                base_number__isnull=False
            ).order_by('-version_number', '-quote_id')
            
            if existing_quotes.exists():
                # This is a subsequent quote - create as a version
                latest_quote = existing_quotes.first()
                self.base_number = latest_quote.base_number
                self.sequence_number = latest_quote.sequence_number
                
                # Determine version number
                max_version = existing_quotes.aggregate(
                    max_v=models.Max('version_number')
                )['max_v']
                self.version_number = (max_version or 0) + 1
                
                # Generate the quote number with version
                product_code = self.application.product.document_code or 'GEN'
                self.quote_number = f"QTE-{product_code}-{self.base_number}-{self.sequence_number:02d}-{self.version_number:02d}"
            else:
                # First quote for this application - inherit base from application
                if self.application.base_number:
                    # Inherit from application
                    self.base_number = self.application.base_number
                    number = f"QTE-{self.application.product.document_code or 'GEN'}-{self.base_number}-{self.sequence_number:02d}"
                else:
                    # Generate new (for legacy applications without numbers)
                    number, base = NumberGenerator.generate_quote_number(
                        application=self.application,
                        sequence_number=self.sequence_number,
                        version_number=self.version_number
                    )
                    self.base_number = base
                    number = number
                
                self.quote_number = number
                
                # Only confirm number if we generated a new one
                if not self.application.base_number:
                    product_code = self.application.product.document_code or 'GEN'
                    NumberGenerator.confirm_number(product_code, self.base_number)
            
            super().save(*args, **kwargs)
        else:
            # Update the quote_number if components changed
            if self.base_number:
                self.quote_number = self.get_display_number()
            
            # Track presentation status
            if self.quote_status == 'presented' and not self.presented_to_customer:
                self.presented_to_customer = True
                self.presented_date = timezone.now()
            
            super().save(*args, **kwargs)
    
    def create_version(self):
        """Create a new version of this quote"""
        from .number_generator import NumberGenerator
        from django.utils import timezone
        
        # Mark this quote as superseded
        self.quote_status = 'superseded'
        super().save(update_fields=['quote_status'])
        
        # Get the next version number
        new_version_number = NumberGenerator.create_quote_version(self)
        
        # Create new quote with same base but new version
        new_quote = Quote.objects.create(
            application=self.application,
            base_number=self.base_number,
            sequence_number=self.sequence_number,
            version_number=new_version_number,
            parent_quote=self,
            quote_version=self.quote_version + 1,  # Legacy field
            effective_date=self.effective_date,
            expiration_date=self.expiration_date,
            quote_status='draft',
            total_premium=self.total_premium,
            commission_amount=self.commission_amount,
            special_conditions=self.special_conditions,
            presented_to_customer=False,
            presented_date=None
        )
        
        # Generate the quote number
        product_code = self.application.product.document_code or 'GEN'
        new_quote.quote_number = f"QTE-{product_code}-{self.base_number}-{self.sequence_number:02d}-{new_version_number:02d}"
        new_quote.save(update_fields=['quote_number'])
        
        return new_quote

class CertificateTemplate(models.Model):
    TEMPLATE_TYPES = [
        ('standard', 'Standard Certificate'),
        ('contractor', 'Contractor Certificate'),
        ('vendor', 'Vendor Certificate'),
        ('tenant', 'Tenant Certificate'),
        ('auto', 'Auto Certificate'),
    ]
    
    template_id = models.AutoField(primary_key=True)
    template_name = models.CharField(max_length=100)
    template_type = models.CharField(max_length=20, choices=TEMPLATE_TYPES)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'certificate_templates'

    def __str__(self):
        return self.template_name

class Certificate(models.Model):
    CERTIFICATE_STATUS = [
        ('draft', 'Draft'),
        ('issued', 'Issued'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired'),
    ]
    
    certificate_id = models.AutoField(primary_key=True)
    certificate_number = models.CharField(max_length=50, unique=True, blank=True, null=True)
    quote = models.ForeignKey(Quote, on_delete=models.CASCADE, db_column='quote_id')
    template = models.ForeignKey(CertificateTemplate, on_delete=models.CASCADE, db_column='template_id')
    
    # Certificate holder information
    certificate_holder_name = models.CharField(max_length=255)
    certificate_holder_address = models.TextField()
    
    # Additional insured information
    additional_insured_name = models.CharField(max_length=255, blank=True, null=True)
    additional_insured_address = models.TextField(blank=True, null=True)
    
    # Project/contract information
    project_description = models.TextField(blank=True, null=True)
    project_location = models.TextField(blank=True, null=True)
    
    # Certificate details
    effective_date = models.DateField()
    expiration_date = models.DateField()
    certificate_status = models.CharField(max_length=20, choices=CERTIFICATE_STATUS, default='draft')
    
    # Special provisions
    special_provisions = models.TextField(blank=True, null=True)
    waiver_of_subrogation = models.BooleanField(default=False)
    primary_and_noncontributory = models.BooleanField(default=False)
    
    # Audit trail
    issued_date = models.DateTimeField(blank=True, null=True)
        
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'certificates'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.certificate_number} - {self.certificate_holder_name}"

    def save(self, *args, **kwargs):
        if not self.certificate_number:
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT nextval('certificate_number_seq')")
                seq_value = cursor.fetchone()[0]
            self.certificate_number = f"CERT-{self.effective_date.year}-{seq_value:06d}"
        super().save(*args, **kwargs)

class CertificateCoverage(models.Model):
    COVERAGE_TYPES = [
        ('general_liability', 'General Liability'),
        ('auto_liability', 'Automobile Liability'),
        ('excess_umbrella', 'Excess/Umbrella Liability'),
        ('workers_comp', 'Workers Compensation'),
        ('property', 'Property'),
        ('professional', 'Professional Liability'),
        ('cyber', 'Cyber Liability'),
        ('other', 'Other'),
    ]
    
    coverage_id = models.AutoField(primary_key=True)
    certificate = models.ForeignKey(Certificate, on_delete=models.CASCADE, db_column='certificate_id')
    coverage_type = models.CharField(max_length=30, choices=COVERAGE_TYPES)
    
    # Coverage limits
    each_occurrence = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    general_aggregate = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    products_completed_ops = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    personal_advertising_injury = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    
    # Deductibles
    deductible = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    
    # Policy information
    policy_number = models.CharField(max_length=50, blank=True, null=True)
    policy_effective_date = models.DateField()
    policy_expiration_date = models.DateField()
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'certificate_coverages'

    def __str__(self):
        return f"{self.get_coverage_type_display()} - {self.certificate.certificate_number}"

class Policy(models.Model):
    POLICY_STATUS_CHOICES = [
        ('active', 'Active'),
        ('pending', 'Pending'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired'),
        ('non_renewed', 'Non-Renewed'),
        ('suspended', 'Suspended'),
    ]
    
    BILLING_FREQUENCY_CHOICES = [
        ('annual', 'Annual'),
        ('semi_annual', 'Semi-Annual'),
        ('quarterly', 'Quarterly'),
        ('monthly', 'Monthly'),
    ]
    
    policy_id = models.AutoField(primary_key=True)
    policy_number = models.CharField(max_length=50, unique=True)
    quote = models.ForeignKey(Quote, on_delete=models.CASCADE)
    
    # Fields for structured numbering (6-digit)
    base_number = models.CharField(max_length=6, blank=True, null=True)  # "000001" - UPDATED TO 6
    sequence_number = models.IntegerField(default=0)  # 0 for original, 1+ for renewals
    version_number = models.IntegerField(blank=True, null=True)  # null for original, 1+ for revisions
    parent_policy = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='renewals_chain')
    original_policy = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='all_renewals')
    
    # Policy dates
    effective_date = models.DateField()
    expiration_date = models.DateField()
    issue_date = models.DateField(auto_now_add=True)
    
    # Financial details
    annual_premium = models.DecimalField(max_digits=12, decimal_places=2)
    billing_frequency = models.CharField(max_length=20, choices=BILLING_FREQUENCY_CHOICES, default='annual')
    
    # Status tracking
    policy_status = models.CharField(max_length=20, choices=POLICY_STATUS_CHOICES, default='pending')
    
    # Renewal tracking
    renewal_date = models.DateField(null=True, blank=True)
    auto_renewal = models.BooleanField(default=True)
    renewal_notice_sent = models.BooleanField(default=False)
    
    # Track if policy has been issued (for auto-versioning)
    issued_to_customer = models.BooleanField(default=False)
    issued_date = models.DateTimeField(blank=True, null=True)
    
    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        db_table = 'policies'
        verbose_name = 'Policy'
        verbose_name_plural = 'Policies'
    
    def __str__(self):
        return f'{self.policy_number} - {self.quote.application.company.company_name}'
    
    def get_display_number(self):
        """Generate the display number with proper formatting"""
        if not self.base_number:
            return self.policy_number or 'POL-TBD'
        
        product_code = self.quote.application.product.document_code or 'XXX'
        number = f"POL-{product_code}-{self.base_number}-{self.sequence_number:02d}"
        
        if self.version_number:
            number += f"-{self.version_number:02d}"
        
        return number
    
    def save(self, *args, **kwargs):
        """Override save to handle number generation and versioning"""
        from .number_generator import NumberGenerator
        from django.utils import timezone
        
        # Check if this is a new policy
        is_new = self.policy_id is None
        
        # Generate policy number for new policies
        if is_new and not self.policy_number:
            # If we have a base_number, use it to generate the number
            if self.base_number:
                product_code = self.quote.application.product.document_code or 'GEN'
                # Generate base policy number WITHOUT version
                self.policy_number = f"POL-{product_code}-{self.base_number}-{self.sequence_number:02d}"
                
                # Only add version suffix if this is an amendment
                if self.version_number:
                    self.policy_number += f"-{self.version_number:02d}"
        
        # Handle renewal date
        if not self.renewal_date and self.expiration_date:
            from datetime import timedelta
            self.renewal_date = self.expiration_date - timedelta(days=60)
        
        # Track if policy has been issued
        if self.policy_status == 'active' and not self.issued_to_customer:
            self.issued_to_customer = True
            self.issued_date = timezone.now()
        
        super().save(*args, **kwargs)
    
    def create_amendment(self, description="Policy Amendment"):
        """Create an amended version of this policy"""
        from .number_generator import NumberGenerator
        from django.utils import timezone
        
        # Find the highest version number for this policy
        existing_versions = Policy.objects.filter(
            base_number=self.base_number,
            sequence_number=self.sequence_number
        ).exclude(
            policy_id=self.policy_id
        ).aggregate(
            max_version=models.Max('version_number')
        )['max_version']
        
        # Determine the new version number
        if existing_versions is None:
            new_version_number = 1 if self.version_number is None else self.version_number + 1
        else:
            new_version_number = existing_versions + 1
        
        # Create the amended policy
        product_code = self.quote.application.product.document_code or 'GEN'
        amended_policy = Policy.objects.create(
            quote=self.quote,
            policy_number=f"POL-{product_code}-{self.base_number}-{self.sequence_number:02d}-{new_version_number:02d}",
            base_number=self.base_number,
            sequence_number=self.sequence_number,
            version_number=new_version_number,
            parent_policy=self,
            original_policy=self.original_policy or self,
            effective_date=self.effective_date,
            expiration_date=self.expiration_date,
            annual_premium=self.annual_premium,
            billing_frequency=self.billing_frequency,
            policy_status='pending',  # Amendment starts as pending
            auto_renewal=self.auto_renewal,
            created_by=self.created_by
        )
        
        # Create a transaction record for the amendment
        from .models import PolicyTransaction
        PolicyTransaction.objects.create(
            policy=amended_policy,
            transaction_type='endorsement',
            effective_date=timezone.now().date(),
            premium_change=0,  # Will be updated when amendment is finalized
            description=description,
            processed_by=self.created_by
        )
        
        return amended_policy

class PolicyTransaction(models.Model):
    TRANSACTION_TYPES = [
        ('new_business', 'New Business'),
        ('renewal', 'Renewal'),
        ('endorsement', 'Endorsement'),
        ('cancellation', 'Cancellation'),
        ('reinstatement', 'Reinstatement'),
    ]
    
    transaction_id = models.AutoField(primary_key=True)
    policy = models.ForeignKey(Policy, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    transaction_date = models.DateTimeField(auto_now_add=True)
    effective_date = models.DateField()
    premium_change = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    description = models.TextField()
    processed_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True)
    
    class Meta:
        db_table = 'policy_transactions'
        
    def __str__(self):
        return f'{self.policy.policy_number} - {self.get_transaction_type_display()}'

class PolicyRenewal(models.Model):
    RENEWAL_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('quoted', 'Quoted'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
        ('non_renewed', 'Non-Renewed'),
    ]
    
    renewal_id = models.AutoField(primary_key=True)
    original_policy = models.ForeignKey(Policy, on_delete=models.CASCADE, related_name='renewals')
    renewal_quote = models.ForeignKey(Quote, on_delete=models.CASCADE, null=True, blank=True)
    renewal_policy = models.ForeignKey(Policy, on_delete=models.CASCADE, null=True, blank=True, related_name='renewed_from')
    
    renewal_status = models.CharField(max_length=20, choices=RENEWAL_STATUS_CHOICES, default='pending')
    renewal_date = models.DateField()
    notice_sent_date = models.DateField(null=True, blank=True)
    response_due_date = models.DateField(null=True, blank=True)
    
    # Renewal terms
    proposed_premium = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    premium_change_percent = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'policy_renewals'
        
    def __str__(self):
        return f'Renewal: {self.original_policy.policy_number}'

class BillingSchedule(models.Model):
    FREQUENCY_CHOICES = [
        ('annual', 'Annual'),
        ('semi_annual', 'Semi-Annual'),
        ('quarterly', 'Quarterly'),
        ('monthly', 'Monthly'),
    ]
    
    schedule_id = models.AutoField(primary_key=True)
    policy = models.OneToOneField(Policy, on_delete=models.CASCADE)
    billing_frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES)
    total_premium = models.DecimalField(max_digits=12, decimal_places=2)
    installments_count = models.IntegerField()
    installment_amount = models.DecimalField(max_digits=10, decimal_places=2)
    first_payment_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'billing_schedules'
    
    def __str__(self):
        return f'{self.policy.policy_number} - {self.get_billing_frequency_display()}'

class PaymentRecord(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('check', 'Check'),
        ('ach', 'ACH/Bank Transfer'),
        ('credit_card', 'Credit Card'),
        ('wire', 'Wire Transfer'),
        ('cash', 'Cash'),
    ]
    
    payment_id = models.AutoField(primary_key=True)
    policy = models.ForeignKey(Policy, on_delete=models.CASCADE, related_name='payments')
    billing_schedule = models.ForeignKey(BillingSchedule, on_delete=models.CASCADE, null=True, blank=True)
    
    installment_number = models.IntegerField()
    due_date = models.DateField()
    amount_due = models.DecimalField(max_digits=10, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_date = models.DateField(null=True, blank=True)
    
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, null=True, blank=True)
    
    reference_number = models.CharField(max_length=50, blank=True)
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    processed_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        db_table = 'payment_records'
        ordering = ['due_date']
    
    def __str__(self):
        return f'{self.policy.policy_number} - Installment {self.installment_number}'
    
    @property
    def is_overdue(self):
        return self.payment_status == 'pending' and self.due_date < date.today()

class Commission(models.Model):
    COMMISSION_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('calculated', 'Calculated'),
        ('paid', 'Paid'),
        ('disputed', 'Disputed'),
    ]
    
    commission_id = models.AutoField(primary_key=True)
    policy = models.ForeignKey(Policy, on_delete=models.CASCADE)
    broker = models.ForeignKey('Broker', on_delete=models.CASCADE)
    
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2)  # Percentage
    premium_amount = models.DecimalField(max_digits=12, decimal_places=2)
    commission_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    commission_status = models.CharField(max_length=20, choices=COMMISSION_STATUS_CHOICES, default='pending')
    payment_date = models.DateField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'commissions'
    
    def __str__(self):
        return f'{self.broker.broker_name} - {self.policy.policy_number}'

class FinancialSummary(models.Model):
    summary_id = models.AutoField(primary_key=True)
    report_date = models.DateField()
    
    # Revenue metrics
    total_premium_written = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_premium_collected = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    outstanding_receivables = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Commission metrics
    total_commissions_owed = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_commissions_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Policy metrics
    active_policies_count = models.IntegerField(default=0)
    new_policies_count = models.IntegerField(default=0)
    renewal_policies_count = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'financial_summaries'
        ordering = ['-report_date']
    
    def __str__(self):
        return f'Financial Summary - {self.report_date}'

class SequenceTracker(models.Model):
    """
    Central sequence management for document numbering.
    Tracks the next available number for each product type.
    """
    sequence_id = models.AutoField(primary_key=True)
    product_code = models.CharField(max_length=3, unique=True)
    product_name = models.CharField(max_length=100)
    last_used_number = models.IntegerField(default=0)
    last_reserved_number = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'sequence_trackers'
        
    def __str__(self):
        return f'{self.product_code} - Last Used: {self.last_used_number}'
    
    def reserve_next_number(self):
        """Reserve the next number in sequence (6-digit)"""
        from django.db import transaction
        with transaction.atomic():
            tracker = SequenceTracker.objects.select_for_update().get(
                sequence_id=self.sequence_id
            )
            tracker.last_reserved_number += 1
            if tracker.last_reserved_number > 999999:  # UPDATED TO 6 DIGITS
                raise ValueError(f"Sequence exhausted for product {self.product_code}")
            tracker.save()
            return tracker.last_reserved_number
    
    def confirm_number(self, number):
        """Confirm a reserved number as used"""
        from django.db import transaction
        with transaction.atomic():
            tracker = SequenceTracker.objects.select_for_update().get(
                sequence_id=self.sequence_id
            )
            if number > tracker.last_used_number:
                tracker.last_used_number = number
                tracker.save()
            return tracker.last_used_number