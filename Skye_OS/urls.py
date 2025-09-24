from django.contrib import admin
from django.urls import path, include
from django.contrib import admin

try:
    import admin_override
except:
    pass

urlpatterns = [
    path('accounts/', include('django.contrib.auth.urls')),
    path('admin/', admin.site.urls),
    path('', include('applications.urls')),
    path('documents/', include('documents.urls')),
    path('claims/', include('claims.urls')), 
    path('portal/', include('client_portal.urls')),
    path('analytics/', include('analytics.urls')),
    ]


