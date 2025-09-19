# PowerShell script to create Django Skye OS file structure
# Run this from C:\Users\AMTOC\Skye_OS_Folder

# Navigate to project directory
Set-Location "C:\Users\AMTOC\Skye_OS_Folder"

# Create main project structure
New-Item -ItemType Directory -Force -Path "Skye_OS"
New-Item -ItemType Directory -Force -Path "Skye"
New-Item -ItemType Directory -Force -Path "templates"
New-Item -ItemType Directory -Force -Path "static"
New-Item -ItemType Directory -Force -Path "media"

# Create Django project files
New-Item -ItemType File -Force -Path "Skye_OS\__init__.py"
New-Item -ItemType File -Force -Path "Skye_OS\settings.py"
New-Item -ItemType File -Force -Path "Skye_OS\urls.py"
New-Item -ItemType File -Force -Path "Skye_OS\wsgi.py"
New-Item -ItemType File -Force -Path "Skye_OS\asgi.py"

# Create Django app files
New-Item -ItemType File -Force -Path "Skye\__init__.py"
New-Item -ItemType File -Force -Path "Skye\admin.py"
New-Item -ItemType File -Force -Path "Skye\apps.py"
New-Item -ItemType File -Force -Path "Skye\models.py"
New-Item -ItemType File -Force -Path "Skye\views.py"
New-Item -ItemType File -Force -Path "Skye\forms.py"
New-Item -ItemType File -Force -Path "Skye\urls.py"
New-Item -ItemType File -Force -Path "Skye\tests.py"

# Create migrations directory
New-Item -ItemType Directory -Force -Path "Skye\migrations"
New-Item -ItemType File -Force -Path "Skye\migrations\__init__.py"

# Create template directories and files
New-Item -ItemType Directory -Force -Path "templates\auth"
New-Item -ItemType Directory -Force -Path "templates\companies"
New-Item -ItemType Directory -Force -Path "templates\products"
New-Item -ItemType Directory -Force -Path "templates\orders"
New-Item -ItemType Directory -Force -Path "templates\applications"
New-Item -ItemType Directory -Force -Path "templates\employees"
New-Item -ItemType Directory -Force -Path "templates\ventures"
New-Item -ItemType Directory -Force -Path "templates\reports"

# Create template files
New-Item -ItemType File -Force -Path "templates\base.html"
New-Item -ItemType File -Force -Path "templates\dashboard.html"
New-Item -ItemType File -Force -Path "templates\auth\login.html"
New-Item -ItemType File -Force -Path "templates\companies\list.html"
New-Item -ItemType File -Force -Path "templates\companies\detail.html"
New-Item -ItemType File -Force -Path "templates\companies\form.html"
New-Item -ItemType File -Force -Path "templates\companies\confirm_delete.html"
New-Item -ItemType File -Force -Path "templates\products\list.html"
New-Item -ItemType File -Force -Path "templates\products\detail.html"
New-Item -ItemType File -Force -Path "templates\products\form.html"
New-Item -ItemType File -Force -Path "templates\products\confirm_delete.html"
New-Item -ItemType File -Force -Path "templates\orders\list.html"
New-Item -ItemType File -Force -Path "templates\orders\detail.html"
New-Item -ItemType File -Force -Path "templates\orders\form.html"
New-Item -ItemType File -Force -Path "templates\orders\confirm_delete.html"
New-Item -ItemType File -Force -Path "templates\applications\list.html"
New-Item -ItemType File -Force -Path "templates\applications\detail.html"
New-Item -ItemType File -Force -Path "templates\applications\form.html"
New-Item -ItemType File -Force -Path "templates\applications\confirm_delete.html"
New-Item -ItemType File -Force -Path "templates\employees\list.html"
New-Item -ItemType File -Force -Path "templates\employees\detail.html"
New-Item -ItemType File -Force -Path "templates\employees\form.html"
New-Item -ItemType File -Force -Path "templates\employees\confirm_delete.html"
New-Item -ItemType File -Force -Path "templates\ventures\list.html"
New-Item -ItemType File -Force -Path "templates\ventures\detail.html"
New-Item -ItemType File -Force -Path "templates\ventures\form.html"
New-Item -ItemType File -Force -Path "templates\ventures\confirm_delete.html"
New-Item -ItemType File -Force -Path "templates\reports\dashboard.html"

# Create static file directories
New-Item -ItemType Directory -Force -Path "static\css"
New-Item -ItemType Directory -Force -Path "static\js"
New-Item -ItemType Directory -Force -Path "static\images"

# Create static files
New-Item -ItemType File -Force -Path "static\css\custom.css"
New-Item -ItemType File -Force -Path "static\js\custom.js"

# Create main Django files
New-Item -ItemType File -Force -Path "manage.py"
New-Item -ItemType File -Force -Path "requirements.txt"
New-Item -ItemType File -Force -Path "test_db.py"
New-Item -ItemType File -Force -Path ".env.example"
New-Item -ItemType File -Force -Path ".gitignore"
New-Item -ItemType File -Force -Path "README.md"

# Create requirements.txt content
@"
Django==4.2.7
psycopg2==2.9.7
pillow==10.0.1
django-crispy-forms==2.1
crispy-bootstrap5==0.7
django-extensions==3.2.3
python-decouple==3.8
"@ | Out-File -FilePath "requirements.txt" -Encoding utf8

