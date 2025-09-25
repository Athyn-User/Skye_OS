from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Count, Q
from .models import Application, Quote, Company, Broker, Product
from .endorsement_generator import EndorsementGenerator

def dashboard(request):
    # Dashboard statistics
    total_applications = Application.objects.count()
    open_applications = Application.objects.filter(
        application_status__in=['received', 'in_progress']
    ).count()
    quoted_applications = Application.objects.filter(application_status='quoted').count()
    
    # Recent applications
    recent_applications = Application.objects.select_related('company', 'broker', 'product')[:10]
    
    # Pending quotes
    pending_quotes = Quote.objects.filter(quote_status='draft').select_related('application__company')[:10]
    
    context = {
        'total_applications': total_applications,
        'open_applications': open_applications,
        'quoted_applications': quoted_applications,
        'recent_applications': recent_applications,
        'pending_quotes': pending_quotes,
    }
    return render(request, 'applications/dashboard.html', context)

def application_list(request):
    applications = Application.objects.select_related('company', 'broker', 'product').all()
    
    # Filter by status if provided
    status = request.GET.get('status')
    if status:
        applications = applications.filter(application_status=status)
    
    # Search functionality
    search = request.GET.get('search')
    if search:
        applications = applications.filter(
            Q(application_number__icontains=search) |
            Q(company__company_name__icontains=search) |
            Q(broker__broker_name__icontains=search)
        )
    
    context = {
        'applications': applications,
        'current_status': status,
        'search_query': search,
    }
    return render(request, 'applications/application_list.html', context)

def application_detail(request, pk):
    application = get_object_or_404(Application, pk=pk)
    quotes = Quote.objects.filter(application=application)
    
    context = {
        'application': application,
        'quotes': quotes,
    }
    return render(request, 'applications/application_detail.html', context)

def application_create(request):
    if request.method == 'POST':
        # This is a basic implementation - you would use Django forms in production
        company_id = request.POST.get('company')
        broker_id = request.POST.get('broker')
        product_id = request.POST.get('product')
        
        application = Application.objects.create(
            company_id=company_id,
            broker_id=broker_id if broker_id else None,
            product_id=product_id,
            target_effective_date=request.POST.get('target_effective_date'),
            estimated_premium=request.POST.get('estimated_premium') or None,
            underwriting_notes=request.POST.get('underwriting_notes'),
        )
        
        messages.success(request, f'Application {application.application_number} created successfully!')
        return redirect('applications:application_detail', pk=application.pk)
    
    companies = Company.objects.filter(is_active=True)
    brokers = Broker.objects.filter(is_active=True)
    products = Product.objects.filter(is_active=True)
    
    context = {
        'companies': companies,
        'brokers': brokers,
        'products': products,
    }
    return render(request, 'applications/application_create.html', context)

def application_edit(request, pk):
    application = get_object_or_404(Application, pk=pk)
    
    if request.method == 'POST':
        application.application_status = request.POST.get('application_status')
        application.estimated_premium = request.POST.get('estimated_premium') or None
        application.quoted_premium = request.POST.get('quoted_premium') or None
        application.bound_premium = request.POST.get('bound_premium') or None
        application.underwriting_notes = request.POST.get('underwriting_notes')
        application.save()
        
        messages.success(request, f'Application {application.application_number} updated successfully!')
        return redirect('applications:application_detail', pk=application.pk)
    
    context = {
        'application': application,
    }
    return render(request, 'applications/application_edit.html', context)

def quote_list(request):
    quotes = Quote.objects.select_related('application__company').all()
    
    context = {
        'quotes': quotes,
    }
    return render(request, 'applications/quote_list.html', context)

def quote_detail(request, pk):
    quote = get_object_or_404(Quote, pk=pk)
    
    context = {
        'quote': quote,
    }
    return render(request, 'applications/quote_detail.html', context)

