from django.db import migrations

class Migration(migrations.Migration):
    
    dependencies = [
        ('documents', '0001_initial'),
    ]
    
    operations = [
        migrations.RunSQL(
            """
            ALTER TABLE portal_documents 
            ADD COLUMN IF NOT EXISTS client_visible BOOLEAN DEFAULT TRUE;
            ALTER TABLE portal_documents 
            ADD COLUMN IF NOT EXISTS client_removed_date TIMESTAMP NULL;
            ALTER TABLE portal_documents 
            ADD COLUMN IF NOT EXISTS client_removed_reason TEXT;
            ALTER TABLE portal_documents 
            ADD COLUMN IF NOT EXISTS archive_path VARCHAR(500);
            ALTER TABLE portal_documents 
            ADD COLUMN IF NOT EXISTS archive_created_date TIMESTAMP NULL;
            ALTER TABLE portal_documents 
            ADD COLUMN IF NOT EXISTS original_file_path VARCHAR(500);
            ALTER TABLE portal_documents 
            ADD COLUMN IF NOT EXISTS retention_period_days INTEGER DEFAULT 2555;
            ALTER TABLE portal_documents 
            ADD COLUMN IF NOT EXISTS compliance_hold BOOLEAN DEFAULT FALSE;
            ALTER TABLE portal_documents 
            ADD COLUMN IF NOT EXISTS permanent_record BOOLEAN DEFAULT TRUE;
            """,
            reverse_sql="""
            ALTER TABLE portal_documents 
            DROP COLUMN IF EXISTS client_visible;
            ALTER TABLE portal_documents 
            DROP COLUMN IF EXISTS client_removed_date;
            ALTER TABLE portal_documents 
            DROP COLUMN IF EXISTS client_removed_reason;
            ALTER TABLE portal_documents 
            DROP COLUMN IF EXISTS archive_path;
            ALTER TABLE portal_documents 
            DROP COLUMN IF EXISTS archive_created_date;
            ALTER TABLE portal_documents 
            DROP COLUMN IF EXISTS original_file_path;
            ALTER TABLE portal_documents 
            DROP COLUMN IF EXISTS retention_period_days;
            ALTER TABLE portal_documents 
            DROP COLUMN IF EXISTS compliance_hold;
            ALTER TABLE portal_documents 
            DROP COLUMN IF EXISTS permanent_record;
            """
        ),
    ]