# Create .gitignore content
@"
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
pip-wheel-metadata/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Django
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal
media/
staticfiles/

# Virtual Environment
skye_env/
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Environment variables
.env
"@ | Out-File -FilePath ".gitignore" -Encoding utf8

# Create .env.example
@"
SECRET_KEY=your-secret-key-here
DEBUG=True
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=your-password-here
DB_HOST=localhost
DB_PORT=5432
ALLOWED_HOSTS=localhost,127.0.0.1
"@ | Out-File -FilePath ".env.example" -Encoding utf8

# Create manage.py content
@"
#!/usr/bin/env python
import os
import sys

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Skye_OS.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)
"@ | Out-File -FilePath "manage.py" -Encoding utf8

# Create test_db.py content
@"
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
"@ | Out-File -FilePath "test_db.py" -Encoding utf8

# Create Skye/apps.py content
@"
from django.apps import AppConfig


class SkyeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Skye'
"@ | Out-File -FilePath "Skye\apps.py" -Encoding utf8

# Create basic wsgi.py content
@"
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Skye_OS.settings')
application = get_wsgi_application()
"@ | Out-File -FilePath "Skye_OS\wsgi.py" -Encoding utf8

# Create basic asgi.py content
@"
import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Skye_OS.settings')
application = get_asgi_application()
"@ | Out-File -FilePath "Skye_OS\asgi.py" -Encoding utf8

# Create custom.css with basic styles
@"
/* Custom styles for Skye OS */
.navbar-brand {
    font-weight: bold;
}

.card-header h5 {
    margin-bottom: 0;
}

.table-hover tbody tr:hover {
    background-color: rgba(0, 123, 255, 0.075);
}

.btn-group .btn {
    margin-right: 0;
}

.pagination .page-link {
    color: #0d6efd;
}

.pagination .page-item.active .page-link {
    background-color: #0d6efd;
    border-color: #0d6efd;
}

/* Dashboard cards */
.card.text-white .card-footer a {
    text-decoration: none;
}

.card.text-white .card-footer a:hover {
    text-decoration: underline;
}

/* Form styling */
.form-control:focus {
    border-color: #0d6efd;
    box-shadow: 0 0 0 0.2rem rgba(13, 110, 253, 0.25);
}

/* Search form */
.search-form {
    background-color: #f8f9fa;
    padding: 1rem;
    border-radius: 0.375rem;
    margin-bottom: 1rem;
}
"@ | Out-File -FilePath "static\css\custom.css" -Encoding utf8

# Create custom.js with basic functionality
@"
// Custom JavaScript for Skye OS

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert-dismissible');
        alerts.forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);

    // Confirm delete actions
    var deleteLinks = document.querySelectorAll('a[href*="delete"]');
    deleteLinks.forEach(function(link) {
        link.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to delete this item?')) {
                e.preventDefault();
            }
        });
    });

    // Search form auto-submit
    var searchInputs = document.querySelectorAll('input[name="search"]');
    searchInputs.forEach(function(input) {
        var timeout;
        input.addEventListener('input', function() {
            clearTimeout(timeout);
            timeout = setTimeout(function() {
                input.closest('form').submit();
            }, 500);
        });
    });
});

// Utility functions
function showLoading() {
    document.body.style.cursor = 'wait';
}

function hideLoading() {
    document.body.style.cursor = 'default';
}

// AJAX helpers
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Set up CSRF token for AJAX requests
const csrftoken = getCookie('csrftoken');
if (csrftoken) {
    document.querySelector('meta[name=csrf-token]').setAttribute('content', csrftoken);
}
"@ | Out-File -FilePath "static\js\custom.js" -Encoding utf8

# Create README.md
@"
# Skye OS - Django Application

A comprehensive Django application for managing insurance/business operations with PostgreSQL database integration.

## Features

- Full CRUD operations for Companies, Products, Orders, Applications
- Employee and Broker management
- Workflow and parameter systems  
- Dashboard with key metrics
- Search and pagination
- Responsive Bootstrap design
- Admin interface

## Setup

1. Create and activate virtual environment:
   ```
   python -m venv skye_env
   skye_env\Scripts\activate
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Configure database in settings.py

4. Run migrations:
   ```
   python manage.py makemigrations
   python manage.py migrate --fake-initial
   ```

5. Create superuser:
   ```
   python manage.py createsuperuser
   ```

6. Run development server:
   ```
   python manage.py runserver
   ```

## Usage

- Access the application at http://127.0.0.1:8000
- Admin interface at http://127.0.0.1:8000/admin
- Use the navigation menu to access different modules

## Structure

- **Skye_OS/**: Main Django project
- **Skye/**: Django application
- **templates/**: HTML templates
- **static/**: CSS, JS, images
- **media/**: User uploaded files
"@ | Out-File -FilePath "README.md" -Encoding utf8

Write-Host "Django file structure created successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Create virtual environment: python -m venv skye_env" -ForegroundColor White
Write-Host "2. Activate it: skye_env\Scripts\activate" -ForegroundColor White
Write-Host "3. Install requirements: pip install -r requirements.txt" -ForegroundColor White
Write-Host "4. Copy your Django code into the created files" -ForegroundColor White
Write-Host "5. Configure database settings" -ForegroundColor White
Write-Host "6. Run migrations and start server" -ForegroundColor White