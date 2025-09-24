# File: applications/document_generator.py
# Document generation service for creating policy documents

import os
import io
import json
from datetime import datetime, date
from decimal import Decimal
from typing import Dict, List, Optional, Tuple

from django.conf import settings
from django.template.loader import render_to_string
from django.core.files.base import ContentFile
from django.db import transaction

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.platypus.frames import Frame
from reportlab.lib.enums import TA_CENTER, TA_RIGHT

from PyPDF2 import PdfMerger, PdfReader, PdfWriter
import PyPDF2.generic as pdf_generic

from .document_models import (
    DocumentTemplate, PolicyDocumentPackage, DocumentComponent,
    EndorsementDocument, DocumentDelivery
)
from .models import Policy, Quote, Application, Company


class DocumentGenerator:
    """Main service for generating insurance documents"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
        
    def _setup_custom_styles(self):
        """Setup custom styles for insurance documents"""
        self.styles.add(ParagraphStyle(
            name='InsuranceTitle',
            parent=self.styles['Heading1'],
            fontSize=16,
            spaceAfter=12,
            textColor=colors.HexColor('#003366'),
            alignment=TA_CENTER
        ))
        
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=12,
            spaceAfter=6,
            textColor=colors.HexColor('#003366'),
            bold=True
        ))
        
        self.styles.add(ParagraphStyle(
            name='CoverageItem',
            parent=self.styles['Normal'],
            fontSize=10,
            leftIndent=20
        ))
    
    def generate_policy_package(self, policy: Policy, reissue: bool = False) -> PolicyDocumentPackage:
        """
        Generate complete policy document package
        """
        with transaction.atomic():
            # Create package record
            package = self._create_package_record(policy, reissue)
            
            # Get applicable templates
            templates = self._get_applicable_templates(policy)
            
            # Generate each component
            components = []
            for seq, template in enumerate(templates, 1):
                component = self._generate_component(package, template, seq)
                components.append(component)
            
            # Combine all PDFs
            combined_pdf = self._combine_pdfs(components)
            
            # Save combined package
            package = self._save_package(package, combined_pdf)
            
            # Mark previous packages as superseded if reissue
            if reissue:
                self._supersede_previous_packages(policy, package)
            
            return package
    
    def _create_package_record(self, policy: Policy, reissue: bool) -> PolicyDocumentPackage:
        """Create the package record"""
        # Determine version number
        version = 0
        if reissue:
            last_package = PolicyDocumentPackage.objects.filter(
                policy=policy
            ).order_by('-package_version').first()
            version = (last_package.package_version + 1) if last_package else 1
        
        package = PolicyDocumentPackage(
            policy=policy,
            package_version=version,
            package_status='draft',
            generation_data=self._get_generation_data(policy),
            state_code=self._get_state_code(policy)
        )
        package.package_number = package.generate_package_number()
        package.save()
        
        return package
    
    def _get_applicable_templates(self, policy: Policy) -> List[DocumentTemplate]:
        """Get all templates applicable to this policy"""
        templates = []
        product = policy.quote.application.product
        state_code = self._get_state_code(policy)
        
        # Get product-specific templates
        product_templates = DocumentTemplate.objects.filter(
            product=product,
            is_active=True,
            effective_date__lte=datetime.now().date()
        ).filter(
            models.Q(expiration_date__isnull=True) | 
            models.Q(expiration_date__gte=datetime.now().date())
        )
        
        # Filter for state applicability
        for template in product_templates:
            if template.template_type == 'state_form':
                if template.is_applicable_to_state(state_code):
                    templates.append(template)
            else:
                templates.append(template)
        
        # Sort by sequence
        templates.sort(key=lambda x: x.default_sequence)
        
        return templates
    
    def _generate_component(self, package: PolicyDocumentPackage, 
                          template: DocumentTemplate, sequence: int) -> DocumentComponent:
        """Generate a single document component"""
        component = DocumentComponent(
            package=package,
            template=template,
            component_type=template.template_type,
            component_name=template.template_name,
            sequence_order=sequence,
            component_status='pending'
        )
        component.save()
        
        try:
            if template.template_format == 'dynamic':
                pdf_content = self._generate_dynamic_pdf(template, package.policy)
            elif template.template_format == 'static':
                pdf_content = self._get_static_pdf(template)
            else:  # hybrid
                pdf_content = self._fill_hybrid_pdf(template, package.policy)
            
            # Save component PDF
            file_path = self._save_component_file(component, pdf_content)
            component.file_path = file_path
            component.component_status = 'generated'
            component.generated_at = datetime.now()
            
            # Get page count
            reader = PdfReader(io.BytesIO(pdf_content))
            component.page_count = len(reader.pages)
            component.file_size = len(pdf_content)
            
            # Set page numbering
            component.page_numbering = f"Page 1 of {component.page_count}"
            
            component.save()
            
        except Exception as e:
            component.component_status = 'error'
            component.error_message = str(e)
            component.save()
        
        return component
    
    def _generate_dynamic_pdf(self, template: DocumentTemplate, policy: Policy) -> bytes:
        """Generate a dynamic PDF from template"""
        # Get merge data
        merge_data = self._get_merge_data(policy)
        
        # Create PDF buffer
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        
        # Build story based on template type
        if template.template_type == 'declaration':
            story = self._build_declaration_page(merge_data)
        elif template.template_type == 'schedule':
            story = self._build_schedule_page(merge_data)
        else:
            # Use HTML template if available
            if template.html_template:
                html_content = self._render_html_template(template.html_template, merge_data)
                story = self._html_to_story(html_content)
            else:
                story = [Paragraph("Template content not available", self.styles['Normal'])]
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer.read()
    
    def _build_declaration_page(self, data: Dict) -> List:
        """Build declaration page story"""
        story = []
        
        # Title
        story.append(Paragraph("DECLARATIONS", self.styles['InsuranceTitle']))
        story.append(Spacer(1, 0.25*inch))
        
        # Policy Information Table
        policy_data = [
            ['Policy Number:', data.get('policy_number', '')],
            ['Policy Period:', f"{data.get('effective_date', '')} to {data.get('expiration_date', '')}"],
            ['Named Insured:', data.get('company_name', '')],
            ['Address:', data.get('company_address', '')],
            ['Product:', data.get('product_name', '')],
        ]
        
        table = Table(policy_data, colWidths=[2*inch, 4*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('FONT', (0, 0), (-1, -1), 'Helvetica', 10),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(table)
        story.append(Spacer(1, 0.25*inch))
        
        # Coverage Limits
        story.append(Paragraph("COVERAGE LIMITS", self.styles['SectionHeader']))
        story.append(Spacer(1, 0.1*inch))
        
        # Premium Information
        story.append(Paragraph("PREMIUM SUMMARY", self.styles['SectionHeader']))
        premium_data = [
            ['Annual Premium:', f"${data.get('annual_premium', '0.00')}"],
            ['Policy Fee:', f"${data.get('policy_fee', '0.00')}"],
            ['Total:', f"${data.get('total_premium', '0.00')}"],
        ]
        
        premium_table = Table(premium_data, colWidths=[2*inch, 2*inch])
        premium_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONT', (0, -1), (1, -1), 'Helvetica-Bold', 10),
            ('LINEABOVE', (0, -1), (1, -1), 1, colors.black),
        ]))
        story.append(premium_table)
        
        # Forms and Endorsements
        story.append(PageBreak())
        story.append(Paragraph("FORMS AND ENDORSEMENTS", self.styles['SectionHeader']))
        story.append(Paragraph("The following forms and endorsements apply to this policy:", 
                              self.styles['Normal']))
        
        return story
    
    def _get_merge_data(self, policy: Policy) -> Dict:
        """Get all data needed for merging into templates"""
        quote = policy.quote
        app = quote.application
        company = app.company
        
        return {
            'policy_number': policy.policy_number,
            'effective_date': policy.effective_date.strftime('%m/%d/%Y'),
            'expiration_date': policy.expiration_date.strftime('%m/%d/%Y'),
            'company_name': company.company_name,
            'company_dba': company.dba_name or '',
            'company_address': self._format_company_address(company),
            'product_name': app.product.product_name,
            'product_code': app.product.document_code or '',
            'annual_premium': f"{policy.annual_premium:,.2f}",
            'total_premium': f"{policy.annual_premium:,.2f}",
            'policy_fee': '0.00',  # Add to model if needed
            'broker_name': app.broker.broker_name if app.broker else '',
            'quote_number': quote.quote_number,
            'state_code': self._get_state_code(policy),
        }
    
    def _get_state_code(self, policy: Policy) -> str:
        """Get state code from policy/company address"""
        # This would need to be implemented based on your address storage
        # For now, return a default
        return getattr(settings, 'DEFAULT_STATE_CODE', 'CA')
    
    def _format_company_address(self, company: Company) -> str:
        """Format company address for display"""
        # This would need to be implemented based on your address model
        return "123 Main St, City, ST 12345"  # Placeholder
    
    def _get_generation_data(self, policy: Policy) -> Dict:
        """Get snapshot of data for audit trail"""
        return {
            'generated_at': datetime.now().isoformat(),
            'policy_version': policy.version_number,
            'premium': str(policy.annual_premium),
            'user': policy.created_by.username if policy.created_by else 'system'
        }
    
    def _combine_pdfs(self, components: List[DocumentComponent]) -> bytes:
        """Combine all component PDFs into single document"""
        merger = PdfMerger()
        
        for component in components:
            if component.component_status == 'generated' and component.file_path:
                pdf_path = os.path.join(settings.MEDIA_ROOT, 'documents', component.file_path)
                if os.path.exists(pdf_path):
                    merger.append(pdf_path)
        
        output = io.BytesIO()
        merger.write(output)
        merger.close()
        output.seek(0)
        
        return output.read()
    
    def _save_component_file(self, component: DocumentComponent, content: bytes) -> str:
        """Save component PDF to storage"""
        date_path = datetime.now().strftime('%Y/%m')
        filename = f"{component.package.package_number}_{component.sequence_order:03d}.pdf"
        file_path = f"policy-components/{date_path}/{filename}"
        
        full_path = os.path.join(settings.MEDIA_ROOT, 'documents', file_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        with open(full_path, 'wb') as f:
            f.write(content)
        
        return file_path
    
    def _save_package(self, package: PolicyDocumentPackage, content: bytes) -> PolicyDocumentPackage:
        """Save combined package PDF"""
        date_path = datetime.now().strftime('%Y/%m')
        filename = f"{package.package_number}.pdf"
        file_path = f"policy-packages/{date_path}/{filename}"
        
        full_path = os.path.join(settings.MEDIA_ROOT, 'documents', file_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        with open(full_path, 'wb') as f:
            f.write(content)
        
        package.combined_pdf_path = file_path
        package.file_size = len(content)
        
        # Get total page count
        reader = PdfReader(io.BytesIO(content))
        package.total_pages = len(reader.pages)
        
        package.package_status = 'generated'
        package.save()
        
        return package
    
    def _supersede_previous_packages(self, policy: Policy, current_package: PolicyDocumentPackage):
        """Mark previous packages as superseded"""
        PolicyDocumentPackage.objects.filter(
            policy=policy,
            is_current=True
        ).exclude(
            package_id=current_package.package_id
        ).update(
            is_current=False,
            package_status='superseded'
        )
    
    def _get_static_pdf(self, template: DocumentTemplate) -> bytes:
        """Get static PDF content"""
        if template.storage_path:
            file_path = os.path.join(settings.MEDIA_ROOT, 'documents', 'templates', template.storage_path)
            if os.path.exists(file_path):
                with open(file_path, 'rb') as f:
                    return f.read()
        return b''
    
    def _fill_hybrid_pdf(self, template: DocumentTemplate, policy: Policy) -> bytes:
        """Fill a PDF form with data"""
        # This would use a library like pdfrw or fillpdf to fill form fields
        # For now, return the static PDF
        return self._get_static_pdf(template)
    
    def _render_html_template(self, template_content: str, data: Dict) -> str:
        """Render HTML template with data"""
        from django.template import Template, Context
        template = Template(template_content)
        context = Context(data)
        return template.render(context)
    
    def _html_to_story(self, html: str) -> List:
        """Convert HTML to ReportLab story"""
        # Simplified - you might want to use a library like xhtml2pdf
        return [Paragraph(html, self.styles['Normal'])]
    
    def _build_schedule_page(self, data: Dict) -> List:
        """Build schedule page story"""
        story = []
        story.append(Paragraph("SCHEDULE OF COVERAGES", self.styles['InsuranceTitle']))
        # Add schedule details
        return story