from django.http import HttpResponse
from django.template.loader import get_template
from django.shortcuts import get_object_or_404
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.units import inch
from io import BytesIO
import os
from django.conf import settings
from applications.models import Quote, Application
from datetime import datetime

class QuotePDFGenerator:
    def __init__(self):
        self.width, self.height = letter
        self.styles = getSampleStyleSheet()
        
    def generate_quote_pdf(self, quote_id):
        quote = get_object_or_404(Quote, pk=quote_id)
        application = quote.application
        company = application.company
        
        # Create BytesIO buffer
        buffer = BytesIO()
        
        # Create PDF document
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        # Build PDF content
        story = []
        
        # Header with company branding
        story.append(self._create_header())
        story.append(Spacer(1, 20))
        
        # Quote title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.darkblue,
            spaceAfter=30
        )
        story.append(Paragraph(f"Insurance Quote #{quote.quote_number}", title_style))
        
        # Quote details table
        story.append(self._create_quote_details(quote, application, company))
        story.append(Spacer(1, 20))
        
        # Coverage details
        story.append(self._create_coverage_section(quote, application))
        story.append(Spacer(1, 20))
        
        # Premium breakdown
        story.append(self._create_premium_section(quote))
        story.append(Spacer(1, 20))
        
        # Terms and conditions
        story.append(self._create_terms_section(quote))
        
        # Footer
        story.append(Spacer(1, 30))
        story.append(self._create_footer())
        
        # Build PDF
        doc.build(story)
        
        # Get PDF data
        pdf_data = buffer.getvalue()
        buffer.close()
        
        return pdf_data
    
    def _create_header(self):
        # Company header with logo placeholder
        header_data = [
            ['SKYE INSURANCE GROUP', ''],
            ['Professional Insurance Solutions', 'Quote Date: ' + datetime.now().strftime('%B %d, %Y')],
            ['Phone: (555) 123-4567', 'Email: quotes@skyeinsurance.com'],
            ['www.skyeinsurance.com', '']
        ]
        
        header_table = Table(header_data, colWidths=[4*inch, 2*inch])
        header_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (0, 0), 16),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (0, 0), colors.darkblue),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        return header_table
    
    def _create_quote_details(self, quote, application, company):
        # Quote and company details
        details_data = [
            ['QUOTE DETAILS', ''],
            ['Quote Number:', quote.quote_number],
            ['Application Number:', application.application_number],
            ['Quote Version:', str(quote.quote_version)],
            ['Effective Date:', quote.effective_date.strftime('%B %d, %Y')],
            ['Expiration Date:', quote.expiration_date.strftime('%B %d, %Y')],
            ['', ''],
            ['INSURED INFORMATION', ''],
            ['Company Name:', company.company_name],
            ['Industry:', company.industry_description or 'Not specified'],
            ['Employee Count:', str(company.employee_count) if company.employee_count else 'Not specified'],
            ['Annual Revenue:', f'${company.annual_revenue:,.0f}' if company.annual_revenue else 'Not disclosed'],
        ]
        
        if application.broker:
            details_data.extend([
                ['', ''],
                ['BROKER INFORMATION', ''],
                ['Broker:', application.broker.broker_name],
                ['Broker Code:', application.broker.broker_code or ''],
            ])
        
        details_table = Table(details_data, colWidths=[2*inch, 4*inch])
        details_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 7), (0, 7), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (0, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 7), (0, 7), colors.darkblue),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LINEBELOW', (0, 0), (-1, 0), 1, colors.darkblue),
            ('LINEBELOW', (0, 7), (-1, 7), 1, colors.darkblue),
        ]))
        
        return details_table
    
    def _create_coverage_section(self, quote, application):
        # Coverage details
        coverage_data = [
            ['COVERAGE DETAILS', '', ''],
            ['Product:', application.product.product_name, ''],
            ['Coverage Type:', 'Comprehensive Insurance Coverage', ''],
            ['Policy Term:', '12 Months', ''],
            ['', '', ''],
            ['COVERAGE LIMITS', 'AMOUNT', 'DEDUCTIBLE'],
            ['General Liability', '$1,000,000 per occurrence', '$1,000'],
            ['Product Liability', '$2,000,000 aggregate', '$2,500'],
            ['Property Coverage', '$500,000', '$1,000'],
        ]
        
        coverage_table = Table(coverage_data, colWidths=[2.5*inch, 2*inch, 1.5*inch])
        coverage_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 5), (-1, 5), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 5), (-1, 5), colors.darkblue),
            ('ALIGN', (1, 5), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LINEBELOW', (0, 0), (-1, 0), 1, colors.darkblue),
            ('LINEBELOW', (0, 5), (-1, 5), 1, colors.darkblue),
            ('GRID', (0, 6), (-1, -1), 0.5, colors.grey),
        ]))
        
        return coverage_table
    
    def _create_premium_section(self, quote):
        # Premium breakdown
        commission = quote.commission_amount or 0
        base_premium = float(quote.total_premium) - float(commission)
        
        premium_data = [
            ['PREMIUM BREAKDOWN', ''],
            ['Base Premium:', f'${base_premium:,.2f}'],
            ['Commission:', f'${commission:,.2f}'],
            ['Taxes & Fees:', '$150.00'],
            ['', ''],
            ['TOTAL PREMIUM:', f'${quote.total_premium:,.2f}'],
        ]
        
        premium_table = Table(premium_data, colWidths=[3*inch, 2*inch])
        premium_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 5), (-1, 5), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 4), 10),
            ('FONTSIZE', (0, 5), (-1, 5), 14),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 5), (-1, 5), colors.darkgreen),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LINEBELOW', (0, 0), (-1, 0), 1, colors.darkblue),
            ('LINEABOVE', (0, 5), (-1, 5), 2, colors.darkgreen),
        ]))
        
        return premium_table
    
    def _create_terms_section(self, quote):
        terms_text = """
        <b>TERMS AND CONDITIONS</b><br/><br/>
        1. This quote is valid for 30 days from the quote date.<br/>
        2. Coverage is subject to underwriting approval and final policy terms.<br/>
        3. Premium is subject to audit and may be adjusted based on actual exposures.<br/>
        4. Policy terms and conditions will govern in case of claim.<br/>
        5. All coverage is subject to policy limits, deductibles, and exclusions.<br/><br/>
        <b>NEXT STEPS</b><br/><br/>
        To accept this quote and bind coverage, please contact us at quotes@skyeinsurance.com 
        or call (555) 123-4567. We will need signed applications and any additional 
        underwriting information before binding coverage.
        """
        
        if quote.special_conditions:
            terms_text += f"<br/><br/><b>SPECIAL CONDITIONS</b><br/><br/>{quote.special_conditions}"
        
        terms_style = ParagraphStyle(
            'Terms',
            parent=self.styles['Normal'],
            fontSize=9,
            leading=12
        )
        
        return Paragraph(terms_text, terms_style)
    
    def _create_footer(self):
        footer_text = """
        <i>This quote is provided by Skye Insurance Group. All coverage subject to policy terms, 
        conditions, and underwriting approval. Please review all terms carefully before acceptance.</i>
        """
        
        footer_style = ParagraphStyle(
            'Footer',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=colors.grey,
            alignment=1  # Center alignment
        )
        
        return Paragraph(footer_text, footer_style)
