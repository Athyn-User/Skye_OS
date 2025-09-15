#!/usr/bin/env python
"""Test Django models with existing database"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Skye_OS.settings')
django.setup()

from core.models import Venture, Drive, EmployeeLocation, GenerationJob, Parameter

def test_models():
    """Test that all models can connect to database"""
    
    models_to_test = [
        ('Venture', Venture),
        ('Drive', Drive), 
        ('EmployeeLocation', EmployeeLocation),
        ('GenerationJob', GenerationJob),
        ('Parameter', Parameter)
    ]
    
    print("🧪 Testing Django Models with Database Connection:\n")
    
    for name, model in models_to_test:
        try:
            count = model.objects.count()
            print(f"✅ {name}: {count} records")
            
            # Try to get first record if any exist
            if count > 0:
                first_record = model.objects.first()
                print(f"   📝 Sample: {first_record}")
            else:
                print(f"   📝 No data found")
                
        except Exception as e:
            print(f"❌ {name}: Error - {e}")
        
        print()

if __name__ == "__main__":
    test_models()