# Skye/forms.py

from django import forms
from django.forms import ModelForm
from .models import (
    Company, CompanyContact, CompanyLocation, Products, Orders,
    Applications, EmployeeContact, EmployeeLocation, Venture,
    Coverage, Parameter, ApplicationQuestion, ApplicationResponse,
    Cover, Options, Limits, Retention, OrderOption, Document,
    Broker, BrokerLocation, BrokerContact, Stage, FlowOrigin,
    Workflow, Task, WorkflowDetail, ParameterType
)


class CompanyForm(ModelForm):
    class Meta:
        model = Company
        fields = ['company_name']
        widgets = {
            'company_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter company name'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['company_name'].required = True


class CompanyContactForm(ModelForm):
    class Meta:
        model = CompanyContact
        fields = [
            'company', 'company_contact_first', 'company_contact_last',
            'company_contact_phone', 'company_contact_email',
            'company_contact_title', 'company_contact_salutation', 'company_web'
        ]
        widgets = {
            'company': forms.Select(attrs={'class': 'form-control'}),
            'company_contact_first': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'First name'
            }),
            'company_contact_last': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Last name'
            }),
            'company_contact_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phone number'
            }),
            'company_contact_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email address'
            }),
            'company_contact_title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Job title'
            }),
            'company_contact_salutation': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Salutation'
            }),
            'company_web': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'Website URL'
            })
        }


class CompanyLocationForm(ModelForm):
    class Meta:
        model = CompanyLocation
        fields = [
            'company', 'company_location_address_1', 'company_location_address_2',
            'company_location_city', 'company_location_state', 'company_location_zip',
            'company_mailing'
        ]
        widgets = {
            'company': forms.Select(attrs={'class': 'form-control'}),
            'company_location_address_1': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Address line 1'
            }),
            'company_location_address_2': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Address line 2'
            }),
            'company_location_city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'City'
            }),
            'company_location_state': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'State'
            }),
            'company_location_zip': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ZIP code'
            }),
            'company_mailing': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }


class ProductsForm(ModelForm):
    class Meta:
        model = Products
        fields = [
            'product_name', 'venture', 'coverage', 'product_code',
            'product_prefix', 'documents_name'
        ]
        widgets = {
            'product_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Product name'
            }),
            'venture': forms.Select(attrs={'class': 'form-control'}),
            'coverage': forms.Select(attrs={'class': 'form-control'}),
            'product_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Product code'
            }),
            'product_prefix': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Product prefix'
            }),
            'documents_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Documents name'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['venture'].queryset = Venture.objects.all()
        self.fields['coverage'].queryset = Coverage.objects.all()
        self.fields['product_name'].required = True


class OrdersForm(ModelForm):
    class Meta:
        model = Orders
        fields = [
            'stage', 'employee', 'flow_origin', 'company', 'products',
            'venture', 'order_created', 'workflow', 'workflow_detail'
        ]
        widgets = {
            'stage': forms.Select(attrs={'class': 'form-control'}),
            'employee': forms.Select(attrs={'class': 'form-control'}),
            'flow_origin': forms.Select(attrs={'class': 'form-control'}),
            'company': forms.Select(attrs={'class': 'form-control'}),
            'products': forms.Select(attrs={'class': 'form-control'}),
            'venture': forms.Select(attrs={'class': 'form-control'}),
            'order_created': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'workflow': forms.Select(attrs={'class': 'form-control'}),
            'workflow_detail': forms.Select(attrs={'class': 'form-control'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['company'].queryset = Company.objects.all()
        self.fields['products'].queryset = Products.objects.all()
        self.fields['employee'].queryset = EmployeeContact.objects.all()
        self.fields['venture'].queryset = Venture.objects.all()
        self.fields['stage'].queryset = Stage.objects.all()
        self.fields['flow_origin'].queryset = FlowOrigin.objects.all()
        self.fields['workflow'].queryset = Workflow.objects.all()
        self.fields['workflow_detail'].queryset = WorkflowDetail.objects.all()


class ApplicationsForm(ModelForm):
    class Meta:
        model = Applications
        fields = ['application_name', 'product']
        widgets = {
            'application_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Application name'
            }),
            'product': forms.Select(attrs={'class': 'form-control'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['product'].queryset = Products.objects.all()
        self.fields['application_name'].required = True


class EmployeeContactForm(ModelForm):
    class Meta:
        model = EmployeeContact
        fields = [
            'employee_location', 'employee_name_first', 'employee_name_last',
            'employee_email', 'employee_name_combined'
        ]
        widgets = {
            'employee_location': forms.Select(attrs={'class': 'form-control'}),
            'employee_name_first': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'First name'
            }),
            'employee_name_last': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Last name'
            }),
            'employee_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email address'
            }),
            'employee_name_combined': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Combined name'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['employee_location'].queryset = EmployeeLocation.objects.all()


