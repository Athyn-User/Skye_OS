import os
import django
import sys

# Add project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Skye_OS.settings')
django.setup()

from Skye.models import Company, Products, Orders

# Test database connectivity
try:
    companies_count = Company.objects.count()
    products_count = Products.objects.count()
    orders_count = Orders.objects.count()
    
    print(f"Database connection successful!")
    print(f"Companies: {companies_count}")
    print(f"Products: {products_count}")
    print(f"Orders: {orders_count}")
    
    # Test a simple query
    if companies_count > 0:
        first_company = Company.objects.first()
        print(f"First company: {first_company.company_name}")
        
except Exception as e:
    print(f"Database connection failed: {e}")
    import traceback
    traceback.print_exc()
