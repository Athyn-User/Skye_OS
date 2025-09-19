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
   `
   python -m venv skye_env
   skye_env\Scripts\activate
   `

2. Install dependencies:
   `
   pip install -r requirements.txt
   `

3. Configure database in settings.py

4. Run migrations:
   `
   python manage.py makemigrations
   python manage.py migrate --fake-initial
   `

5. Create superuser:
   `
   python manage.py createsuperuser
   `

6. Run development server:
   `
   python manage.py runserver
   `

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
