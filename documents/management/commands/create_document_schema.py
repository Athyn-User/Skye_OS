from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = "Create document management tables"

    def handle(self, *args, **options):
        sql_commands = [
            """
            CREATE TABLE IF NOT EXISTS public.document_categories (
                document_category_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                category_name TEXT NOT NULL UNIQUE,
                description TEXT,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS public.documents (
                document_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                document_category_id INTEGER NOT NULL,
                application_id INTEGER,
                quote_id INTEGER,
                company_id INTEGER,
                document_name TEXT NOT NULL,
                original_filename TEXT NOT NULL,
                file_path TEXT NOT NULL,
                file_size_bytes BIGINT NOT NULL,
                mime_type TEXT NOT NULL,
                file_extension TEXT,
                version_number INTEGER DEFAULT 1,
                is_current_version BOOLEAN DEFAULT TRUE,
                parent_document_id INTEGER,
                document_status TEXT DEFAULT 'uploaded',
                upload_date TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
                is_confidential BOOLEAN DEFAULT FALSE,
                access_level TEXT DEFAULT 'internal',
                uploaded_by INTEGER,
                approved_by INTEGER,
                approved_date TIMESTAMP WITH TIME ZONE,
                description TEXT,
                tags JSONB DEFAULT '[]',
                metadata JSONB DEFAULT '{}',
                created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
                
                CONSTRAINT fk_document_category 
                    FOREIGN KEY (document_category_id) REFERENCES public.document_categories(document_category_id),
                CONSTRAINT fk_document_application 
                    FOREIGN KEY (application_id) REFERENCES public.applications(application_id) ON DELETE SET NULL,
                CONSTRAINT fk_document_quote 
                    FOREIGN KEY (quote_id) REFERENCES public.quotes(quote_id) ON DELETE SET NULL,
                CONSTRAINT fk_document_company 
                    FOREIGN KEY (company_id) REFERENCES public.companies(company_id) ON DELETE SET NULL
            );
            """,
            """
            INSERT INTO public.document_categories (category_name, description) VALUES
            ('Application Documents', 'Documents submitted with insurance applications'),
            ('Financial Statements', 'Company financial documents and reports'),
            ('Certificates', 'Insurance certificates and proof of coverage'),
            ('Policies', 'Insurance policy documents'),
            ('Claims', 'Claims-related documentation'),
            ('Underwriting', 'Underwriting reports and risk assessments'),
            ('Compliance', 'Regulatory and compliance documents'),
            ('Correspondence', 'Letters, emails, and other correspondence'),
            ('Proposals', 'Insurance proposals and quotes'),
            ('Other', 'Miscellaneous documents')
            ON CONFLICT (category_name) DO NOTHING;
            """
        ]
        
        with connection.cursor() as cursor:
            for sql in sql_commands:
                try:
                    cursor.execute(sql)
                    self.stdout.write(".", ending="")
                except Exception as e:
                    self.stdout.write(f"Error: {e}")
        
        self.stdout.write(self.style.SUCCESS("\nDocument management schema created successfully!"))
