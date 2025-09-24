from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from .models import Certificate, CertificateTemplate, CertificateCoverage, Quote
from .certificate_forms import CertificateForm, CertificateTemplateForm
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from io import BytesIO
import uuid
from datetime import date

def certificate_list(request):
    '''List all certificates with pagination'''
    certificates = Certificate.objects.all().order_by('-created_at')
    paginator = Paginator(certificates, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'certificates': page_obj,
        'title': 'Certificate Management'
    }
    return render(request, 'certificates/certificate_list.html', context)

def certificate_detail(request, certificate_id):
    '''View certificate details'''
    certificate = get_object_or_404(Certificate, certificate_id=certificate_id)
    coverages = certificate.certificatecoverage_set.all()
    
    context = {
        'certificate': certificate,
        'coverages': coverages,
        'title': f'Certificate {certificate.certificate_number}'
    }
    return render(request, 'certificates/certificate_detail.html', context)

def certificate_create(request):
    '''Create new certificate'''
    if request.method == 'POST':
        form = CertificateForm(request.POST)
        if form.is_valid():
            certificate = form.save(commit=False)
            # certificate.created_by = request.user  # Temporarily disabled
            if not certificate.certificate_number:
                certificate.certificate_number = f'CERT-{uuid.uuid4().hex[:8].upper()}'
            certificate.save()
            messages.success(request, f'Certificate {certificate.certificate_number} created successfully!')
            return redirect('applications:certificate_detail', certificate_id=certificate.certificate_id)
    else:
        form = CertificateForm()
    
    context = {
        'form': form,
        'title': 'Create New Certificate'
    }
    return render(request, 'certificates/certificate_form.html', context)

def certificate_from_quote(request, quote_id):
    '''Create certificate from existing quote'''
    quote = get_object_or_404(Quote, quote_id=quote_id)
    
    if request.method == 'POST':
        form = CertificateForm(request.POST)
        if form.is_valid():
            certificate = form.save(commit=False)
            certificate.quote = quote
            # certificate.created_by = request.user  # Temporarily disabled
            certificate.certificate_number = f'CERT-{uuid.uuid4().hex[:8].upper()}'
            
            # Pre-populate from quote data
            if quote.application:
                certificate.insured_name = quote.application.company.company_name
                # Add more quote data mapping here
            
            certificate.save()
            messages.success(request, f'Certificate {certificate.certificate_number} created from quote!')
            return redirect('applications:certificate_detail', certificate_id=certificate.certificate_id)
    else:
        # Pre-populate form with quote data
        initial_data = {
            'effective_date': date.today(),
            'template': CertificateTemplate.objects.filter(template_type='standard').first()
        }
        if quote.application:
            initial_data['insured_name'] = quote.application.company.company_name
        
        form = CertificateForm(initial=initial_data)
    
    context = {
        'form': form,
        'quote': quote,
        'title': f'Create Certificate from Quote {quote.quote_number}'
    }
    return render(request, 'certificates/certificate_form.html', context)








from django.http import JsonResponse
from datetime import date
import uuid

@login_required
def certificate_issue(request, certificate_id):
    '''Issue a certificate'''
    certificate = get_object_or_404(Certificate, certificate_id=certificate_id)
    
    if request.method == 'POST':
        certificate.certificate_status = 'issued'
        # certificate.issued_date = date.today()  # Temporarily disabled
        # certificate.issued_by = request.user  # Temporarily disabled
        certificate.save()
        
        return JsonResponse({'success': True, 'message': 'Certificate issued successfully'})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@login_required
def certificate_cancel(request, certificate_id):
    '''Cancel a certificate'''
    certificate = get_object_or_404(Certificate, certificate_id=certificate_id)
    
    if request.method == 'POST':
        certificate.certificate_status = 'cancelled'
        certificate.save()
        
        return JsonResponse({'success': True, 'message': 'Certificate cancelled'})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@login_required
