# File: applications/management/commands/load_document_templates.py
# Management command to load initial document templates

from django.core.management.base import BaseCommand
from django.db import transaction
from datetime import date
from applications.document_models import DocumentTemplate
from applications.models import Product

class Command(BaseCommand):
    help = 'Load initial document templates for policies'

    def handle(self, *args, **options):
        self.stdout.write('Loading document templates...')
        
        with transaction.atomic():
            # Get products
            products = Product.objects.all()
            if not products.exists():
                self.stdout.write(self.style.ERROR('No products found. Please create products first.'))
                return
            
            # For each product, create standard templates
            for product in products:
                self.create_templates_for_product(product)
            
            self.stdout.write(self.style.SUCCESS('Document templates loaded successfully!'))
    
    def create_templates_for_product(self, product):
        """Create standard templates for a product"""
        
        # 1. Declaration Page (Dynamic)
        DocumentTemplate.objects.get_or_create(
            template_code=f'DEC-{product.document_code or "GEN"}-001',
            defaults={
                'template_name': f'{product.product_name} Declaration Page',
                'template_type': 'declaration',
                'template_format': 'dynamic',
                'product': product,
                'version': '1.0',
                'effective_date': date(2024, 1, 1),
                'default_sequence': 10,
                'merge_fields': {
                    'policy_number': 'policy.policy_number',
                    'company_name': 'policy.quote.application.company.company_name',
                    'effective_date': 'policy.effective_date',
                    'expiration_date': 'policy.expiration_date',
                    'premium': 'policy.annual_premium',
                }
            }
        )
        self.stdout.write(f'  - Created declaration template for {product.product_name}')
        
        # 2. Standard Policy Form (Static - placeholder)
        DocumentTemplate.objects.get_or_create(
            template_code=f'FORM-{product.document_code or "GEN"}-001',
            defaults={
                'template_name': f'{product.product_name} Standard Policy Form',
                'template_type': 'policy_form',
                'template_format': 'static',
                'product': product,
                'storage_path': f'forms/{product.product_code}/standard-form.pdf',
                'version': '1.0',
                'effective_date': date(2024, 1, 1),
                'default_sequence': 100,
            }
        )
        
        # 3. Common Endorsements
        endorsements = [
            ('END-ADD-INSURED', 'Additional Insured', 'endorsement'),
            ('END-WAIVER-SUB', 'Waiver of Subrogation', 'endorsement'),
            ('END-PRIMARY', 'Primary and Non-Contributory', 'endorsement'),
            ('END-BLANKET-ADD', 'Blanket Additional Insured', 'endorsement'),
        ]
        
        for code_suffix, name, template_type in endorsements:
            DocumentTemplate.objects.get_or_create(
                template_code=f'{code_suffix}-{product.document_code or "GEN"}',
                defaults={
                    'template_name': f'{name} - {product.product_name}',
                    'template_type': template_type,
                    'template_format': 'hybrid',
                    'product': product,
                    'version': '1.0',
                    'effective_date': date(2024, 1, 1),
                    'default_sequence': 200,
                    'merge_fields': {
                        'policy_number': 'policy.policy_number',
                        'endorsement_number': 'endorsement.endorsement_number',
                        'effective_date': 'endorsement.effective_date',
                        'additional_insured_name': 'endorsement.endorsement_data.additional_insured_name',
                    }
                }
            )
        self.stdout.write(f'  - Created endorsement templates for {product.product_name}')
        
        # 4. State-specific forms (examples for CA and NY)
        state_forms = [
            ('CA', 'CA-NOTICE-001', 'California Workers Comp Notice'),
            ('CA', 'CA-DISCLOSURE-001', 'California Coverage Disclosure'),
            ('NY', 'NY-NOTICE-001', 'New York Statutory Notice'),
            ('NY', 'NY-WC-FORM-001', 'New York Workers Comp Form'),
        ]
        
        for state, code, name in state_forms:
            # Only create if product is Workers Comp (WCP)
            if product.document_code == 'WCP':
                DocumentTemplate.objects.get_or_create(
                    template_code=code,
                    defaults={
                        'template_name': name,
                        'template_type': 'state_form',
                        'template_format': 'static',
                        'product': product,
                        'applicable_states': state,
                        'is_state_mandatory': True,
                        'storage_path': f'forms/states/{state.lower()}/{code.lower()}.pdf',
                        'version': '2024.1',
                        'effective_date': date(2024, 1, 1),
                        'default_sequence': 300,
                    }
                )
        
        if product.document_code == 'WCP':
            self.stdout.write(f'  - Created state-specific forms for {product.product_name}')