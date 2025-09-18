# core/forms.py
from django import forms
from .models import (
    CompanyContact, Company, Options, CompanyLocation, CompanyAlias,
    ApplicationResponse, OrderOption, OrderDataVert, DocumentDetail,
    Applications, ApplicationQuestion, Orders, Cover, Retention, 
    Limits, Document, Parameter, ParameterMap
)

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


class CompanyForm(forms.ModelForm):
    """Form for editing Company records"""
    
    class Meta:
        model = Company
        fields = ['company_name']
        
        widgets = {
            'company_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter company name',
                'maxlength': 200,
                'required': True
            })
        }
        
        labels = {
            'company_name': 'Company Name'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['company_name'].required = True

    def clean_company_name(self):
        """Validate and clean company name"""
        name = self.cleaned_data.get('company_name')
        if name:
            name = name.strip()
            if len(name) < 2:
                raise forms.ValidationError("Company name must be at least 2 characters long.")
        return name


class OptionsForm(forms.ModelForm):
    """Form for editing Options records"""
    
    class Meta:
        model = Options
        fields = ['option_name']
        
        widgets = {
            'option_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter option name',
                'maxlength': 200,
                'required': True
            })
        }
        
        labels = {
            'option_name': 'Option Name'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['option_name'].required = True

    def clean_option_name(self):
        """Validate and clean option name"""
        name = self.cleaned_data.get('option_name')
        if name:
            name = name.strip()
            if len(name) < 2:
                raise forms.ValidationError("Option name must be at least 2 characters long.")
        return name

class CompanyLocationForm(forms.ModelForm):
    """Form for editing CompanyLocation records"""
    class Meta:
        model = CompanyLocation
        fields = [
            'company', 'company_location_address_1', 'company_location_address_2',
            'company_location_city', 'company_location_state', 'company_location_zip',
            'company_mailing'
        ]
        
        widgets = {
            'company': forms.Select(attrs={'class': 'form-control'}),
            'company_location_address_1': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Street Address'}),
            'company_location_address_2': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Suite, Unit, etc. (optional)'}),
            'company_location_city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'}),
            'company_location_state': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'State'}),
            'company_location_zip': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ZIP Code'}),
            'company_mailing': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['company'].queryset = Company.objects.all().order_by('company_name')
        self.fields['company'].empty_label = "Select a Company"
        # Make optional fields
        for field in ['company_location_address_2', 'company_mailing']:
            self.fields[field].required = False

class CompanyAliasForm(forms.ModelForm):
    """Form for editing CompanyAlias records"""
    class Meta:
        model = CompanyAlias
        fields = [
            'company', 'company_alias_name', 'company_alias_retro_start', 'company_alias_retro_end',
            'company_alias_eff_dte', 'company_alias_exp_dte'
        ]
        
        widgets = {
            'company': forms.Select(attrs={'class': 'form-control'}),
            'company_alias_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Alias Name'}),
            'company_alias_retro_start': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'company_alias_retro_end': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'company_alias_eff_dte': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'company_alias_exp_dte': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['company'].queryset = Company.objects.all().order_by('company_name')
        self.fields['company'].empty_label = "Select a Company"
        # Make date fields optional
        for field in ['company_alias_retro_start', 'company_alias_retro_end', 'company_alias_eff_dte', 'company_alias_exp_dte']:
            self.fields[field].required = False

class ApplicationResponseForm(forms.ModelForm):
    """Form for editing ApplicationResponse records"""
    class Meta:
        model = ApplicationResponse
        fields = ['application', 'application_question', 'order', 'response']
        
        widgets = {
            'application': forms.Select(attrs={'class': 'form-control'}),
            'application_question': forms.Select(attrs={'class': 'form-control'}),
            'order': forms.Select(attrs={'class': 'form-control'}),
            'response': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter response...', 'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['application'].queryset = Applications.objects.all().order_by('application_name')
        self.fields['application'].empty_label = "Select an Application"
        self.fields['application_question'].queryset = ApplicationQuestion.objects.all()
        self.fields['application_question'].empty_label = "Select a Question"
        self.fields['order'].queryset = Orders.objects.all().order_by('-orders_id')[:100]  # Limit for performance
        self.fields['order'].empty_label = "Select an Order (optional)"
        # Make optional fields
        for field in ['order']:
            self.fields[field].required = False

class OrderOptionForm(forms.ModelForm):
    """Form for editing OrderOption records"""
    class Meta:
        model = OrderOption
        fields = [
            'orders', 'options', 'cover', 'order_option_include', 
            'retention', 'limits', 'premium', 'bound'
        ]
        
        widgets = {
            'orders': forms.Select(attrs={'class': 'form-control'}),
            'options': forms.Select(attrs={'class': 'form-control'}),
            'cover': forms.Select(attrs={'class': 'form-control'}),
            'order_option_include': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'retention': forms.Select(attrs={'class': 'form-control'}),
            'limits': forms.Select(attrs={'class': 'form-control'}),
            'premium': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'}),
            'bound': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['orders'].queryset = Orders.objects.all().order_by('-orders_id')[:100]
        self.fields['orders'].empty_label = "Select an Order"
        self.fields['options'].queryset = Options.objects.all().order_by('option_name')
        self.fields['options'].empty_label = "Select an Option"
        self.fields['cover'].queryset = Cover.objects.all().order_by('cover_name')
        self.fields['cover'].empty_label = "Select Cover"
        self.fields['retention'].queryset = Retention.objects.all()
        self.fields['retention'].empty_label = "Select Retention (optional)"
        self.fields['limits'].queryset = Limits.objects.all()
        self.fields['limits'].empty_label = "Select Limits (optional)"
        # Make optional fields
        for field in ['retention', 'limits', 'premium', 'order_option_include', 'bound']:
            self.fields[field].required = False

class OrderDataVertForm(forms.ModelForm):
    """Form for editing OrderDataVert records"""
    class Meta:
        model = OrderDataVert
        fields = ['order', 'parameter', 'vert_value', 'parameter_map']
        
        widgets = {
            'order': forms.Select(attrs={'class': 'form-control'}),
            'parameter': forms.Select(attrs={'class': 'form-control'}),
            'vert_value': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter value...', 'rows': 3}),
            'parameter_map': forms.Select(attrs={'class': 'form-control'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['order'].queryset = Orders.objects.all().order_by('-orders_id')[:100]
        self.fields['order'].empty_label = "Select an Order"
        self.fields['parameter'].queryset = Parameter.objects.all().order_by('parameter_name')
        self.fields['parameter'].empty_label = "Select a Parameter"
        self.fields['parameter_map'].queryset = ParameterMap.objects.all()
        self.fields['parameter_map'].empty_label = "Select Parameter Map (optional)"
        # Make optional fields
        self.fields['parameter_map'].required = False

class DocumentDetailForm(forms.ModelForm):
    """Form for editing DocumentDetail records"""
    class Meta:
        model = DocumentDetail
        fields = ['order_option', 'document']
        
        widgets = {
            'order_option': forms.Select(attrs={'class': 'form-control'}),
            'document': forms.Select(attrs={'class': 'form-control'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['order_option'].queryset = OrderOption.objects.all().order_by('-order_option_id')[:100]
        self.fields['order_option'].empty_label = "Select an Order Option"
        self.fields['document'].queryset = Document.objects.all().order_by('document_name')
        self.fields['document'].empty_label = "Select a Document"