def certificate_revise(request, certificate_id):
    '''Create a revised version of a certificate'''
    original_certificate = get_object_or_404(Certificate, certificate_id=certificate_id)
    
    # Create new certificate based on original
    new_certificate = Certificate(
        template=original_certificate.template,
        certificate_holder_name=original_certificate.certificate_holder_name,
        certificate_holder_address=original_certificate.certificate_holder_address,
        additional_insured_name=original_certificate.additional_insured_name,
        additional_insured_address=original_certificate.additional_insured_address,
        project_description=original_certificate.project_description,
        project_location=original_certificate.project_location,
        effective_date=original_certificate.effective_date,
        expiration_date=original_certificate.expiration_date,
        special_provisions=original_certificate.special_provisions,
        waiver_of_subrogation=original_certificate.waiver_of_subrogation,
        primary_and_noncontributory=original_certificate.primary_and_noncontributory,
        certificate_status='draft',
        created_by=request.user
    )
    new_certificate.certificate_number = f'CERT-{uuid.uuid4().hex[:8].upper()}'
    new_certificate.save()
    
    # Mark original as revised
    original_certificate.certificate_status = 'revised'
    original_certificate.save()
    
    messages.success(request, f'Created revised certificate {new_certificate.certificate_number}')
    return redirect('applications:certificate_detail', certificate_id=new_certificate.certificate_id)


from .certificate_pdf import generate_certificate_pdf
from django.core.mail import EmailMessage
from django.conf import settings

@login_required
def certificate_pdf(request, certificate_id):
    '''Generate ACORD-style certificate PDF'''
    certificate = get_object_or_404(Certificate, certificate_id=certificate_id)
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, 
                          topMargin=0.75*inch, bottomMargin=0.75*inch,
                          leftMargin=0.5*inch, rightMargin=0.5*inch)
    
    styles = getSampleStyleSheet()
    story = []
    
    # ACORD Header
    header_style = ParagraphStyle('ACORDHeader', parent=styles['Normal'],
                                fontSize=14, alignment=1, spaceAfter=20,
                                fontName='Helvetica-Bold')
    
    story.append(Paragraph('CERTIFICATE OF LIABILITY INSURANCE', header_style))
    story.append(Paragraph('DATE (MM/DD/YYYY)', styles['Normal']))
    
    # Producer and Insurer section
    producer_data = [
        ['PRODUCER', 'CONTACT NAME:', '', 'PHONE (A/C, No, Ext):', 'E-MAIL ADDRESS:'],
        ['Your Insurance Agency', 'Agent Name', '', '(555) 123-4567', 'agent@agency.com'],
        ['123 Agency Street', '', '', 'FAX (A/C, No):', ''],
        ['City, ST 12345', '', '', '(555) 123-4568', '']
    ]
    
    producer_table = Table(producer_data, colWidths=[2*inch, 1.5*inch, 0.5*inch, 1.2*inch, 1.8*inch])
    producer_table.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 3),
        ('TOPPADDING', (0,0), (-1,-1), 3),
    ]))
    
    story.append(producer_table)
    story.append(Spacer(1, 10))
    
    # Insured section
    insured_data = [
        ['INSURED'],
        [certificate.certificate_holder_name or 'Certificate Holder Name'],
        [certificate.certificate_holder_address or 'Address']
    ]
    
    insured_table = Table(insured_data, colWidths=[7*inch])
    insured_table.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('FONTNAME', (0,0), (0,0), 'Helvetica-Bold'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    
    story.append(insured_table)
    story.append(Spacer(1, 10))
    
    # Coverages table (ACORD standard layout)
    coverage_headers = [
        'TYPE OF INSURANCE',
        'ADDL INSD',
        'SUBR WVD', 
        'POLICY NUMBER',
        'POLICY EFF DATE (MM/DD/YYYY)',
        'POLICY EXP DATE (MM/DD/YYYY)',
        'LIMITS'
    ]
    
    coverage_data = [coverage_headers]
    
    # Add sample coverage rows (you can populate from your CertificateCoverage model)
    sample_coverages = [
        ['GENERAL LIABILITY', 'Y', 'Y', 'GL-123456789', '09/22/2025', '09/22/2026', 'EACH OCCURRENCE: $1,000,000\nGENERAL AGGREGATE: $2,000,000'],
        ['COMMERCIAL GENERAL LIABILITY', '', '', '', '', '', 'PRODUCTS-COMP/OP AGG: $2,000,000'],
        ['AUTOMOBILE LIABILITY', 'Y', 'Y', 'AL-987654321', '09/22/2025', '09/22/2026', 'COMBINED SINGLE LIMIT: $1,000,000'],
        ['', '', '', '', '', '', 'BODILY INJURY (Per person): $'],
        ['', '', '', '', '', '', 'BODILY INJURY (Per accident): $'],
        ['', '', '', '', '', '', 'PROPERTY DAMAGE (Per accident): $']
    ]
    
    coverage_data.extend(sample_coverages)
    
    coverage_table = Table(coverage_data, colWidths=[1.3*inch, 0.5*inch, 0.5*inch, 1.2*inch, 1.0*inch, 1.0*inch, 1.5*inch])
    coverage_table.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 7),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 2),
        ('RIGHTPADDING', (0,0), (-1,-1), 2),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
    ]))
    
    story.append(coverage_table)
    story.append(Spacer(1, 15))
    
    # Description section
    desc_text = f"""DESCRIPTION OF OPERATIONS / LOCATIONS / VEHICLES (ACORD 101, Additional Remarks Schedule, may be attached if more space is required)
    
{certificate.project_description or 'Project operations as per contract'}

Certificate holder is included as additional insured as respects general liability coverage."""
    
    story.append(Paragraph(desc_text, styles['Normal']))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Certificate_{certificate.certificate_number}.pdf"'
    
    return response