def quote_create(request, application_pk):
    application = get_object_or_404(Application, pk=application_pk)
    
    if request.method == 'POST':
        quote = Quote.objects.create(
            application=application,
            effective_date=request.POST.get('effective_date'),
            expiration_date=request.POST.get('expiration_date'),
            total_premium=request.POST.get('total_premium'),
            commission_amount=request.POST.get('commission_amount') or None,
            special_conditions=request.POST.get('special_conditions'),
        )
        
        # Update application status
        application.application_status = 'quoted'
        application.quoted_premium = quote.total_premium
        application.save()
        
        messages.success(request, f'Quote {quote.quote_number} created successfully!')
        return redirect('applications:quote_detail', pk=quote.pk)
    
    context = {
        'application': application,
    }
    return render(request, 'applications/quote_create.html', context)

def quote_edit(request, pk):
    quote = get_object_or_404(Quote, pk=pk)
    
    if request.method == 'POST':
        quote.quote_status = request.POST.get('quote_status')
        quote.total_premium = request.POST.get('total_premium')
        quote.commission_amount = request.POST.get('commission_amount') or None
        quote.special_conditions = request.POST.get('special_conditions')
        quote.save()
        
        messages.success(request, f'Quote {quote.quote_number} updated successfully!')
        return redirect('applications:quote_detail', pk=quote.pk)
    
    context = {
        'quote': quote,
    }
    return render(request, 'applications/quote_edit.html', context)

def company_list(request):
    companies = Company.objects.filter(is_active=True)
    
    context = {
        'companies': companies,
    }
    return render(request, 'applications/company_list.html', context)

def company_create(request):
    if request.method == 'POST':
        company = Company.objects.create(
            company_name=request.POST.get('company_name'),
            dba_name=request.POST.get('dba_name'),
            tax_id=request.POST.get('tax_id'),
            company_type=request.POST.get('company_type'),
            industry_description=request.POST.get('industry_description'),
            annual_revenue=request.POST.get('annual_revenue') or None,
            employee_count=request.POST.get('employee_count') or None,
            website=request.POST.get('website'),
        )
        
        messages.success(request, f'Company {company.company_name} created successfully!')
        return redirect('applications:company_detail', pk=company.pk)
    
    return render(request, 'applications/company_create.html')

def company_detail(request, pk):
    company = get_object_or_404(Company, pk=pk)
    applications = Application.objects.filter(company=company)
    
    context = {
        'company': company,
        'applications': applications,
    }
    return render(request, 'applications/company_detail.html', context)

# Add these imports at the top of the file
from django.http import HttpResponse
from .pdf_generator import QuotePDFGenerator

