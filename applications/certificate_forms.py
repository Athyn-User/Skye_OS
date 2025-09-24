from django import forms
from .models import Certificate, CertificateTemplate

class CertificateForm(forms.ModelForm):
    class Meta:
        model = Certificate
        fields = [
            'template', 'certificate_holder_name', 'certificate_holder_address',
            'project_description', 'effective_date', 'expiration_date', 
            'certificate_status'
        ]
        
        widgets = {
            'template': forms.Select(attrs={'class': 'form-control'}),
            'certificate_holder_name': forms.TextInput(attrs={'class': 'form-control'}),
            'certificate_holder_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'project_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'effective_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'expiration_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'certificate_status': forms.Select(attrs={'class': 'form-control'}),
        }

class CertificateTemplateForm(forms.ModelForm):
    class Meta:
        model = CertificateTemplate
        fields = ['template_name', 'template_type', 'description']
        
        widgets = {
            'template_name': forms.TextInput(attrs={'class': 'form-control'}),
            'template_type': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