@login_required
def certificate_email(request, certificate_id):
    '''Email certificate PDF to certificate holder'''
    certificate = get_object_or_404(Certificate, certificate_id=certificate_id)
    
    if request.method == 'POST':
        try:
            # Generate PDF
            pdf_buffer = generate_certificate_pdf(certificate)
            
            # Create email
            subject = f'Certificate of Insurance - {certificate.certificate_number}'
            message = f'''Dear {certificate.certificate_holder_name},

Please find attached your Certificate of Insurance #{certificate.certificate_number}.

Certificate Details:
- Effective Date: {certificate.effective_date.strftime('%B %d, %Y') if certificate.effective_date else 'Not specified'}
- Expiration Date: {certificate.expiration_date.strftime('%B %d, %Y') if certificate.expiration_date else 'Not specified'}

If you have any questions about this certificate, please contact us.

Best regards,
Insurance Team'''
            
            email = EmailMessage(
                subject=subject,
                body=message,
                from_email=settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@example.com',
                to=['placeholder@example.com']  # You'll need to add email field to certificate model
            )
            
            # Attach PDF
            email.attach(
                f'Certificate_{certificate.certificate_number}.pdf',
                pdf_buffer.getvalue(),
                'application/pdf'
            )
            
            # Send email
            email.send()
            
            return JsonResponse({'success': True, 'message': 'Certificate emailed successfully'})
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})







from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from io import BytesIO

@login_required
def certificate_issue(request, certificate_id):
    '''Issue a certificate (change from draft to issued)'''
    certificate = get_object_or_404(Certificate, certificate_id=certificate_id)
    
    if request.method == 'POST':
        if certificate.certificate_status == 'draft':
            certificate.certificate_status = 'issued'
            certificate.issued_date = date.today()
            if hasattr(certificate, 'issued_by'):
                certificate.issued_by = request.user
            certificate.save()
            
            messages.success(request, f'Certificate {certificate.certificate_number} has been issued!')
            return JsonResponse({'success': True, 'status': 'issued'})
        else:
            return JsonResponse({'success': False, 'error': 'Certificate is not in draft status'})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@login_required
