import os
from celery import Celery
from decouple import config

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skye_os.settings')

app = Celery('skye_os')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Redis configuration
app.conf.broker_url = config('CELERY_BROKER_URL', default='redis://localhost:6379/0')
app.conf.result_backend = config('CELERY_RESULT_BACKEND', default='redis://localhost:6379/0')

# Task discovery
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
