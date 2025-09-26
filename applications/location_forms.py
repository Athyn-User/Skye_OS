# Path: applications/location_forms.py
# Complete forms with properly configured state dropdowns

from django import forms
from django.core.exceptions import ValidationError
from decimal import Decimal
from .location_models import PolicyLocation, LocationSchedule

# Define US states as a constant so it can be reused
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

US_STATES_SHORT = [('', 'State')] + [(code, code) for code, name in US_STATES[1:]]


class PolicyLocationForm(forms.ModelForm):
    """Form for adding/editing policy locations"""
    
    # Override state as a ChoiceField
    state = forms.ChoiceField(
        choices=US_STATES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=True,
        label='State'
    )
    
    class Meta:
        model = PolicyLocation
        fields = [
            'location_number',
            'location_name',
            'street_address',
            'address_line_2',
            'city', 
            'state',  # Now using the ChoiceField defined above
            'zip_code',
            'building_limit',
            'contents_limit',
            'effective_date',
        ]
        
        widgets = {
            'location_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '001',
                'maxlength': 10,
            }),
            'location_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Optional location description',
            }),
            'street_address': forms.TextInput(attrs={
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
            # state widget is handled by the ChoiceField above
            'zip_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '12345',
                'maxlength': 10,
                'required': True,
            }),
            'building_limit': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '1000000',
                'step': '1000',
                'min': '0',
            }),
            'contents_limit': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '500000',
                'step': '1000',
                'min': '0',
            }),
            'effective_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),
        }
        
        labels = {
            'location_number': 'Location Number',
            'location_name': 'Location Name/Description',
            'street_address': 'Street Address',
            'address_line_2': 'Address Line 2',
            'city': 'City',
            'zip_code': 'ZIP Code',
            'building_limit': 'Building Limit ($)',
            'contents_limit': 'Contents Limit ($)',
            'effective_date': 'Effective Date',
        }
        
        help_texts = {
            'location_number': 'Unique identifier for this location (e.g., 001, 002)',
            'building_limit': 'Coverage limit for building/structure',
            'contents_limit': 'Coverage limit for contents/equipment',
            'effective_date': 'Date this location becomes effective under the policy',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make location_number optional for auto-generation
        self.fields['location_number'].required = False
    
    def clean(self):
        cleaned_data = super().clean()
        building_limit = cleaned_data.get('building_limit', 0) or 0
        contents_limit = cleaned_data.get('contents_limit', 0) or 0
        
        if building_limit <= 0 and contents_limit <= 0:
            raise ValidationError("At least one coverage limit must be greater than zero.")
        
        return cleaned_data


class BulkLocationForm(forms.ModelForm):
    """Simplified form for bulk location entry"""
    
    # Override state as a ChoiceField with shorter labels
    state = forms.ChoiceField(
        choices=US_STATES_SHORT,
        widget=forms.Select(attrs={'class': 'form-select form-select-sm'}),
        required=False,
        label='State'
    )
    
    class Meta:
        model = PolicyLocation
        fields = [
            'location_number',
            'street_address',
            'city',
            'state',
            'zip_code',
            'building_limit',
            'contents_limit',
        ]
        
        widgets = {
            'location_number': forms.TextInput(attrs={
                'class': 'form-control form-control-sm',
                'placeholder': 'Auto',
            }),
            'street_address': forms.TextInput(attrs={
                'class': 'form-control form-control-sm',
                'placeholder': 'Street Address',
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control form-control-sm',
                'placeholder': 'City',
            }),
            # state widget is handled by the ChoiceField above
            'zip_code': forms.TextInput(attrs={
                'class': 'form-control form-control-sm',
                'placeholder': 'ZIP',
                'maxlength': 10,
            }),
            'building_limit': forms.NumberInput(attrs={
                'class': 'form-control form-control-sm',
                'placeholder': '1000000',
                'step': '1000',
                'min': '0',
            }),
            'contents_limit': forms.NumberInput(attrs={
                'class': 'form-control form-control-sm',
                'placeholder': '500000',
                'step': '1000',
                'min': '0',
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # All fields optional for bulk entry flexibility
        for field in self.fields:
            self.fields[field].required = False


class LocationScheduleForm(forms.ModelForm):
    """Form for creating and managing location schedules"""
    
    class Meta:
        model = LocationSchedule
        fields = [
            'schedule_name',
            'schedule_type',
            'include_states',
            'include_occupancies',
            'min_limit',
            'max_limit',
            'show_building_limits',
            'show_contents_limits',
            'show_deductibles',
            'show_construction_details',
            'show_protection_features',
        ]
        
        widgets = {
            'schedule_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'All Locations Schedule',
                'required': True,
            }),
            'schedule_type': forms.Select(attrs={
                'class': 'form-select',
                'onchange': 'toggleScheduleCriteria()',
            }),
            'include_states': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'CA, NY, TX (comma-separated state codes)',
            }),
            'include_occupancies': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'office, retail (comma-separated)',
            }),
            'min_limit': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '100000',
                'step': '1000',
                'min': '0',
            }),
            'max_limit': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '10000000',
                'step': '1000',
                'min': '0',
            }),
            'show_building_limits': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
            'show_contents_limits': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
            'show_deductibles': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
            'show_construction_details': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
            'show_protection_features': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
        }
        
        help_texts = {
            'schedule_name': 'Descriptive name for this location schedule',
            'schedule_type': 'How locations should be included in this schedule',
            'include_states': 'Comma-separated list of state codes',
            'include_occupancies': 'Comma-separated list of occupancy types',
            'min_limit': 'Minimum total limit for location inclusion',
            'max_limit': 'Maximum total limit for location inclusion',
        }
    
    def clean(self):
        cleaned_data = super().clean()
        schedule_type = cleaned_data.get('schedule_type')
        include_states = cleaned_data.get('include_states')
        include_occupancies = cleaned_data.get('include_occupancies')
        min_limit = cleaned_data.get('min_limit')
        max_limit = cleaned_data.get('max_limit')
        
        # Validation based on schedule type
        if schedule_type == 'locations_by_state' and not include_states:
            raise ValidationError("States must be specified for state-based schedules.")
        
        if schedule_type == 'locations_by_occupancy' and not include_occupancies:
            raise ValidationError("Occupancies must be specified for occupancy-based schedules.")
        
        # Validate limit range
        if min_limit and max_limit and min_limit >= max_limit:
            raise ValidationError("Minimum limit must be less than maximum limit.")
        
        return cleaned_data


class LocationSearchForm(forms.Form):
    """Form for searching and filtering locations"""
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search locations...',
        })
    )
    
    state = forms.ChoiceField(
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select',
        })
    )
    
    occupancy = forms.ChoiceField(
        required=False,
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
    
    def __init__(self, policy=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        if policy:
            # Populate state choices from policy locations
            states = policy.locations.values_list('state', flat=True).distinct().order_by('state')
            state_choices = [('', 'All States')] + [(s, s) for s in states if s]
            self.fields['state'].choices = state_choices
            
            # Populate occupancy choices
            occupancies = policy.locations.exclude(primary_occupancy='').values_list(
                'primary_occupancy', flat=True
            ).distinct().order_by('primary_occupancy')
            occupancy_choices = [('', 'All Occupancies')] + [(o, o.title()) for o in occupancies if o]
            self.fields['occupancy'].choices = occupancy_choices