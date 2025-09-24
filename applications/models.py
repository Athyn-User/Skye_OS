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
    quote_version = models.IntegerField(default=1)
    quote_date = models.DateField(auto_now_add=True)
    effective_date = models.DateField()
    expiration_date = models.DateField()
    quote_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    total_premium = models.DecimalField(max_digits=12, decimal_places=2)
    commission_amount = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    special_conditions = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'quotes'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.quote_number or 'QTE-TBD'} - {self.application.company.company_name}"

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

# Import certificate models



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
    
    def save(self, *args, **kwargs):
        if not self.policy_number:
            self.policy_number = f'POL-{uuid.uuid4().hex[:8].upper()}'
        if not self.renewal_date and self.expiration_date:
            # Set renewal date 60 days before expiration
            from datetime import timedelta
            self.renewal_date = self.expiration_date - timedelta(days=60)
        super().save(*args, **kwargs)

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


