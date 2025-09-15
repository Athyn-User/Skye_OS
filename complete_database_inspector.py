#!/usr/bin/env python
"""Complete Database Inspector for Django Migration"""

import os
import django
from collections import defaultdict

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Skye_OS.settings')
django.setup()

from django.db import connection

def get_postgres_to_django_type(pg_type, character_maximum_length=None):
    """Convert PostgreSQL data types to Django field types"""
    type_mapping = {
        'integer': 'IntegerField',
        'bigint': 'BigIntegerField',
        'smallint': 'SmallIntegerField',
        'serial': 'AutoField',
        'bigserial': 'BigAutoField',
        'boolean': 'BooleanField',
        'character varying': f'CharField(max_length={character_maximum_length or 255})',
        'varchar': f'CharField(max_length={character_maximum_length or 255})',
        'text': 'TextField',
        'date': 'DateField',
        'timestamp without time zone': 'DateTimeField',
        'timestamp with time zone': 'DateTimeField',
        'time without time zone': 'TimeField',
        'numeric': 'DecimalField(max_digits=10, decimal_places=2)',
        'decimal': 'DecimalField(max_digits=10, decimal_places=2)',
        'real': 'FloatField',
        'double precision': 'FloatField',
        'money': 'DecimalField(max_digits=10, decimal_places=2)',
        'uuid': 'UUIDField',
        'json': 'JSONField',
        'jsonb': 'JSONField',
    }
    
    base_type = pg_type.lower()
    return type_mapping.get(base_type, f'CharField(max_length=255)  # Unknown type: {pg_type}')

def inspect_database():
    """Complete database inspection for Django migration"""
    
    print("🔍 COMPLETE DATABASE INSPECTION FOR DJANGO MIGRATION")
    print("=" * 60)
    
    with connection.cursor() as cursor:
        
        # 1. Get all tables with row counts
        print("\n📊 ALL TABLES OVERVIEW:")
        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """)
        
        table_results = cursor.fetchall()
        table_names = [table[0] for table in table_results]
        
        print(f"Found {len(table_names)} tables:")
        
        # Get row counts for each table
        all_tables = []
        for table_name in table_names:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                row_count = cursor.fetchone()[0]
                all_tables.append(('public', table_name, row_count))
                print(f"  📋 {table_name:<25} ({row_count:>4} rows)")
            except Exception as e:
                all_tables.append(('public', table_name, 0))
                print(f"  📋 {table_name:<25} (error counting rows)")
        
        # 2. Get detailed table structures
        print(f"\n🏗️  DETAILED TABLE STRUCTURES:")
        print("-" * 60)
        
        table_structures = {}
        
        for table_name in table_names:
            print(f"\n📋 Table: {table_name}")
            
            # Get columns
            cursor.execute("""
                SELECT 
                    column_name,
                    data_type,
                    character_maximum_length,
                    is_nullable,
                    column_default
                FROM information_schema.columns 
                WHERE table_name = %s 
                ORDER BY ordinal_position
            """, [table_name])
            
            columns = cursor.fetchall()
            
            # Get primary keys
            cursor.execute("""
                SELECT a.attname
                FROM pg_index i
                JOIN pg_attribute a ON a.attrelid = i.indrelid 
                    AND a.attnum = ANY(i.indkey)
                JOIN pg_class c ON c.oid = i.indrelid
                WHERE c.relname = %s
                    AND i.indisprimary
            """, [table_name])
            
            primary_keys = [row[0] for row in cursor.fetchall()]
            
            # Get foreign keys
            cursor.execute("""
                SELECT
                    kcu.column_name,
                    ccu.table_name AS foreign_table_name,
                    ccu.column_name AS foreign_column_name
                FROM 
                    information_schema.table_constraints AS tc 
                    JOIN information_schema.key_column_usage AS kcu
                        ON tc.constraint_name = kcu.constraint_name
                        AND tc.table_schema = kcu.table_schema
                    JOIN information_schema.constraint_column_usage AS ccu
                        ON ccu.constraint_name = tc.constraint_name
                        AND ccu.table_schema = tc.table_schema
                WHERE tc.constraint_type = 'FOREIGN KEY' 
                    AND tc.table_name = %s
            """, [table_name])
            
            foreign_keys = cursor.fetchall()
            
            # Store structure
            table_structures[table_name] = {
                'columns': columns,
                'primary_keys': primary_keys,
                'foreign_keys': foreign_keys
            }
            
            # Display structure
            print(f"  📋 Columns ({len(columns)}):")
            for col_name, data_type, max_length, nullable, default in columns:
                pk_indicator = " 🔑" if col_name in primary_keys else ""
                fk_indicator = ""
                for fk_col, fk_table, fk_ref_col in foreign_keys:
                    if fk_col == col_name:
                        fk_indicator = f" 🔗 → {fk_table}.{fk_ref_col}"
                        break
                
                django_type = get_postgres_to_django_type(data_type, max_length)
                nullable_str = "NULL" if nullable == "YES" else "NOT NULL"
                
                print(f"    • {col_name:<20} {data_type:<15} {nullable_str:<8} {django_type:<30}{pk_indicator}{fk_indicator}")
        
        # 3. Analyze relationships
        print(f"\n🔗 FOREIGN KEY RELATIONSHIPS:")
        print("-" * 60)
        
        relationships = defaultdict(list)
        
        for table_name, structure in table_structures.items():
            for fk_col, fk_table, fk_ref_col in structure['foreign_keys']:
                relationships[table_name].append({
                    'column': fk_col,
                    'references': fk_table,
                    'ref_column': fk_ref_col
                })
        
        for table, fks in relationships.items():
            if fks:
                print(f"\n📋 {table}:")
                for fk in fks:
                    print(f"    🔗 {fk['column']} → {fk['references']}.{fk['ref_column']}")
        
        # 4. Generate Django models
        print(f"\n🐍 DJANGO MODELS GENERATION:")
        print("-" * 60)
        
        models_code = generate_django_models(table_structures)
        
        # Save to file
        with open('generated_models.py', 'w') as f:
            f.write(models_code)
        
        print("✅ Django models generated and saved to 'generated_models.py'")
        
        # 5. Summary and recommendations
        print(f"\n📈 MIGRATION SUMMARY:")
        print("-" * 60)
        print(f"• Total tables to migrate: {len(all_tables)}")
        print(f"• Tables with foreign keys: {len([t for t in relationships.keys() if relationships[t]])}")
        print(f"• Current Django tables: 5 (venture, drive, employee_location, generation_job, parameter)")
        print(f"• Remaining tables: {len(all_tables) - 5}")
        
        # Find most connected tables
        fk_counts = defaultdict(int)
        for table, fks in relationships.items():
            fk_counts[table] = len(fks)
        
        most_connected = sorted(fk_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        print(f"\n🔗 MOST CONNECTED TABLES (good candidates for next migration):")
        for table, fk_count in most_connected:
            if fk_count > 0:
                print(f"  📋 {table:<25} ({fk_count} foreign keys)")
        
        return table_structures

def generate_django_models(table_structures):
    """Generate Django models code from table structures"""
    
    models_code = """# Generated Django Models