class EmployeeLocationForm(ModelForm):
    class Meta:
        model = EmployeeLocation
        fields = [
            'venture', 'employee_location_name', 'employee_location_address_1',
            'employee_location_address_2', 'employee_location_city',
            'employee_location_state', 'employee_location_zip'
        ]
        widgets = {
            'venture': forms.Select(attrs={'class': 'form-control'}),
            'employee_location_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Location name'
            }),
            'employee_location_address_1': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Address line 1'
            }),
            'employee_location_address_2': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Address line 2'
            }),
            'employee_location_city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'City'
            }),
            'employee_location_state': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'State'
            }),
            'employee_location_zip': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ZIP code'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['venture'].queryset = Venture.objects.all()


class VentureForm(ModelForm):
    class Meta:
        model = Venture
        fields = [
            'venture_name', 'venture_address_1', 'venture_address_2',
            'venture_city', 'venture_state', 'venture_zip'
        ]
        widgets = {
            'venture_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Venture name'
            }),
            'venture_address_1': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Address line 1'
            }),
            'venture_address_2': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Address line 2'
            }),
            'venture_city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'City'
            }),
            'venture_state': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'State'
            }),
            'venture_zip': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ZIP code'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['venture_name'].required = True


class ApplicationQuestionForm(ModelForm):
    class Meta:
        model = ApplicationQuestion
        fields = ['application', 'custom_question', 'parameter']
        widgets = {
            'application': forms.Select(attrs={'class': 'form-control'}),
            'custom_question': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter your question'
            }),
            'parameter': forms.Select(attrs={'class': 'form-control'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['application'].queryset = Applications.objects.all()
        self.fields['parameter'].queryset = Parameter.objects.all()


class ApplicationResponseForm(ModelForm):
    class Meta:
        model = ApplicationResponse
        fields = ['application', 'application_question', 'order', 'response']
        widgets = {
            'application': forms.Select(attrs={'class': 'form-control'}),
            'application_question': forms.Select(attrs={'class': 'form-control'}),
            'order': forms.Select(attrs={'class': 'form-control'}),
            'response': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Enter response'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['application'].queryset = Applications.objects.all()
        self.fields['application_question'].queryset = ApplicationQuestion.objects.all()
        self.fields['order'].queryset = Orders.objects.all()


class CoverageForm(ModelForm):
    class Meta:
        model = Coverage
        fields = ['coverage_name']
        widgets = {
            'coverage_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Coverage name'
            })
        }


class ParameterForm(ModelForm):
    class Meta:
        model = Parameter
        fields = [
            'parameter_name', 'parameter_type', 'parameter_docs',
            'parameter_quote', 'parameter_binder', 'parameter_policy'
        ]
        widgets = {
            'parameter_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Parameter name'
            }),
            'parameter_type': forms.Select(attrs={'class': 'form-control'}),
            'parameter_docs': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Parameter documentation'
            }),
            'parameter_quote': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'parameter_binder': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'parameter_policy': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['parameter_type'].queryset = ParameterType.objects.all()


class DocumentForm(ModelForm):
    class Meta:
        model = Document
        fields = [
            'document_name', 'product', 'document_number', 'default_document',
            'document_added', 'document_expiration', 'document_prior_version',
            'document_code'
        ]
        widgets = {
            'document_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Document name'
            }),
            'product': forms.Select(attrs={'class': 'form-control'}),
            'document_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Document number'
            }),
            'default_document': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'document_added': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'document_expiration': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'document_prior_version': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Prior version'
            }),
            'document_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Document code'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['product'].queryset = Products.objects.all()


# Search Forms
class CompanySearchForm(forms.Form):
    search = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search companies...'
        })
    )


class ProductSearchForm(forms.Form):
    search = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search products...'
        })
    )
    venture = forms.ModelChoiceField(
        queryset=Venture.objects.all(),
        required=False,
        empty_label="All Ventures",
        widget=forms.Select(attrs={'class': 'form-control'})
    )


class OrderSearchForm(forms.Form):
    search = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search orders...'
        })
    )
    stage = forms.ModelChoiceField(
        queryset=Stage.objects.all(),
        required=False,
        empty_label="All Stages",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    company = forms.ModelChoiceField(
        queryset=Company.objects.all(),
        required=False,
        empty_label="All Companies",
        widget=forms.Select(attrs={'class': 'form-control'})
    )