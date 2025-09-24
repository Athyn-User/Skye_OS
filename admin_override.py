# admin_override.py
from django.contrib import admin
from django.apps import apps

# Force registration of all models
for app in ['claims', 'client_portal']:
    app_models = apps.get_app_config(app).get_models()
    for model in app_models:
        try:
            admin.site.register(model)
        except admin.sites.AlreadyRegistered:
            pass