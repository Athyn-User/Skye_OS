#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Skye_OS.settings')
django.setup()

from django.db import connection

def check_migration_state():
    with connection.cursor() as cursor:
        # Check if django_migrations table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'django_migrations'
            );
        """)
        migrations_table_exists = cursor.fetchone()[0]
        print(f"Django migrations table exists: {migrations_table_exists}")
        
        if migrations_table_exists:
            # Check what migrations Django thinks are applied
            cursor.execute("""
                SELECT app, name, applied 
                FROM django_migrations 
                WHERE app = 'core'
                ORDER BY applied;
            """)
            migrations = cursor.fetchall()
            print(f"\nApplied core migrations: {len(migrations)}")
            for app, name, applied in migrations:
                print(f"  {app}.{name} - {applied}")
        
        # Check if our business tables exist
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('application_question', 'products', 'orders', 'companies')
            ORDER BY table_name;
        """)
        tables = [row[0] for row in cursor.fetchall()]
        print(f"\nBusiness tables found: {tables}")

if __name__ == "__main__":
    check_migration_state()