from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, Frame
from reportlab.lib.units import inch
from io import BytesIO
from datetime import datetime
from applications.models import Certificate, CertificateCoverage

class CertificatePDFGenerator:
    def __init__(self):
        self.width, self.height = letter
        self.styles = getSampleStyleSheet()
        
    def generate_certificate_pdf(self, certificate_id):
        certificate = Certificate.objects.get(pk=certificate_id)
        coverages = CertificateCoverage.objects.filter(certificate=certificate)
        
        # Create BytesIO buffer
        buffer = BytesIO()
        
        # Create PDF document
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )
        
        # Build PDF content
        story = []
        
        # ACORD Header
        story.append(self._create_acord_header())
        story.append(Spacer(1, 10))
        
        # Certificate title
        story.append(self._create_certificate_title(certificate))
        story.append(Spacer(1, 15))
        
        # Producer information
        story.append(self._create_producer_section())
        story.append(Spacer(1, 10))
        
        # Insurer information
        story.append(self._create_insurer_section())
        story.append(Spacer(1, 10))
        
        # Insured information
        story.append(self._create_insured_section(certificate))
        story.append(Spacer(1, 10))
        
        # Coverages table
        story.append(self._create_coverages_table(coverages))
        story.append(Spacer(1, 15))
        
        # Certificate holder section
        story.append(self._create_certificate_holder_section(certificate))
        story.append(Spacer(1, 10))
        
        # Description section
        story.append(self._create_description_section(certificate))
        story.append(Spacer(1, 15))
        
        # Signature section
        story.append(self._create_signature_section(certificate))
        
        # Build PDF
        doc.build(story)
        
        # Get PDF data
        pdf_data = buffer.getvalue()
        buffer.close()
        
        return pdf_data
    
    def _create_acord_header(self):
        # ACORD-style header
        header_data = [
            ['CERTIFICATE OF LIABILITY INSURANCE', '', '', 'DATE (MM/DD/YYYY)'],
            ['', '', '', datetime.now().strftime('%m/%d/%Y')]
        ]
        
        header_table = Table(header_data, colWidths=[4*inch, 1*inch, 1*inch, 1.5*inch])
        header_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (0, 0), 14),
            ('FONTNAME', (3, 0), (3, 1), 'Helvetica-Bold'),
            ('FONTSIZE', (3, 0), (3, 1), 10),
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (3, 0), (3, 1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('BOX', (3, 0), (3, 1), 1, colors.black),
        ]))
        
        return header_table
    
    def _create_certificate_title(self, certificate):
        title_text = f"Certificate No: {certificate.certificate_number}"
        title_style = ParagraphStyle(
            'CertTitle',
            parent=self.styles['Normal'],
            fontSize=12,
            fontName='Helvetica-Bold'
        )
        return Paragraph(title_text, title_style)
    
    def _create_producer_section(self):
        producer_data = [
            ['THIS CERTIFICATE IS ISSUED AS A MATTER OF INFORMATION ONLY AND CONFERS NO RIGHTS UPON THE CERTIFICATE HOLDER. THIS CERTIFICATE DOES NOT AFFIRMATIVELY OR NEGATIVELY AMEND, EXTEND OR ALTER THE COVERAGE AFFORDED BY THE POLICIES BELOW. THIS CERTIFICATE OF INSURANCE DOES NOT CONSTITUTE A CONTRACT BETWEEN THE ISSUING INSURER(S), AUTHORIZED REPRESENTATIVE OR PRODUCER, AND THE CERTIFICATE HOLDER.'],
            [''],
            ['PRODUCER', ''],
            ['Skye Insurance Group', 'CONTACT NAME:'],
            ['123 Insurance Plaza', 'John Smith'],
            ['Any City, State 12345', 'PHONE: (555) 123-4567'],
            ['', 'E-MAIL: certificates@skyeinsurance.com']
        ]
        
        producer_table = Table(producer_data, colWidths=[4*inch, 3.5*inch])
        producer_table.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('FONTNAME', (0, 2), (0, 2), 'Helvetica-Bold'),
            ('FONTNAME', (1, 3), (1, 6), 'Helvetica-Bold'),
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('LINEBELOW', (0, 1), (-1, 1), 1, colors.black),
            ('LINEBETWEEN', (0, 2), (0, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        return producer_table
    
    def _create_insurer_section(self):
        insurer_data = [
            ['INSURER(S) AFFORDING COVERAGE', 'NAIC #'],
            ['INSURER A: Acme Insurance Company', '12345'],
            ['INSURER B: Reliable Coverage Corp', '67890'],
            ['INSURER C:', ''],
            ['INSURER D:', ''],
            ['INSURER E:', ''],
            ['INSURER F:', '']
        ]
        
        insurer_table = Table(insurer_data, colWidths=[6*inch, 1.5*inch])
        insurer_table.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        return insurer_table
    
    def _create_insured_section(self, certificate):
        insured_data = [
            ['INSURED'],
            [certificate.quote.application.company.company_name],
            [certificate.quote.application.company.company_name],  # Address would go here
            ['Any City, State 12345']  # Address continuation
        ]
        
        insured_table = Table(insured_data, colWidths=[7.5*inch])
        insured_table.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        return insured_table
    
    def _create_coverages_table(self, coverages):
        # Create coverages table header
        headers = [
            'TYPE OF INSURANCE',
            'ADDL INSD',
            'SUBR WVD',
            'POLICY NUMBER',
            'POLICY EFF DATE',
            'POLICY EXP DATE',
            'LIMITS'
        ]
        
        # Build coverage rows
        coverage_data = [headers]
        
        for coverage in coverages:
            # Format limits based on coverage type
            limits_text = self._format_coverage_limits(coverage)
            
            row = [
                coverage.get_coverage_type_display(),
                'Y' if hasattr(coverage.certificate, 'additional_insured_name') and coverage.certificate.additional_insured_name else 'N',
                'Y' if coverage.certificate.waiver_of_subrogation else 'N',
                coverage.policy_number or 'TBD',
                coverage.policy_effective_date.strftime('%m/%d/%Y'),
                coverage.policy_expiration_date.strftime('%m/%d/%Y'),
                limits_text
            ]
            coverage_data.append(row)
        
        # Add empty rows if needed
        while len(coverage_data) < 6:  # Minimum 5 coverage rows
            coverage_data.append(['', '', '', '', '', '', ''])
        
        coverage_table = Table(coverage_data, colWidths=[1.8*inch, 0.6*inch, 0.6*inch, 1.2*inch, 0.8*inch, 0.8*inch, 1.7*inch])
        coverage_table.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (1, 0), (2, -1), 'CENTER'),
        ]))
        
        return coverage_table
    
    def _format_coverage_limits(self, coverage):
        """Format coverage limits based on type"""
        if coverage.coverage_type == 'general_liability':
            limits = []
            if coverage.each_occurrence:
                limits.append(f"Each Occurrence: ${coverage.each_occurrence:,.0f}")
            if coverage.general_aggregate:
                limits.append(f"General Aggregate: ${coverage.general_aggregate:,.0f}")
            if coverage.products_completed_ops:
                limits.append(f"Products-Comp/OP Agg: ${coverage.products_completed_ops:,.0f}")
            return '\n'.join(limits)
        elif coverage.coverage_type == 'auto_liability':
            if coverage.each_occurrence:
                return f"Combined Single Limit: ${coverage.each_occurrence:,.0f}"
        elif coverage.coverage_type == 'workers_comp':
            return "WC Statutory Limits\nEL Each Accident: $1,000,000\nEL Disease-Policy Limit: $1,000,000\nEL Disease-Each Employee: $1,000,000"
        else:
            if coverage.each_occurrence:
                return f"${coverage.each_occurrence:,.0f}"
        return ""
    
    def _create_certificate_holder_section(self, certificate):
        holder_data = [
            ['CERTIFICATE HOLDER'],
            [certificate.certificate_holder_name],
            [certificate.certificate_holder_address]
        ]
        
        holder_table = Table(holder_data, colWidths=[7.5*inch])
        holder_table.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        return holder_table
    
    def _create_description_section(self, certificate):
        description_text = "DESCRIPTION OF OPERATIONS / LOCATIONS / VEHICLES (ACORD 101, Additional Remarks Schedule, may be attached if more space is required)\n\n"
        
        if certificate.project_description:
            description_text += f"Project: {certificate.project_description}\n"
        if certificate.project_location:
            description_text += f"Location: {certificate.project_location}\n"
        if certificate.additional_insured_name:
            description_text += f"\n{certificate.additional_insured_name} is included as Additional Insured.\n"
        if certificate.waiver_of_subrogation:
            description_text += "Waiver of Subrogation applies in favor of Certificate Holder.\n"
        if certificate.primary_and_noncontributory:
            description_text += "Coverage is Primary and Non-contributory.\n"
        if certificate.special_provisions:
            description_text += f"\nSpecial Provisions: {certificate.special_provisions}"
        
        description_style = ParagraphStyle(
            'Description',
            parent=self.styles['Normal'],
            fontSize=9,
            leading=11
        )
        
        description_para = Paragraph(description_text, description_style)
        
        # Create frame for description
        description_data = [
            ['DESCRIPTION OF OPERATIONS / LOCATIONS / VEHICLES'],
            [description_para]
        ]
        
        description_table = Table(description_data, colWidths=[7.5*inch], rowHeights=[20, 120])
        description_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (0, 0), 9),
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        return description_table
    
    def _create_signature_section(self, certificate):
        signature_data = [
            ['CANCELLATION', ''],
            ['SHOULD ANY OF THE ABOVE DESCRIBED POLICIES BE CANCELLED BEFORE THE EXPIRATION DATE THEREOF, NOTICE WILL BE DELIVERED IN ACCORDANCE WITH THE POLICY PROVISIONS.', ''],
            ['', ''],
            ['AUTHORIZED REPRESENTATIVE', 'SIGNATURE OF AUTHORIZED REPRESENTATIVE'],
            ['Skye Insurance Group', ''],
            [f'Date: {datetime.now().strftime("%m/%d/%Y")}', '']
        ]
        
        signature_table = Table(signature_data, colWidths=[3.75*inch, 3.75*inch], rowHeights=[20, 40, 10, 20, 30, 20])
        signature_table.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 3), (-1, 3), 'Helvetica-Bold'),
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('LINEBETWEEN', (0, 0), (0, -1), 1, colors.black),
            ('LINEBELOW', (0, 2), (-1, 2), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        return signature_table
