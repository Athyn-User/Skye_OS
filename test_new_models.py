#!/usr/bin/env python
"""Test the new Django models we added"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Skye_OS.settings')
django.setup()

from core.models import (
    Products, Company, Coverage, Orders, Workflow, Task, 
    Paper, Attachment, Document, EmployeeContact, BrokerContact,
    Stage, FlowOrigin, AttachmentType, Broker, Cloud, Options,
    GenerationModel, TrainingModel, InputOutput
)

def test_new_models():
    """Test that the new models can connect to database"""
    
    new_models_to_test = [
        ('Products', Products),
        ('Company', Company),
        ('Coverage', Coverage),
        ('Orders', Orders),
        ('Workflow', Workflow),
        ('Task', Task),
        ('Paper', Paper),
        ('Attachment', Attachment),
        ('Document', Document),
        ('EmployeeContact', EmployeeContact),
        ('BrokerContact', BrokerContact),
        ('Stage', Stage),
        ('FlowOrigin', FlowOrigin),
        ('AttachmentType', AttachmentType),
        ('Broker', Broker),
        ('Cloud', Cloud),
        ('Options', Options),
        ('GenerationModel', GenerationModel),
        ('TrainingModel', TrainingModel),
        ('InputOutput', InputOutput),
    ]
    
    print("🧪 Testing NEW Django Models:\n")
    
    working_models = 0
    total_records = 0
    models_with_data = []
    
    for name, model in new_models_to_test:
        try:
            count = model.objects.count()
            print(f"✅ {name}: {count} records")
            working_models += 1
            total_records += count
            
            # Track models with data
            if count > 0:
                models_with_data.append((name, count))
                # Try to get first record if any exist
                first_record = model.objects.first()
                print(f"   📝 Sample: {first_record}")
            else:
                print(f"   📝 No data found")
                
        except Exception as e:
            print(f"❌ {name}: Error - {e}")
        
        print()
    
    print(f"📊 SUMMARY:")
    print(f"✅ Working models: {working_models}/{len(new_models_to_test)}")
    print(f"📋 Total records across all models: {total_records}")
    print(f"🗃️  Models with data: {len(models_with_data)}")
    
    if models_with_data:
        print(f"\n📈 Models with most data:")
        sorted_models = sorted(models_with_data, key=lambda x: x[1], reverse=True)
        for name, count in sorted_models[:5]:  # Show top 5
            print(f"  • {name}: {count} records")
    
    if working_models == len(new_models_to_test):
        print("\n🎉 All new models are working perfectly!")
        return True
    else:
        print(f"\n⚠️  {len(new_models_to_test) - working_models} models need attention")
        return False

if __name__ == "__main__":
    success = test_new_models()
    
    if success:
        print("\n🚀 Ready to create web pages for these models!")
        print("Which tables would you like to create web pages for first?")
    else:
        print("\n🔧 Some models need fixes before proceeding.")