def certificate_cancel(request, certificate_id):
    '''Cancel an issued certificate'''
    certificate = get_object_or_404(Certificate, certificate_id=certificate_id)
    
    if request.method == 'POST':
        if certificate.certificate_status == 'issued':
            certificate.certificate_status = 'cancelled'
            certificate.save()
            
            messages.success(request, f'Certificate {certificate.certificate_number} has been cancelled!')
            return JsonResponse({'success': True, 'status': 'cancelled'})
        else:
            return JsonResponse({'success': False, 'error': 'Only issued certificates can be cancelled'})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@login_required
def certificate_revise(request, certificate_id):
    '''Create a revised version of a certificate'''
    original = get_object_or_404(Certificate, certificate_id=certificate_id)
    
    if original.certificate_status != 'issued':
        messages.error(request, 'Only issued certificates can be revised')
        return redirect('applications:certificate_detail', certificate_id=certificate_id)
    
    # Create revised certificate
    revised = Certificate(
        quote=original.quote,
        template=original.template,
        certificate_holder_name=original.certificate_holder_name,
        certificate_holder_address=original.certificate_holder_address,
        additional_insured_name=original.additional_insured_name,
        additional_insured_address=original.additional_insured_address,
        project_description=original.project_description,
        project_location=original.project_location,
        effective_date=original.effective_date,
        expiration_date=original.expiration_date,
        special_provisions=original.special_provisions,
        waiver_of_subrogation=original.waiver_of_subrogation,
        primary_and_noncontributory=original.primary_and_noncontributory,
        certificate_status='draft'
    )
    revised.certificate_number = f'CERT-{uuid.uuid4().hex[:8].upper()}'
    revised.save()
    
    # Mark original as revised
    original.certificate_status = 'revised'
    original.save()
    
    messages.success(request, f'Created revised certificate {revised.certificate_number}')
    return redirect('applications:certificate_detail', certificate_id=revised.certificate_id)


from django.core.mail import EmailMessage
from django.conf import settings

@login_required
def certificate_email(request, certificate_id):
    '''Email certificate PDF to certificate holder'''
    certificate = get_object_or_404(Certificate, certificate_id=certificate_id)
    
    if request.method == 'POST':
        try:
            # Generate PDF
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter)
            # (Use the same PDF generation code as certificate_pdf)
            
            # Create email
            subject = f'Certificate of Insurance - {certificate.certificate_number}'
            message = f'''Dear {certificate.certificate_holder_name},

Please find attached your Certificate of Insurance #{certificate.certificate_number}.

Certificate Details:
- Effective Date: {certificate.effective_date.strftime('%B %d, %Y') if certificate.effective_date else 'Not specified'}
- Expiration Date: {certificate.expiration_date.strftime('%B %d, %Y') if certificate.expiration_date else 'Not specified'}
- Status: {certificate.get_certificate_status_display()}

This certificate serves as evidence of insurance coverage. Please keep it for your records.

If you have any questions about this certificate, please contact us.

Best regards,
Insurance Team'''
            
            # For now, we'll use a placeholder email - in production you'd get this from certificate holder
            recipient_email = request.POST.get('email', 'client@example.com')
            
            email = EmailMessage(
                subject=subject,
                body=message,
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@skyeos.com'),
                to=[recipient_email]
            )
            
            # Generate and attach PDF (reuse certificate_pdf logic)
            pdf_buffer = BytesIO()
            # (PDF generation code here)
            
            email.attach(
                f'Certificate_{certificate.certificate_number}.pdf',
                pdf_buffer.getvalue(),
                'application/pdf'
            )
            
            # Send email (for demo, we'll just return success)
            # email.send()
            
            return JsonResponse({'success': True, 'message': 'Certificate emailed successfully'})
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

