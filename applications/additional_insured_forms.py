# Path: applications/additional_insured_forms.py
# Forms for managing additional insureds

from django import forms
from django.core.exceptions import ValidationError
from .additional_insured_models import AdditionalInsured, AdditionalInsuredSchedule

# US States for dropdowns
US_STATES = [
    ('', 'Select State'),
    ('AL', 'Alabama'), ('AK', 'Alaska'), ('AZ', 'Arizona'), ('AR', 'Arkansas'),
    ('CA', 'California'), ('CO', 'Colorado'), ('CT', 'Connecticut'), ('DE', 'Delaware'),
    ('FL', 'Florida'), ('GA', 'Georgia'), ('HI', 'Hawaii'), ('ID', 'Idaho'),
    ('IL', 'Illinois'), ('IN', 'Indiana'), ('IA', 'Iowa'), ('KS', 'Kansas'),
    ('KY', 'Kentucky'), ('LA', 'Louisiana'), ('ME', 'Maine'), ('MD', 'Maryland'),
    ('MA', 'Massachusetts'), ('MI', 'Michigan'), ('MN', 'Minnesota'), ('MS', 'Mississippi'),
    ('MO', 'Missouri'), ('MT', 'Montana'), ('NE', 'Nebraska'), ('NV', 'Nevada'),
    ('NH', 'New Hampshire'), ('NJ', 'New Jersey'), ('NM', 'New Mexico'), ('NY', 'New York'),
    ('NC', 'North Carolina'), ('ND', 'North Dakota'), ('OH', 'Ohio'), ('OK', 'Oklahoma'),
    ('OR', 'Oregon'), ('PA', 'Pennsylvania'), ('RI', 'Rhode Island'), ('SC', 'South Carolina'),
    ('SD', 'South Dakota'), ('TN', 'Tennessee'), ('TX', 'Texas'), ('UT', 'Utah'),
    ('VT', 'Vermont'), ('VA', 'Virginia'), ('WA', 'Washington'), ('WV', 'West Virginia'),
    ('WI', 'Wisconsin'), ('WY', 'Wyoming'),
]


