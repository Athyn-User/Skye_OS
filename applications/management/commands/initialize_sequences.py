# File: applications/management/commands/initialize_sequences.py
# Create the directory structure first:
# applications/management/__init__.py (empty file)
# applications/management/commands/__init__.py (empty file)
# applications/management/commands/initialize_sequences.py (this file)

from django.core.management.base import BaseCommand
from django.db import transaction
from applications.models import Product, SequenceTracker, Quote, Policy

class Command(BaseCommand):
    help = 'Initialize sequence trackers and update existing records'

    def handle(self, *args, **options):
        self.stdout.write('Initializing sequence tracking system...')
        
        # Define default product codes
        product_codes = {
            'Commercial Property': 'COM',
            'General Liability': 'GEN',
            'Professional Liability': 'PRO',
            'Auto/Fleet': 'AUT',
            'Umbrella/Excess': 'UMB',
            'Workers Compensation': 'WCP',
        }
        
        with transaction.atomic():
            # Step 1: Update Products with document codes
            self.stdout.write('Updating product document codes...')
            for product in Product.objects.all():
                # Try to match product name to get code
                for name_pattern, code in product_codes.items():
                    if name_pattern.lower() in product.product_name.lower():
                        product.document_code = code
                        product.save()
                        self.stdout.write(f'  - {product.product_name}: {code}')
                        break
                else:
                    # Default code if no match
                    product.document_code = 'GEN'
                    product.save()
                    self.stdout.write(f'  - {product.product_name}: GEN (default)')
            
            # Step 2: Create SequenceTracker entries
            self.stdout.write('\nCreating sequence trackers...')
            for name, code in product_codes.items():
                tracker, created = SequenceTracker.objects.get_or_create(
                    product_code=code,
                    defaults={
                        'product_name': name,
                        'last_used_number': 0,
                        'last_reserved_number': 0
                    }
                )
                if created:
                    self.stdout.write(f'  - Created tracker for {code} - {name}')
                else:
                    self.stdout.write(f'  - Tracker already exists for {code}')
            
            # Step 3: Analyze existing quotes and policies
            self.stdout.write('\nAnalyzing existing records...')
            existing_quotes = Quote.objects.all()
            existing_policies = Policy.objects.all()
            
            self.stdout.write(f'  - Found {existing_quotes.count()} existing quotes')
            self.stdout.write(f'  - Found {existing_policies.count()} existing policies')
            
            # Step 4: Update existing quotes with new numbering
            for i, quote in enumerate(existing_quotes, 1):
                product_code = quote.application.product.document_code or 'GEN'
                tracker = SequenceTracker.objects.get(product_code=product_code)
                
                # Assign base number
                quote.base_number = f'{i:05d}'
                quote.sequence_number = 0
                quote.version_number = None
                
                # Generate new quote number
                new_number = f"QTE-{product_code}-{quote.base_number}-00"
                self.stdout.write(f'  - Quote {quote.quote_number} -> {new_number}')
                quote.quote_number = new_number
                quote.save()
                
                # Update tracker
                tracker.last_used_number = i
                tracker.last_reserved_number = i
                tracker.save()
            
            # Step 5: Update existing policies with new numbering
            for policy in existing_policies:
                if policy.quote:
                    # Inherit from quote
                    policy.base_number = policy.quote.base_number
                    policy.sequence_number = 0  # Original policy
                    policy.version_number = None
                    
                    product_code = policy.quote.application.product.document_code or 'GEN'
                    new_number = f"POL-{product_code}-{policy.base_number}-00"
                    self.stdout.write(f'  - Policy {policy.policy_number} -> {new_number}')
                    policy.policy_number = new_number
                    policy.save()
            
            self.stdout.write(self.style.SUCCESS('\nSequence tracking system initialized successfully!'))