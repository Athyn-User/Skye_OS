# File: applications/endorsement_generator.py
# New file for endorsement generation

from django.db import transaction
from datetime import datetime
import io
import os

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib import colors

from .document_models import EndorsementDocument, DocumentTemplate
from .models import Policy


class EndorsementGenerator:
    """Generate endorsement documents"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
    
    def create_endorsement(self, policy: Policy, template_code: str, 
                          endorsement_data: dict, effective_date=None):
        """Create an endorsement for a policy"""
        
        with transaction.atomic():
            # Get template
            template = DocumentTemplate.objects.get(template_code=template_code)
            
            # Get next endorsement sequence
            last_endorsement = EndorsementDocument.objects.filter(
                policy=policy
            ).order_by('-endorsement_sequence').first()
            
            next_sequence = (last_endorsement.endorsement_sequence + 1) if last_endorsement else 1
            
            # Create endorsement record
            endorsement = EndorsementDocument(
                policy=policy,
                template=template,
                endorsement_sequence=next_sequence,
                endorsement_title=template.template_name,
                effective_date=effective_date or datetime.now().date(),
                endorsement_data=endorsement_data
            )
            endorsement.endorsement_number = endorsement.generate_endorsement_number()
            endorsement.save()
            
            # Generate PDF
            pdf_content = self._generate_endorsement_pdf(endorsement)
            
            # Save PDF
            file_path = self._save_endorsement_file(endorsement, pdf_content)
            endorsement.document_path = file_path
            endorsement.save()
            
            return endorsement
    
    def _generate_endorsement_pdf(self, endorsement: EndorsementDocument) -> bytes:
        """Generate the endorsement PDF"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        story = []
        
        # Title
        title_style = self.styles['Title']
        story.append(Paragraph("ENDORSEMENT", title_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Endorsement info table
        info_data = [
            ['Endorsement Number:', endorsement.endorsement_number],
            ['Policy Number:', endorsement.policy.policy_number],
            ['Effective Date:', endorsement.effective_date.strftime('%B %d, %Y')],
            ['Named Insured:', endorsement.policy.quote.application.company.company_name],
        ]
        
        # Add custom data fields
        for key, value in endorsement.endorsement_data.items():
            if key == 'additional_insured_name':
                info_data.append(['Additional Insured:', value])
            elif key == 'additional_insured_address':
                info_data.append(['Address:', value])
            elif key == 'description':
                info_data.append(['Description:', value])
        
        info_table = Table(info_data, colWidths=[2*inch, 4*inch])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('FONT', (0, 0), (-1, -1), 'Helvetica', 10),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(info_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Endorsement text
        story.append(Paragraph(endorsement.endorsement_title, self.styles['Heading2']))
        story.append(Spacer(1, 0.1*inch))
        
        # Standard endorsement language (customize per template)
        if 'ADD-INSURED' in endorsement.template.template_code:
            text = f"""This endorsement modifies insurance provided under the following:
            <br/><br/>
            {endorsement.policy.quote.application.product.product_name}
            <br/><br/>
            The following is added as an Additional Insured under this policy:
            <br/><br/>
            <b>{endorsement.endorsement_data.get('additional_insured_name', '')}</b><br/>
            {endorsement.endorsement_data.get('additional_insured_address', '')}
            <br/><br/>
            But only with respect to liability arising out of the operations of the Named Insured.
            <br/><br/>
            All other terms and conditions of this policy remain unchanged.
            """
        elif 'WAIVER-SUB' in endorsement.template.template_code:
            text = """This endorsement modifies insurance provided under the following:
            <br/><br/>
            We waive any right of recovery we may have against the person or organization 
            shown in the Schedule because of payments we make for injury or damage arising 
            out of your ongoing operations or your work done under a contract with that 
            person or organization and included in the "products-completed operations hazard".
            <br/><br/>
            All other terms and conditions of this policy remain unchanged.
            """
        else:
            text = "This endorsement modifies the insurance provided under this policy."
        
        story.append(Paragraph(text, self.styles['Normal']))
        
        # Footer
        story.append(Spacer(1, 1*inch))
        story.append(Paragraph(f"Endorsement {endorsement.endorsement_number} - Page 1 of 1", 
                              self.styles['Normal']))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer.read()
    
    def _save_endorsement_file(self, endorsement: EndorsementDocument, content: bytes) -> str:
        """Save endorsement PDF to storage"""
        from django.conf import settings
        
        date_path = datetime.now().strftime('%Y/%m')
        filename = f"{endorsement.endorsement_number}.pdf"
        file_path = f"endorsements/{date_path}/{filename}"
        
        full_path = os.path.join(settings.MEDIA_ROOT, 'documents', file_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        with open(full_path, 'wb') as f:
            f.write(content)
        
        return file_path