class AdditionalInsuredForm(forms.ModelForm):
    """Form for adding/editing additional insureds"""
    
    state = forms.ChoiceField(
        choices=US_STATES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=True
    )
    
    class Meta:
        model = AdditionalInsured
        fields = [
            'ai_number',
            'ai_type',
            'name',
            'address_line_1',
            'address_line_2',
            'city',
            'state',
            'zip_code',
            'contact_name',
            'contact_email',
            'contact_phone',
            'certificate_required',
            'certificate_frequency',
            'coverage_gl',
            'coverage_auto',
            'coverage_property',
            'coverage_umbrella',
            'waiver_of_subrogation',
            'primary_non_contributory',
            'additional_requirements',
            'effective_date',
            'expiration_date',
        ]
        
        widgets = {
            'ai_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'AI-001',
                'maxlength': 10,
            }),
            'ai_type': forms.Select(attrs={
                'class': 'form-select',
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Company or Individual Name',
                'required': True,
            }),
            'address_line_1': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '123 Main Street',
                'required': True,
            }),
            'address_line_2': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Suite 100 (optional)',
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'City',
                'required': True,
            }),
            'zip_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '12345',
                'maxlength': 10,
            }),
            'contact_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Contact Person',
            }),
            'contact_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'email@example.com',
            }),
            'contact_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '(555) 123-4567',
            }),
            'certificate_required': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
            'certificate_frequency': forms.Select(attrs={
                'class': 'form-select',
            }),
            'coverage_gl': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
            'coverage_auto': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
            'coverage_property': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
            'coverage_umbrella': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
            'waiver_of_subrogation': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
            'primary_non_contributory': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
            'additional_requirements': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Any additional requirements or notes',
            }),
            'effective_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),
            'expiration_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),
        }
        
        labels = {
            'ai_number': 'AI Number',
            'ai_type': 'Type',
            'coverage_gl': 'General Liability',
            'coverage_auto': 'Auto Liability',
            'coverage_property': 'Property',
            'coverage_umbrella': 'Umbrella/Excess',
            'waiver_of_subrogation': 'Waiver of Subrogation',
            'primary_non_contributory': 'Primary & Non-Contributory',
        }
        
        help_texts = {
            'ai_number': 'Unique identifier (auto-generated if blank)',
            'certificate_frequency': 'How often certificates need to be issued',
            'additional_requirements': 'Special provisions or requirements',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make ai_number optional for auto-generation
        self.fields['ai_number'].required = False
        
        # Set default effective date to today if not editing
        if not self.instance.pk:
            from datetime import date
            self.fields['effective_date'].initial = date.today()
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Ensure at least one coverage type is selected if certificate is required
        if cleaned_data.get('certificate_required'):
            coverage_types = [
                cleaned_data.get('coverage_gl'),
                cleaned_data.get('coverage_auto'),
                cleaned_data.get('coverage_property'),
                cleaned_data.get('coverage_umbrella'),
            ]
            if not any(coverage_types):
                raise ValidationError(
                    "At least one coverage type must be selected when certificate is required."
                )
        
        return cleaned_data


class BulkAdditionalInsuredForm(forms.ModelForm):
    """Simplified form for bulk adding additional insureds"""
    
    state = forms.ChoiceField(
        choices=[('', 'State')] + [(code, code) for code, name in US_STATES[1:]],
        widget=forms.Select(attrs={'class': 'form-select form-select-sm'}),
        required=False
    )
    
    class Meta:
        model = AdditionalInsured
        fields = [
            'ai_number',
            'ai_type',
            'name',
            'address_line_1',
            'city',
            'state',
            'zip_code',
            'certificate_required',
        ]
        
        widgets = {
            'ai_number': forms.TextInput(attrs={
                'class': 'form-control form-control-sm',
                'placeholder': 'Auto',
            }),
            'ai_type': forms.Select(attrs={
                'class': 'form-select form-select-sm',
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control form-control-sm',
                'placeholder': 'Name',
            }),
            'address_line_1': forms.TextInput(attrs={
                'class': 'form-control form-control-sm',
                'placeholder': 'Address',
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control form-control-sm',
                'placeholder': 'City',
            }),
            'zip_code': forms.TextInput(attrs={
                'class': 'form-control form-control-sm',
                'placeholder': 'ZIP',
            }),
            'certificate_required': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # All fields optional for bulk entry
        for field in self.fields:
            self.fields[field].required = False


class AdditionalInsuredScheduleForm(forms.ModelForm):
    """Form for creating AI schedules"""
    
    class Meta:
        model = AdditionalInsuredSchedule
        fields = [
            'schedule_name',
            'schedule_type',
            'filter_types',
        ]
        
        widgets = {
            'schedule_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., All Landlords Schedule',
            }),
            'schedule_type': forms.Select(attrs={
                'class': 'form-select',
            }),
            'filter_types': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'landlord, vendor (comma-separated)',
            }),
        }
        
        help_texts = {
            'filter_types': 'Enter comma-separated AI types for filtering',
        }
    
    def clean_filter_types(self):
        """Validate filter types"""
        filter_types = self.cleaned_data.get('filter_types', '')
        schedule_type = self.cleaned_data.get('schedule_type')
        
        if schedule_type == 'by_type' and not filter_types:
            raise ValidationError("Filter types are required when schedule type is 'By Type'")
        
        return filter_types


class AdditionalInsuredSearchForm(forms.Form):
    """Form for searching and filtering additional insureds"""
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by name...',
        })
    )
    
    ai_type = forms.ChoiceField(
        required=False,
        choices=[('', 'All Types')] + AdditionalInsured.AI_TYPE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select',
        })
    )
    
    certificate_required = forms.ChoiceField(
        required=False,
        choices=[
            ('', 'All'),
            ('yes', 'Certificate Required'),
            ('no', 'No Certificate'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-select',
        })
    )
    
    active_only = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
        })
    )