# PDF Generation Views
def quote_pdf(request, pk):
    """Generate and download PDF for a quote"""
    try:
        generator = QuotePDFGenerator()
        pdf_data = generator.generate_quote_pdf(pk)
        
        quote = get_object_or_404(Quote, pk=pk)
        filename = f"Quote_{quote.quote_number}_{quote.application.company.company_name.replace(' ', '_')}.pdf"
        
        response = HttpResponse(pdf_data, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response
        
    except Exception as e:
        messages.error(request, f'Error generating PDF: {str(e)}')
        return redirect('applications:quote_detail', pk=pk)

def quote_pdf_view(request, pk):
    """View PDF in browser"""
    try:
        generator = QuotePDFGenerator()
        pdf_data = generator.generate_quote_pdf(pk)
        
        response = HttpResponse(pdf_data, content_type='application/pdf')
        response['Content-Disposition'] = 'inline'
        
        return response
        
    except Exception as e:
        messages.error(request, f'Error generating PDF: {str(e)}')
        return redirect('applications:quote_detail', pk=pk)

def quote_email_pdf(request, pk):
    """Email PDF quote to broker/client"""
    quote = get_object_or_404(Quote, pk=pk)
    
    if request.method == 'POST':
        try:
            # Generate PDF
            generator = QuotePDFGenerator()
            pdf_data = generator.generate_quote_pdf(pk)
            
            # Email details
            recipient_email = request.POST.get('email')
            subject = f"Insurance Quote #{quote.quote_number}"
            
            # Send email (we'll implement this next)
            from django.core.mail import EmailMessage
            
            email = EmailMessage(
                subject=subject,
                body=f"""
Dear Client,

Please find attached your insurance quote #{quote.quote_number} for {quote.application.company.company_name}.

Quote Details:
- Total Premium: ${quote.total_premium:,.2f}
- Effective Date: {quote.effective_date.strftime('%B %d, %Y')}
- Expiration Date: {quote.expiration_date.strftime('%B %d, %Y')}

This quote is valid for 30 days. Please contact us to accept this quote and bind coverage.

Best regards,
Skye Insurance Group
Phone: (555) 123-4567
Email: quotes@skyeinsurance.com
                """,
                from_email='quotes@skyeinsurance.com',
                to=[recipient_email],
            )
            
            filename = f"Quote_{quote.quote_number}.pdf"
            email.attach(filename, pdf_data, 'application/pdf')
            
            # For now, we'll simulate sending (configure email backend later)
            # email.send()
            
            messages.success(request, f'Quote PDF would be sent to {recipient_email} (email not configured yet)')
            return redirect('applications:quote_detail', pk=pk)
            
        except Exception as e:
            messages.error(request, f'Error sending email: {str(e)}')
    
    context = {
        'quote': quote,
        'suggested_email': quote.application.broker.broker_name if quote.application.broker else quote.application.company.company_name
    }
    return render(request, 'applications/quote_email.html', context)

# Add these imports at the top
from .models import Certificate, CertificateTemplate, CertificateCoverage
from .certificate_generator import CertificatePDFGenerator

# Certificate Management Views
def certificate_list(request):
    certificates = Certificate.objects.select_related('quote__application__company', 'template').all()
    
    # Filter by status
    status = request.GET.get('status')
    if status:
        certificates = certificates.filter(certificate_status=status)
    
    context = {
        'certificates': certificates,
        'current_status': status,
    }
    return render(request, 'applications/certificate_list.html', context)

def certificate_detail(request, pk):
    certificate = get_object_or_404(Certificate, pk=pk)
    coverages = CertificateCoverage.objects.filter(certificate=certificate)
    
    context = {
        'certificate': certificate,
        'coverages': coverages,
    }
    return render(request, 'applications/certificate_detail.html', context)

def certificate_create(request, quote_pk):
    quote = get_object_or_404(Quote, pk=quote_pk)
    
    if request.method == 'POST':
        try:
            # Get template
            template_id = request.POST.get('template')
            template = CertificateTemplate.objects.get(pk=template_id)
            
            # Create certificate
            certificate = Certificate.objects.create(
                quote=quote,
                template=template,
                certificate_holder_name=request.POST.get('certificate_holder_name'),
                certificate_holder_address=request.POST.get('certificate_holder_address'),
                additional_insured_name=request.POST.get('additional_insured_name'),
                additional_insured_address=request.POST.get('additional_insured_address'),
                project_description=request.POST.get('project_description'),
                project_location=request.POST.get('project_location'),
                effective_date=request.POST.get('effective_date'),
                expiration_date=request.POST.get('expiration_date'),
                waiver_of_subrogation=bool(request.POST.get('waiver_of_subrogation')),
                primary_and_noncontributory=bool(request.POST.get('primary_and_noncontributory')),
                special_provisions=request.POST.get('special_provisions'),
                issued_by=request.user if request.user.is_authenticated else None,
            )
            
            # Create default coverages based on quote
            self._create_default_coverages(certificate, quote)
            
            messages.success(request, f'Certificate {certificate.certificate_number} created successfully!')
            return redirect('applications:certificate_detail', pk=certificate.pk)
            
        except Exception as e:
            messages.error(request, f'Error creating certificate: {str(e)}')
    
    templates = CertificateTemplate.objects.filter(is_active=True)
    context = {
        'quote': quote,
        'templates': templates,
    }
    return render(request, 'applications/certificate_create.html', context)

def _create_default_coverages(certificate, quote):
    """Create default coverage entries for a certificate"""
    # General Liability
    CertificateCoverage.objects.create(
        certificate=certificate,
        coverage_type='general_liability',
        each_occurrence=1000000,
        general_aggregate=2000000,
        products_completed_ops=2000000,
        personal_advertising_injury=1000000,
        policy_effective_date=certificate.effective_date,
        policy_expiration_date=certificate.expiration_date,
        policy_number=f'GL-{quote.quote_number}'
    )
    
    # Auto Liability
    CertificateCoverage.objects.create(
        certificate=certificate,
        coverage_type='auto_liability',
        each_occurrence=1000000,
        policy_effective_date=certificate.effective_date,
        policy_expiration_date=certificate.expiration_date,
        policy_number=f'AL-{quote.quote_number}'
    )
    
    # Workers Compensation
    CertificateCoverage.objects.create(
        certificate=certificate,
        coverage_type='workers_comp',
        each_occurrence=1000000,
        policy_effective_date=certificate.effective_date,
        policy_expiration_date=certificate.expiration_date,
        policy_number=f'WC-{quote.quote_number}'
    )

def certificate_pdf(request, pk):
    """Generate and download certificate PDF"""
    try:
        generator = CertificatePDFGenerator()
        pdf_data = generator.generate_certificate_pdf(pk)
        
        certificate = get_object_or_404(Certificate, pk=pk)
        filename = f"Certificate_{certificate.certificate_number}_{certificate.certificate_holder_name.replace(' ', '_')}.pdf"
        
        response = HttpResponse(pdf_data, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response
        
    except Exception as e:
        messages.error(request, f'Error generating certificate PDF: {str(e)}')
        return redirect('applications:certificate_detail', pk=pk)

def certificate_pdf_view(request, pk):
    """View certificate PDF in browser"""
    try:
        generator = CertificatePDFGenerator()
        pdf_data = generator.generate_certificate_pdf(pk)
        
        response = HttpResponse(pdf_data, content_type='application/pdf')
        response['Content-Disposition'] = 'inline'
        
        return response
        
    except Exception as e:
        messages.error(request, f'Error generating certificate PDF: {str(e)}')
        return redirect('applications:certificate_detail', pk=pk)

def certificate_issue(request, pk):
    """Issue a certificate (change status to issued)"""
    certificate = get_object_or_404(Certificate, pk=pk)
    
    if request.method == 'POST':
        certificate.certificate_status = 'issued'
        certificate.issued_date = timezone.now()
        certificate.issued_by = request.user if request.user.is_authenticated else None
        certificate.save()
        
        messages.success(request, f'Certificate {certificate.certificate_number} has been issued!')
        return redirect('applications:certificate_detail', pk=pk)
    
    context = {'certificate': certificate}
    return render(request, 'applications/certificate_issue.html', context)

def quote_accept_and_certificate(request, pk):
    """Accept quote and automatically create certificate"""
    quote = get_object_or_404(Quote, pk=pk)
    
    if request.method == 'POST':
        try:
            # Update quote status
            quote.quote_status = 'accepted'
            quote.save()
            
            # Update application status
            application = quote.application
            application.application_status = 'bound'
            application.bound_premium = quote.total_premium
            application.save()
            
            # Check if certificate should be auto-created
            if request.POST.get('create_certificate'):
                # Get default template
                template = CertificateTemplate.objects.filter(template_type='standard', is_active=True).first()
                
                if template:
                    # Create certificate with quote details
                    certificate = Certificate.objects.create(
                        quote=quote,
                        template=template,
                        certificate_holder_name=request.POST.get('certificate_holder_name', application.company.company_name),
                        certificate_holder_address=request.POST.get('certificate_holder_address', 'Address Required'),
                        effective_date=quote.effective_date,
                        expiration_date=quote.expiration_date,
                        certificate_status='issued',
                        issued_date=timezone.now(),
                        issued_by=request.user if request.user.is_authenticated else None,
                    )
                    
                    # Create default coverages
                    _create_default_coverages(certificate, quote)
                    
                    messages.success(request, f'Quote accepted and Certificate {certificate.certificate_number} created!')
                    return redirect('applications:certificate_detail', pk=certificate.pk)
            
            messages.success(request, 'Quote accepted successfully!')
            return redirect('applications:quote_detail', pk=pk)
            
        except Exception as e:
            messages.error(request, f'Error processing quote acceptance: {str(e)}')
    
    context = {
        'quote': quote,
        'application': quote.application,
    }
    return render(request, 'applications/quote_accept.html', context)

def create_endorsement(request, policy_id):
    """Create an endorsement for a policy with standard header variables"""
    policy = get_object_or_404(Policy, policy_id=policy_id)
    
    if request.method == 'POST':
        template_code = request.POST.get('template_code')
        effective_date = request.POST.get('effective_date')
        description = request.POST.get('description', '')
        
        # Collect ALL endorsement data from form
        endorsement_data = {
            'additional_insured_name': request.POST.get('additional_insured_name', ''),
            'additional_insured_address': request.POST.get('additional_insured_address', ''),
            'waiver_party': request.POST.get('waiver_party', ''),
            'description': description,
            # Add any other fields from your form
            'special_conditions': request.POST.get('special_conditions', ''),
            'project_description': request.POST.get('project_description', ''),
            'coverage_territory': request.POST.get('coverage_territory', ''),
        }
        
        try:
            # Use the enhanced endorsement generator
            generator = EndorsementGenerator()
            endorsement = generator.create_endorsement(
                policy=policy,
                template_code=template_code,
                endorsement_data=endorsement_data,
                effective_date=datetime.strptime(effective_date, '%Y-%m-%d').date() if effective_date else None
            )
            
            messages.success(request, f'Endorsement {endorsement.endorsement_number} created successfully! Header variables automatically populated.')
            return redirect('applications:view_endorsements', policy_id=policy_id)
            
        except Exception as e:
            messages.error(request, f'Error creating endorsement: {str(e)}')
    
    # Get available endorsement templates for this product
    endorsement_templates = DocumentTemplate.objects.filter(
        template_type='endorsement',
        product=policy.quote.application.product,
        is_active=True
    ).order_by('template_name')
    
    context = {
        'policy': policy,
        'templates': endorsement_templates,
        'today': datetime.now().date().isoformat(),
        # Show the user what header variables will be populated
        'header_preview': {
            'named_insured': policy.quote.application.company.company_name,
            'policy_number': policy.policy_number,
            'effective_date_preview': datetime.now().date().strftime('%B %d, %Y')
        }
    }
    
    return render(request, 'applications/create_endorsement.html', context)

def test_endorsement_generation(request, policy_id):
    """Test endorsement generation with sample data"""
    policy = get_object_or_404(Policy, policy_id=policy_id)
    
    try:
        generator = EndorsementGenerator()
        sample_endorsements = generator.create_sample_endorsements(policy)
        
        if sample_endorsements:
            endorsement_numbers = [e.endorsement_number for e in sample_endorsements]
            messages.success(request, f'Created {len(sample_endorsements)} sample endorsements: {", ".join(endorsement_numbers)}')
        else:
            messages.warning(request, 'No endorsement templates found for testing.')
            
        return redirect('applications:view_endorsements', policy_id=policy_id)
        
    except Exception as e:
        messages.error(request, f'Error creating test endorsements: {str(e)}')
        return redirect('applications:policy_detail', policy_id=policy_id)