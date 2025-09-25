# File: applications/endorsement_generator.py
# Enhanced endorsement generator with standard header variables

from django.shortcuts import get_object_or_404
from django.template import Template, Context
from django.utils import timezone
from django.conf import settings
from datetime import datetime
import os
import logging

from .models import Policy
from .document_models import DocumentTemplate, EndorsementDocument
from .document_service import EnhancedDocumentService

logger = logging.getLogger(__name__)

class EndorsementGenerator:
    """Generate endorsements with standard header variables"""
    
    # Standard header template for ALL endorsements
    STANDARD_ENDORSEMENT_HEADER = """
    <div class="endorsement-header" style="page-break-inside: avoid; margin-bottom: 20px;">
        <table style="width: 100%; border-collapse: collapse; font-family: Arial, sans-serif; font-size: 11px;">
            <tr>
                <td style="width: 60%; padding: 12px; border: 2px solid black; vertical-align: top;">
                    <strong style="font-size: 12px;">NAMED INSURED:</strong><br>
                    {{ named_insured.company_name }}<br>
                    {{ named_insured.address }}<br>
                    {{ named_insured.city }}, {{ named_insured.state }} {{ named_insured.zip_code }}
                </td>
                <td style="width: 40%; padding: 12px; border: 2px solid black; vertical-align: top;">
                    <div style="margin-bottom: 8px;">
                        <strong>POLICY NUMBER:</strong><br>
                        {{ policy_number }}
                    </div>
                    <div style="margin-bottom: 8px;">
                        <strong>ENDORSEMENT NUMBER:</strong><br>
                        {{ endorsement_number }}
                    </div>
                    <div>
                        <strong>ENDORSEMENT EFFECTIVE DATE:</strong><br>
                        {{ endorsement_effective_date }}
                    </div>
                </td>
            </tr>
        </table>
    </div>
    """
    
    def __init__(self):
        self.document_service = EnhancedDocumentService()
    
    def create_endorsement(self, policy: Policy, template_code: str, 
                          endorsement_data: dict, effective_date=None):
        """Create an endorsement with standard header"""
        try:
            # Get the endorsement template
            template = DocumentTemplate.objects.get(
                template_code=template_code,
                template_type='endorsement',
                is_active=True
            )
            
            # Generate endorsement number
            endorsement_number = self._generate_endorsement_number(policy)
            
            # Prepare all template data
            template_data = self._prepare_endorsement_data(
                policy, template, endorsement_data, 
                endorsement_number, effective_date
            )
            
            # Generate the endorsement document
            success, result = self._generate_endorsement_document(
                policy, template, template_data, endorsement_number, effective_date
            )
            
            if success:
                # Create endorsement record
                endorsement = EndorsementDocument.objects.create(
                    policy=policy,
                    template=template,
                    endorsement_number=endorsement_number,
                    endorsement_sequence=self._get_next_sequence(policy),
                    endorsement_title=template.template_name,
                    effective_date=effective_date or timezone.now().date(),
                    document_path=result['file_path'],
                    endorsement_data=endorsement_data
                )
                
                logger.info(f"Endorsement {endorsement_number} created successfully")
                return endorsement
            else:
                raise Exception(result.get('error', 'Failed to generate endorsement document'))
                
        except Exception as e:
            logger.error(f"Error creating endorsement: {str(e)}")
            raise
    
    def _prepare_endorsement_data(self, policy: Policy, template: DocumentTemplate, 
                                 endorsement_data: dict, endorsement_number: str, 
                                 effective_date=None):
        """Prepare complete data context for endorsement template"""
        
        # Get company information
        company = policy.quote.application.company
        
        # Standard header data that appears on ALL endorsements
        standard_data = {
            'named_insured': {
                'company_name': company.company_name,
                'address': getattr(company, 'address', 'Address on file'),
                'city': getattr(company, 'city', 'City'),
                'state': getattr(company, 'state', 'ST'),
                'zip_code': getattr(company, 'zip_code', '00000')
            },
            'policy_number': policy.policy_number,
            'endorsement_number': endorsement_number,
            'endorsement_effective_date': (effective_date or timezone.now().date()).strftime('%B %d, %Y'),
            
            # Additional policy context
            'policy': {
                'effective_date': policy.effective_date.strftime('%B %d, %Y'),
                'expiration_date': policy.expiration_date.strftime('%B %d, %Y'),
                'annual_premium': policy.annual_premium,
                'status': policy.policy_status
            },
            
            # Product information
            'product': {
                'name': policy.quote.application.product.product_name,
                'code': policy.quote.application.product.product_code
            },
            
            # Template information
            'template': {
                'name': template.template_name,
                'code': template.template_code,
                'type': template.template_type
            },
            
            # Generation metadata
            'generated_date': timezone.now().strftime('%B %d, %Y at %I:%M %p'),
            'generated_by': 'Skye Insurance Group',
            
            # Custom endorsement data (from form)
            'endorsement_data': endorsement_data
        }
        
        return standard_data
    
    def _generate_endorsement_document(self, policy: Policy, template: DocumentTemplate, 
                                     template_data: dict, endorsement_number: str, 
                                     effective_date=None):
        """Generate the actual endorsement PDF document"""
        try:
            # Combine standard header with template content
            if template.template_format == 'hybrid':
                # For hybrid templates, we'll fill PDF form fields
                return self._generate_hybrid_endorsement(template, template_data, endorsement_number)
            elif template.template_format == 'dynamic':
                # For dynamic templates, combine header with template HTML
                return self._generate_dynamic_endorsement(template, template_data, endorsement_number)
            else:
                # For static templates, overlay header on existing PDF
                return self._generate_static_endorsement(template, template_data, endorsement_number)
                
        except Exception as e:
            logger.error(f"Error generating endorsement document: {str(e)}")
            return False, {'error': str(e)}
    
    def _generate_hybrid_endorsement(self, template: DocumentTemplate, 
                                   template_data: dict, endorsement_number: str):
        """Generate hybrid endorsement (fillable PDF)"""
        try:
            # Check if template has a PDF file
            if not hasattr(template, 'storage_path') or not template.storage_path:
                return self._generate_basic_endorsement_pdf(template, template_data, endorsement_number)
            
            template_file = os.path.join(settings.MEDIA_ROOT, 'documents', template.storage_path)
            if not os.path.exists(template_file):
                return self._generate_basic_endorsement_pdf(template, template_data, endorsement_number)
            
            # For now, create a basic PDF with header (you can enhance with PDF form filling)
            return self._generate_basic_endorsement_pdf(template, template_data, endorsement_number)
            
        except Exception as e:
            logger.error(f"Error generating hybrid endorsement: {str(e)}")
            return False, {'error': str(e)}
    
    def _generate_dynamic_endorsement(self, template: DocumentTemplate, 
                                    template_data: dict, endorsement_number: str):
        """Generate dynamic endorsement from HTML template"""
        try:
            # Combine standard header with template content
            template_content = template.html_template if hasattr(template, 'html_template') and template.html_template else ""
            
            full_template = self.STANDARD_ENDORSEMENT_HEADER + template_content
            
            # Render template with data
            django_template = Template(full_template)
            context = Context(template_data)
            rendered_html = django_template.render(context)
            
            # Convert HTML to PDF
            return self._html_to_pdf(rendered_html, endorsement_number)
            
        except Exception as e:
            logger.error(f"Error generating dynamic endorsement: {str(e)}")
            return False, {'error': str(e)}
    
    def _generate_static_endorsement(self, template: DocumentTemplate, 
                                   template_data: dict, endorsement_number: str):
        """Generate static endorsement by overlaying header on PDF"""
        try:
            # For now, generate basic PDF (you can enhance with PDF overlay)
            return self._generate_basic_endorsement_pdf(template, template_data, endorsement_number)
            
        except Exception as e:
            logger.error(f"Error generating static endorsement: {str(e)}")
            return False, {'error': str(e)}
    
    def _generate_basic_endorsement_pdf(self, template: DocumentTemplate, 
                                      template_data: dict, endorsement_number: str):
        """Generate basic endorsement PDF using ReportLab"""
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
            from reportlab.lib.units import inch
            from reportlab.lib import colors
            import io
            
            # Create PDF buffer
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=1*inch)
            
            # Build document elements
            elements = []
            styles = getSampleStyleSheet()
            
            # Standard Header Table
            header_data = [
                ['NAMED INSURED:', 'POLICY NUMBER:'],
                [template_data['named_insured']['company_name'], template_data['policy_number']],
                [f"{template_data['named_insured']['address']}", 'ENDORSEMENT NUMBER:'],
                [f"{template_data['named_insured']['city']}, {template_data['named_insured']['state']} {template_data['named_insured']['zip_code']}", 
                 template_data['endorsement_number']],
                ['', 'ENDORSEMENT EFFECTIVE DATE:'],
                ['', template_data['endorsement_effective_date']]
            ]
            
            header_table = Table(header_data, colWidths=[4*inch, 2.5*inch])
            header_table.setStyle(TableStyle([
                ('BOX', (0, 0), (-1, -1), 2, colors.black),
                ('INNERGRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('LEFTPADDING', (0, 0), (-1, -1), 12),
                ('RIGHTPADDING', (0, 0), (-1, -1), 12),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ]))
            
            elements.append(header_table)
            elements.append(Spacer(1, 0.3*inch))
            
            # Endorsement Title
            title_style = styles['Heading1']
            title_style.alignment = 1  # Center
            title = Paragraph(template.template_name.upper(), title_style)
            elements.append(title)
            elements.append(Spacer(1, 0.2*inch))
            
            # Endorsement Content
            content_style = styles['Normal']
            
            # Add specific content based on endorsement type
            if 'additional_insured' in template.template_code.lower():
                content_text = f"""
                This endorsement modifies insurance provided under the following:
                
                <b>POLICY NUMBER:</b> {template_data['policy_number']}<br/>
                <b>NAMED INSURED:</b> {template_data['named_insured']['company_name']}<br/>
                <b>EFFECTIVE DATE:</b> {template_data['endorsement_effective_date']}<br/>
                
                <b>ADDITIONAL INSURED:</b><br/>
                {template_data['endorsement_data'].get('additional_insured_name', 'TO BE COMPLETED')}<br/>
                {template_data['endorsement_data'].get('additional_insured_address', 'Address to be provided')}
                
                <br/><br/>
                This endorsement adds the above named person or organization as an additional insured 
                under the General Liability Coverage of this policy, but only with respect to liability 
                arising out of operations performed by or on behalf of the named insured.
                """
            elif 'waiver' in template.template_code.lower():
                content_text = f"""
                This endorsement modifies insurance provided under the following:
                
                <b>POLICY NUMBER:</b> {template_data['policy_number']}<br/>
                <b>NAMED INSURED:</b> {template_data['named_insured']['company_name']}<br/>
                <b>EFFECTIVE DATE:</b> {template_data['endorsement_effective_date']}<br/>
                
                <b>WAIVER OF SUBROGATION:</b><br/>
                The insurer waives all rights of subrogation against:
                {template_data['endorsement_data'].get('waiver_party', 'TO BE COMPLETED')}
                
                <br/><br/>
                This waiver applies only to the extent that such waiver is permitted by law.
                """
            else:
                # Generic endorsement content
                content_text = f"""
                This endorsement modifies insurance provided under the following:
                
                <b>POLICY NUMBER:</b> {template_data['policy_number']}<br/>
                <b>NAMED INSURED:</b> {template_data['named_insured']['company_name']}<br/>
                <b>EFFECTIVE DATE:</b> {template_data['endorsement_effective_date']}<br/>
                
                <br/>
                {template_data['endorsement_data'].get('description', 'Endorsement details to be specified.')}
                """
            
            content = Paragraph(content_text, content_style)
            elements.append(content)
            
            # Footer
            elements.append(Spacer(1, 0.5*inch))
            footer_style = styles['Normal']
            footer_style.fontSize = 8
            footer_style.alignment = 1  # Center
            footer = Paragraph(f"Generated on {template_data['generated_date']} by {template_data['generated_by']}", footer_style)
            elements.append(footer)
            
            # Build PDF
            doc.build(elements)
            
            # Save to file
            pdf_content = buffer.getvalue()
            buffer.close()
            
            filename = f"{endorsement_number}_{template.template_code}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            dest_dir = os.path.join(settings.MEDIA_ROOT, 'documents', 'endorsements')
            os.makedirs(dest_dir, exist_ok=True)
            dest_path = os.path.join(dest_dir, filename)
            
            with open(dest_path, 'wb') as f:
                f.write(pdf_content)
            
            return True, {
                'file_path': f'endorsements/{filename}',
                'file_size': len(pdf_content),
                'page_count': 1
            }
            
        except Exception as e:
            logger.error(f"Error generating basic endorsement PDF: {str(e)}")
            return False, {'error': str(e)}
    
    def _html_to_pdf(self, html_content: str, endorsement_number: str):
        """Convert HTML to PDF using weasyprint or similar"""
        try:
            # For now, fall back to basic PDF generation
            # In production, you'd use weasyprint or similar
            template_data = {'endorsement_number': endorsement_number}
            return self._generate_basic_endorsement_pdf(None, template_data, endorsement_number)
            
        except Exception as e:
            logger.error(f"Error converting HTML to PDF: {str(e)}")
            return False, {'error': str(e)}
    
    def _generate_endorsement_number(self, policy: Policy):
        """Generate endorsement number"""
        # Get the next sequence number for this policy
        existing_endorsements = EndorsementDocument.objects.filter(
            policy=policy
        ).count()
        
        next_sequence = existing_endorsements + 1
        
        # Format: END-WCP-000001-01
        base_number = policy.policy_number.replace('POL-', 'END-')
        return f"{base_number}-{next_sequence:02d}"
    
    def _get_next_sequence(self, policy: Policy):
        """Get next endorsement sequence number"""
        max_sequence = EndorsementDocument.objects.filter(
            policy=policy
        ).aggregate(
            max_seq=models.Max('endorsement_sequence')
        )['max_seq'] or 0
        
        return max_sequence + 1
    
    def create_sample_endorsements(self, policy: Policy):
        """Create sample endorsements for testing"""
        try:
            # Additional Insured Endorsement
            additional_insured_data = {
                'additional_insured_name': 'ABC Construction Company',
                'additional_insured_address': '123 Main Street\nAnytown, CA 90210',
                'description': 'Additional insured endorsement for construction project'
            }
            
            # Waiver of Subrogation Endorsement  
            waiver_data = {
                'waiver_party': 'XYZ Property Management LLC',
                'description': 'Waiver of subrogation endorsement for lease agreement'
            }
            
            endorsements_created = []
            
            # Try to create endorsements if templates exist
            try:
                endorsement1 = self.create_endorsement(
                    policy=policy,
                    template_code='END-ADD-INSURED-' + policy.quote.application.product.document_code,
                    endorsement_data=additional_insured_data,
                    effective_date=timezone.now().date()
                )
                endorsements_created.append(endorsement1)
            except DocumentTemplate.DoesNotExist:
                logger.warning("Additional insured template not found")
            
            try:
                endorsement2 = self.create_endorsement(
                    policy=policy,
                    template_code='END-WAIVER-SUB-' + policy.quote.application.product.document_code,
                    endorsement_data=waiver_data,
                    effective_date=timezone.now().date()
                )
                endorsements_created.append(endorsement2)
            except DocumentTemplate.DoesNotExist:
                logger.warning("Waiver of subrogation template not found")
            
            return endorsements_created
            
        except Exception as e:
            logger.error(f"Error creating sample endorsements: {str(e)}")
            return []