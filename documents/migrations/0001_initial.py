from django.db import migrations

class Migration(migrations.Migration):
    initial = True
    dependencies = []
    
    operations = [
        migrations.RunSQL(
            # This declares that the table already exists
            sql="SELECT 1;",  # Dummy SQL since table exists
            reverse_sql="SELECT 1;",
            state_operations=[],
        ),
    ]
