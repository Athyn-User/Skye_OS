# core/forms.py
from django import forms
from .models import CompanyContact, Company

class CompanyContactForm(forms.ModelForm):
    """Form for editing CompanyContact records"""
    
    class Meta:
        model = CompanyContact
        fields = [
            'company',
            'company_contact_first',
            'company_contact_last', 
            'company_contact_email',
            'company_contact_phone',
            'company_contact_title',
            'company_contact_salutation',
            'company_web'
        ]
        
        widgets = {
            'company': forms.Select(attrs={
                'class': 'form-control',
                'required': False
            }),
            'company_contact_first': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'First Name',
                'maxlength': 100
            }),
            'company_contact_last': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Last Name',
                'maxlength': 100
            }),
            'company_contact_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'email@company.com'
            }),
            'company_contact_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '(555) 123-4567'
            }),
            'company_contact_title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Job Title'
            }),
            'company_contact_salutation': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Mr., Ms., Dr., etc.'
            }),
            'company_web': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://company.com'
            })
        }
        
        labels = {
            'company': 'Company',
            'company_contact_first': 'First Name',
            'company_contact_last': 'Last Name',
            'company_contact_email': 'Email Address',
            'company_contact_phone': 'Phone Number',
            'company_contact_title': 'Job Title',
            'company_contact_salutation': 'Salutation',
            'company_web': 'Company Website'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Populate company dropdown with all companies
        self.fields['company'].queryset = Company.objects.all().order_by('company_name')
        self.fields['company'].empty_label = "Select a Company"
        
        # Make some fields optional
        self.fields['company_contact_phone'].required = False
        self.fields['company_contact_title'].required = False
        self.fields['company_contact_salutation'].required = False
        self.fields['company_web'].required = False

    def clean_company_contact_email(self):
        """Validate email format"""
        email = self.cleaned_data.get('company_contact_email')
        if email:
            email = email.lower().strip()
        return email

    def clean_company_contact_phone(self):
        """Clean phone number format"""
        phone = self.cleaned_data.get('company_contact_phone')
        if phone:
            # Remove any non-digit characters except + and -
            import re
            phone = re.sub(r'[^\d\+\-\(\)\s]', '', phone)
        return phone