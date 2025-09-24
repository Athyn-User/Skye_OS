from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = "Create certificate management tables"

    def handle(self, *args, **options):
        sql_commands = [
            """
            CREATE SEQUENCE IF NOT EXISTS certificate_number_seq START 1;
            """,
            """
            CREATE TABLE IF NOT EXISTS public.certificate_templates (
                template_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                template_name TEXT NOT NULL,
                template_type TEXT NOT NULL,
                description TEXT,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS public.certificates (
                certificate_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                certificate_number TEXT UNIQUE,
                quote_id INTEGER NOT NULL,
                template_id INTEGER NOT NULL,
                certificate_holder_name TEXT NOT NULL,
                certificate_holder_address TEXT NOT NULL,
                additional_insured_name TEXT,
                additional_insured_address TEXT,
                project_description TEXT,
                project_location TEXT,
                effective_date DATE NOT NULL,
                expiration_date DATE NOT NULL,
                certificate_status TEXT DEFAULT 'draft',
                special_provisions TEXT,
                waiver_of_subrogation BOOLEAN DEFAULT FALSE,
                primary_and_noncontributory BOOLEAN DEFAULT FALSE,
                issued_date TIMESTAMP WITH TIME ZONE,
                issued_by INTEGER,
                created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
                
                CONSTRAINT fk_certificate_quote 
                    FOREIGN KEY (quote_id) REFERENCES public.quotes(quote_id),
                CONSTRAINT fk_certificate_template 
                    FOREIGN KEY (template_id) REFERENCES public.certificate_templates(template_id)
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS public.certificate_coverages (
                coverage_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                certificate_id INTEGER NOT NULL,
                coverage_type TEXT NOT NULL,
                each_occurrence DECIMAL(15,2),
                general_aggregate DECIMAL(15,2),
                products_completed_ops DECIMAL(15,2),
                personal_advertising_injury DECIMAL(15,2),
                deductible DECIMAL(12,2),
                policy_number TEXT,
                policy_effective_date DATE NOT NULL,
                policy_expiration_date DATE NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
                
                CONSTRAINT fk_coverage_certificate 
                    FOREIGN KEY (certificate_id) REFERENCES public.certificates(certificate_id) ON DELETE CASCADE
            );
            """,
            """
            INSERT INTO public.certificate_templates (template_name, template_type, description) VALUES
            ('Standard Certificate', 'standard', 'Standard certificate of insurance'),
            ('Contractor Certificate', 'contractor', 'Certificate for contractor requirements'),
            ('Vendor Certificate', 'vendor', 'Certificate for vendor agreements'),
            ('Auto Certificate', 'auto', 'Automobile liability certificate')
            ON CONFLICT DO NOTHING;
            """
        ]
        
        with connection.cursor() as cursor:
            for sql in sql_commands:
                try:
                    cursor.execute(sql)
                    self.stdout.write(".", ending="")
                except Exception as e:
                    self.stdout.write(f"Error: {e}")
        
        self.stdout.write(self.style.SUCCESS("\nCertificate management schema created successfully!"))
