from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from django.http import HttpResponse
from io import BytesIO
import os

def generate_certificate_pdf(certificate):
    '''Generate ACORD-style certificate PDF'''
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    
    # Get styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30,
        alignment=1,  # Center
        textColor=colors.black
    )
    
    header_style = ParagraphStyle(
        'HeaderStyle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.black,
        fontName='Helvetica-Bold'
    )
    
    normal_style = ParagraphStyle(
        'NormalStyle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.black
    )
    
    story = []
    
    # Title
    story.append(Paragraph('CERTIFICATE OF LIABILITY INSURANCE', title_style))
    story.append(Spacer(1, 20))
    
    # Certificate information header
    cert_info_data = [
        ['CERTIFICATE NUMBER:', certificate.certificate_number or 'PENDING'],
        ['EFFECTIVE DATE:', certificate.effective_date.strftime('%m/%d/%Y') if certificate.effective_date else ''],
        ['EXPIRATION DATE:', certificate.expiration_date.strftime('%m/%d/%Y') if certificate.expiration_date else ''],
        ['ISSUED DATE:', certificate.issued_date.strftime('%m/%d/%Y') if certificate.issued_date else 'DRAFT']
    ]
    
    cert_info_table = Table(cert_info_data, colWidths=[2*inch, 2*inch])
    cert_info_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    
    story.append(cert_info_table)
    story.append(Spacer(1, 20))
    
    # Certificate Holder Information
    story.append(Paragraph('CERTIFICATE HOLDER', header_style))
    story.append(Spacer(1, 10))
    
    holder_data = [
        [certificate.certificate_holder_name or ''],
        [certificate.certificate_holder_address or '']
    ]
    
    holder_table = Table(holder_data, colWidths=[6*inch])
    holder_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    
    story.append(holder_table)
    story.append(Spacer(1, 20))
    
    # Coverage Information
    story.append(Paragraph('COVERAGES', header_style))
    story.append(Spacer(1, 10))
    
    # Coverage table headers
    coverage_headers = [
        'TYPE OF INSURANCE',
        'POLICY NUMBER',
        'POLICY EFF DATE',
        'POLICY EXP DATE',
        'LIMITS'
    ]
    
    coverage_data = [coverage_headers]
    
    # Add coverage rows
    coverages = certificate.certificatecoverage_set.all()
    for coverage in coverages:
        limits_text = ''
        if coverage.each_occurrence:
            limits_text += f'Each Occurrence: \\n'
        if coverage.general_aggregate:
            limits_text += f'General Aggregate: '
            
        coverage_data.append([
            coverage.get_coverage_type_display(),
            coverage.policy_number or '',
            coverage.policy_effective_date.strftime('%m/%d/%Y') if hasattr(coverage, 'policy_effective_date') and coverage.policy_effective_date else '',
            coverage.policy_expiration_date.strftime('%m/%d/%Y') if hasattr(coverage, 'policy_expiration_date') and coverage.policy_expiration_date else '',
            limits_text
        ])
    
    # If no coverages, add empty rows
    if not coverages:
        for _ in range(3):
            coverage_data.append(['', '', '', '', ''])
    
    coverage_table = Table(coverage_data, colWidths=[1.5*inch, 1.5*inch, 1*inch, 1*inch, 1.5*inch])
    coverage_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Headers
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),  # Header background
    ]))
    
    story.append(coverage_table)
    story.append(Spacer(1, 20))
    
    # Additional Information
    if certificate.project_description or certificate.special_provisions:
        story.append(Paragraph('DESCRIPTION OF OPERATIONS / LOCATIONS / VEHICLES / EXCLUSIONS ADDED BY ENDORSEMENT / SPECIAL PROVISIONS', header_style))
        story.append(Spacer(1, 10))
        
        desc_text = ''
        if certificate.project_description:
            desc_text += f'Project Description: {certificate.project_description}\\n\\n'
        if certificate.special_provisions:
            desc_text += f'Special Provisions: {certificate.special_provisions}'
            
        story.append(Paragraph(desc_text, normal_style))
        story.append(Spacer(1, 20))
    
    # Certificate provisions
    provisions = []
    if certificate.waiver_of_subrogation:
        provisions.append('Waiver of Subrogation in favor of Certificate Holder')
    if certificate.primary_and_noncontributory:
        provisions.append('Certificate Holder is Additional Insured on Primary and Non-contributory basis')
    
    if provisions:
        story.append(Paragraph('CERTIFICATE PROVISIONS:', header_style))
        for provision in provisions:
            story.append(Paragraph(f'• {provision}', normal_style))
        story.append(Spacer(1, 20))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer

