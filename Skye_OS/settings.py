# Skye_OS/settings.py

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'your-secret-key-here-change-in-production'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'Skye',  # Your main app
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'Skye_OS.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'Skye_OS.wsgi.application'

# Database configuration for PostgreSQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',
        'USER': 'postgres',
        'PASSWORD': 'MyPSW555',  # Replace with your actual password
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Pagination
PAGINATION_PER_PAGE = 25
# Login/Logout URLs
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# Skye OS Configuration
SKYE_PAGES_CONFIG = {
    'IT': {
        'title': 'IT Operations',
        'description': 'Infrastructure and technology management',
        'icon': 'computer', 
        'color': '#4285f4'
    },
    'DocGen': {
        'title': 'Document Generation',
        'description': 'Automated document creation and processing',
        'icon': 'description', 
        'color': '#34a853'
    },
    'Portfolio': {
        'title': 'Portfolio Management',
        'description': 'Investment and portfolio tracking',
        'icon': 'folder', 
        'color': '#fbbc04'
    },
    'Workstation': {
        'title': 'Workstation',
        'description': 'Personal productivity and task management',
        'icon': 'work', 
        'color': '#ea4335'
    },
    'Catalog': {
        'title': 'Data Catalog',
        'description': 'Comprehensive data management and organization',
        'icon': 'storage', 
        'color': '#9aa0a6'
    },
    'Machine Learning': {
        'title': 'Machine Learning',
        'description': 'AI model training, generation, and parameter management',
        'icon': 'psychology', 
        'color': '#9c27b0'
    }
}

PROGRESSIVE_LOADING = {
    'INITIAL_SECTIONS': 3,  # Load first 3 sections immediately
    'SECTION_BATCH_SIZE': 2,  # Load 2 sections per subsequent request
    'RECORDS_PER_SECTION': 20  # Max records per section preview
}
# Foreign key resolution cache settings
FK_RESOLUTION_CACHE_TIMEOUT = 300  # 5 minutes