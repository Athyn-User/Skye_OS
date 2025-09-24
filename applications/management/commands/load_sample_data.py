from django.core.management.base import BaseCommand
from applications.models import Company, Broker, Product, Application, Quote
from django.db import connection
from datetime import date, timedelta
import random

class Command(BaseCommand):
    help = 'Load sample insurance data'

    def handle(self, *args, **options):
        # First, let's create a venture if none exists
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM ventures")
            venture_count = cursor.fetchone()[0]
            
            if venture_count == 0:
                cursor.execute("""
                    INSERT INTO ventures (venture_name, venture_code, is_active, created_at, updated_at) 
                    VALUES ('Skye Insurance Group', 'SIG', true, NOW(), NOW())
                    RETURNING venture_id
                """)
                venture_id = cursor.fetchone()[0]
                self.stdout.write(f'Created venture: Skye Insurance Group (ID: {venture_id})')
            else:
                cursor.execute("SELECT venture_id FROM ventures WHERE is_active = true LIMIT 1")
                venture_id = cursor.fetchone()[0]
                self.stdout.write(f'Using existing venture ID: {venture_id}')

            # Create coverage types if they don't exist
            cursor.execute("SELECT COUNT(*) FROM coverage_types")
            coverage_count = cursor.fetchone()[0]
            
            coverage_types = {}
            if coverage_count == 0:
                coverage_data = [
                    ('General Liability', 'casualty'),
                    ('Property', 'property'),
                    ('Workers Compensation', 'workers_comp'),
                    ('Cyber Liability', 'cyber')
                ]
                for name, category in coverage_data:
                    cursor.execute("""
                        INSERT INTO coverage_types (coverage_name, coverage_category, is_active, created_at) 
                        VALUES (%s, %s, true, NOW()) 
                        RETURNING coverage_type_id
                    """, [name, category])
                    coverage_id = cursor.fetchone()[0]
                    coverage_types[category] = coverage_id
                    self.stdout.write(f'Created coverage type: {name} (ID: {coverage_id})')
            else:
                cursor.execute("SELECT coverage_type_id, coverage_category FROM coverage_types WHERE is_active = true")
                for row in cursor.fetchall():
                    coverage_types[row[1]] = row[0]

        # Create sample companies
        companies_data = [
            {'company_name': 'ABC Manufacturing Inc', 'company_type': 'corporation', 'employee_count': 150, 'annual_revenue': 25000000},
            {'company_name': 'XYZ Logistics LLC', 'company_type': 'llc', 'employee_count': 75, 'annual_revenue': 12000000},
            {'company_name': 'Tech Solutions Corp', 'company_type': 'corporation', 'employee_count': 200, 'annual_revenue': 35000000},
            {'company_name': 'Green Energy Partners', 'company_type': 'partnership', 'employee_count': 50, 'annual_revenue': 8000000},
        ]
        
        for data in companies_data:
            company, created = Company.objects.get_or_create(
                company_name=data['company_name'],
                defaults=data
            )
            if created:
                self.stdout.write(f'Created company: {company.company_name}')

        # Create sample brokers
        brokers_data = [
            {'broker_name': 'Premium Insurance Brokers', 'broker_code': 'PIB', 'broker_type': 'retail'},
            {'broker_name': 'Commercial Risk Advisors', 'broker_code': 'CRA', 'broker_type': 'wholesale'},
            {'broker_name': 'Elite Coverage Solutions', 'broker_code': 'ECS', 'broker_type': 'retail'},
        ]
        
        for data in brokers_data:
            broker, created = Broker.objects.get_or_create(
                broker_code=data['broker_code'],
                defaults=data
            )
            if created:
                self.stdout.write(f'Created broker: {broker.broker_name}')

        # Create sample products with required fields
        products_data = [
            {'product_name': 'General Liability Premium', 'product_code': 'GL-PREM', 'coverage_type': 'casualty'},
            {'product_name': 'Commercial Property', 'product_code': 'PROP-COM', 'coverage_type': 'property'},
            {'product_name': 'Workers Compensation', 'product_code': 'WC-STD', 'coverage_type': 'workers_comp'},
            {'product_name': 'Cyber Liability Plus', 'product_code': 'CYBER-PLUS', 'coverage_type': 'cyber'},
        ]
        
        for data in products_data:
            product_data = {
                'product_name': data['product_name'],
                'product_code': data['product_code'],
                'venture_id': venture_id,
                'coverage_type_id': coverage_types.get(data['coverage_type'], coverage_types[list(coverage_types.keys())[0]]),
                'description': f"{data['product_name']} insurance coverage"
            }
            
            product, created = Product.objects.get_or_create(
                product_code=data['product_code'],
                defaults=product_data
            )
            if created:
                self.stdout.write(f'Created product: {product.product_name}')

        self.stdout.write(self.style.SUCCESS('Sample data loaded successfully!'))