# This file was auto-generated from your PostgreSQL database structure

from django.db import models

"""
    
    # Sort tables to handle dependencies (tables with fewer FKs first)
    def fk_count(item):
        return len(item[1]['foreign_keys'])
    
    sorted_tables = sorted(table_structures.items(), key=fk_count)
    
    for table_name, structure in sorted_tables:
        
        # Skip tables we already have models for
        if table_name in ['venture', 'drive', 'employee_location', 'generation_job', 'parameter']:
            continue
        
        class_name = ''.join(word.capitalize() for word in table_name.split('_'))
        
        models_code += f"\nclass {class_name}(models.Model):\n"
        
        for col_name, data_type, max_length, nullable, default in structure['columns']:
            
            # Check if this is a foreign key
            is_fk = False
            fk_reference = None
            for fk_col, fk_table, fk_ref_col in structure['foreign_keys']:
                if fk_col == col_name:
                    is_fk = True
                    fk_class = ''.join(word.capitalize() for word in fk_table.split('_'))
                    fk_reference = fk_class
                    break
            
            # Check if this is a primary key
            is_pk = col_name in structure['primary_keys']
            
            # Generate field
            if is_fk:
                field_def = f"models.ForeignKey({fk_reference}, models.DO_NOTHING"
                field_def += f", db_column='{col_name}'"
                if nullable == "YES":
                    field_def += ", blank=True, null=True"
                field_def += ")"
            elif is_pk and col_name.endswith('_id'):
                field_def = "models.AutoField(primary_key=True)"
            else:
                django_type = get_postgres_to_django_type(data_type, max_length)
                field_def = f"models.{django_type}"
                
                if nullable == "YES":
                    field_def += ", blank=True, null=True"
            
            models_code += f"    {col_name} = {field_def}\n"
        
        models_code += f"\n    class Meta:\n"
        models_code += f"        managed = True\n"
        models_code += f"        db_table = '{table_name}'\n"
        
        # Add __str__ method
        # Try to find a name field
        name_fields = ['name', 'title', 'description']
        name_field = None
        for col_name, _, _, _, _ in structure['columns']:
            if any(nf in col_name.lower() for nf in name_fields):
                name_field = col_name
                break
        
        if name_field:
            models_code += f"\n    def __str__(self):\n"
            models_code += f"        return self.{name_field} or f\"{class_name} {{self.pk}}\"\n"
        else:
            models_code += f"\n    def __str__(self):\n"
            models_code += f"        return f\"{class_name} {{self.pk}}\"\n"
    
    return models_code

if __name__ == "__main__":
    try:
        table_structures = inspect_database()
        print(f"\n✅ Database inspection complete!")
        print(f"📁 Check 'generated_models.py' for Django models")
        
    except Exception as e:
        print(f"❌ Error during inspection: {e}")
        import traceback
        traceback.print_exc()