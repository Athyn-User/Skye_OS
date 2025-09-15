#!/usr/bin/env python
"""Fix the Django migration mess"""

import os
import django
import glob

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Skye_OS.settings')
django.setup()

from django.db import connection

def fix_migration_mess():
    """Clean up and fix Django migrations"""
    
    print("🔧 FIXING MIGRATION MESS")
    print("=" * 40)
    
    # Check current migration files
    migration_files = glob.glob('core/migrations/*.py')
    migration_files = [f for f in migration_files if not f.endswith('__init__.py')]
    
    print(f"📁 Current migration files:")
    for file in migration_files:
        print(f"  - {file}")
    
    # Check what Django thinks is applied
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT app, name, applied 
            FROM django_migrations 
            WHERE app = 'core'
            ORDER BY applied;
        """)
        applied_migrations = cursor.fetchall()
        
        print(f"\n📋 Django thinks these migrations are applied:")
        for app, name, applied in applied_migrations:
            print(f"  - {name} (applied: {applied})")
    
    print(f"\n🎯 RECOMMENDED FIXES:")
    print(f"1. Delete problematic migration files:")
    for file in migration_files:
        if '0002_' in file:
            print(f"   rm {file}")
    
    print(f"\n2. Clear Django's migration tracking for core app:")
    print(f"   DELETE FROM django_migrations WHERE app = 'core';")
    
    print(f"\n3. Create fresh initial migration:")
    print(f"   python manage.py makemigrations core --name fresh_initial")
    
    print(f"\n4. Fake apply it since tables exist:")
    print(f"   python manage.py migrate core --fake")
    
    print(f"\nShould I help you execute these fixes? (y/n)")
    
def execute_fixes():
    """Execute the migration fixes"""
    
    # Delete problematic migration files
    migration_files = glob.glob('core/migrations/0002_*.py')
    for file in migration_files:
        print(f"🗑️  Deleting {file}")
        os.remove(file)
    
    # Clear Django migration tracking
    with connection.cursor() as cursor:
        print("🧹 Clearing Django migration tracking for core app...")
        cursor.execute("DELETE FROM django_migrations WHERE app = 'core';")
    
    print("✅ Migration mess cleaned up!")
    print("\nNow run:")
    print("1. python manage.py makemigrations core --name fresh_initial")
    print("2. python manage.py migrate core --fake")

if __name__ == "__main__":
    fix_migration_mess()
    
    response = input().strip().lower()
    if response == 'y':
        execute_fixes()