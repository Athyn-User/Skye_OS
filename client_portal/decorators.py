# client_portal/decorators.py

from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def client_login_required(view_func):
    """Decorator to check if user is logged in and has client profile"""
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.info(request, 'Please log in to access the client portal.')
            return redirect('client_portal:login')
        
        if not hasattr(request.user, 'client_profile'):
            messages.error(request, 'You do not have client portal access.')
            return redirect('client_portal:login')
        
        if not request.user.client_profile.portal_access_enabled:
            messages.error(request, 'Your portal access has been disabled.')
            return redirect('client_portal:login')
        
        return view_func(request, *args, **kwargs)
    
    return wrapped_view