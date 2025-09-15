#!/usr/bin/env python
"""Fix migration state for existing database"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Skye_OS.settings')
django.setup()

from django.db import connection
from django.core.management import execute_from_command_line

def fix_migrations():
    """Fix Django migration state to match existing database"""
    
    print("🔧 Fixing Django migration state...")
    
    with connection.cursor() as cursor:
        # Get list of all existing tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            AND table_name NOT LIKE 'django_%'
            AND table_name NOT LIKE 'auth_%'
            ORDER BY table_name;
        """)
        existing_tables = [row[0] for row in cursor.fetchall()]
        
        print(f"📊 Found {len(existing_tables)} business tables in database")
        
        # Check current migration state
        cursor.execute("""
            SELECT name FROM django_migrations 
            WHERE app = 'core'
            ORDER BY applied;
        """)
        applied_migrations = [row[0] for row in cursor.fetchall()]
        print(f"📋 Current applied migrations: {applied_migrations}")
        
    print("\n🎯 Recommended approach:")
    print("1. Create new migration for additional tables:")
    print("   python manage.py makemigrations core --name add_remaining_tables")
    print("\n2. Since tables already exist, fake the migration:")
    print("   python manage.py migrate core --fake")
    print("\n3. Test that models work:")
    print("   python test_models.py")
    
    return existing_tables, applied_migrations

if __name__ == "__main__":
    fix_migrations()