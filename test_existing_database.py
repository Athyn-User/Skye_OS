#!/usr/bin/env python
"""Test connection to existing PostgreSQL database"""

import os
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Skye_OS.settings')
django.setup()

from django.db import connection

def test_existing_database():
    """Test connection to existing database and check tables"""
    try:
        # Test database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            db_version = cursor.fetchone()
            print(f"✅ Database connected successfully!")
            print(f"PostgreSQL version: {db_version[0]}")
            
            # Check if our tables exist
            tables_to_check = ['venture', 'drive', 'employee_location', 'generation_job', 'parameter']
            
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name IN %s
            """, (tuple(tables_to_check),))
            
            existing_tables = [row[0] for row in cursor.fetchall()]
            
            print(f"\n📊 Table Status:")
            for table in tables_to_check:
                if table in existing_tables:
                    print(f"✅ {table} - EXISTS")
                    
                    # Get row count
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    print(f"   📝 Rows: {count}")
                else:
                    print(f"❌ {table} - MISSING")
            
            # List all tables in database
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """)
            all_tables = [row[0] for row in cursor.fetchall()]
            
            print(f"\n📋 All tables in database ({len(all_tables)}):")
            for table in all_tables[:10]:  # Show first 10
                print(f"   - {table}")
            if len(all_tables) > 10:
                print(f"   ... and {len(all_tables) - 10} more")
        
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

if __name__ == "__main__":
    test_existing_database()