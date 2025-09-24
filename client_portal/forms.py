# client_portal/forms.py

from django import forms
from django.contrib.auth.models import User
from .models import ClientProfile, ClientMessage
from claims.models import Claim
from applications.models import Quote


class ClientLoginForm(forms.Form):
    """Client portal login form"""
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username or Email'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        })
    )
    remember_me = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )


class ClientProfileForm(forms.ModelForm):
    """Client profile update form"""
    first_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = ClientProfile
        fields = [
            'phone', 'mobile_phone', 'position', 'department',
            'receive_emails', 'receive_sms'
        ]
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'mobile_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'position': forms.TextInput(attrs={'class': 'form-control'}),
            'department': forms.TextInput(attrs={'class': 'form-control'}),
            'receive_emails': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'receive_sms': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            self.fields['email'].initial = user.email
    
    def save(self, commit=True):
        profile = super().save(commit=False)
        if commit:
            # Update user fields
            user = profile.user
            user.first_name = self.cleaned_data['first_name']
            user.last_name = self.cleaned_data['last_name']
            user.email = self.cleaned_data['email']
            user.save()
            profile.save()
        return profile


class ClientClaimForm(forms.ModelForm):
    """Simplified claim submission form for clients"""
    
    class Meta:
        model = Claim
        fields = [
            'quote', 'claim_type', 'claimant_name', 'claimant_phone',
            'claimant_email', 'claimant_address', 'date_of_loss',
            'time_of_loss', 'location_of_loss', 'cause_of_loss',
            'loss_description', 'estimated_loss', 'police_report_number',
            'injuries_reported', 'property_damage'
        ]
        widgets = {
            'quote': forms.Select(attrs={'class': 'form-control'}),
            'claim_type': forms.Select(attrs={'class': 'form-control'}),
            'claimant_name': forms.TextInput(attrs={'class': 'form-control'}),
            'claimant_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'claimant_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'claimant_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'date_of_loss': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'time_of_loss': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'location_of_loss': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'cause_of_loss': forms.TextInput(attrs={'class': 'form-control'}),
            'loss_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'estimated_loss': forms.NumberInput(attrs={'class': 'form-control'}),
            'police_report_number': forms.TextInput(attrs={'class': 'form-control'}),
            'injuries_reported': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'property_damage': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        company = kwargs.pop('company', None)
        super().__init__(*args, **kwargs)
        
        if company:
            # Limit quotes to company's accepted quotes
            self.fields['quote'].queryset = Quote.objects.filter(
                application__company=company,
                quote_status='accepted'
            ).select_related('application')
            
            # Pre-populate claimant info
            self.fields['claimant_name'].initial = company.company_name
            self.fields['claimant_email'].initial = company.primary_contact_email
            self.fields['claimant_phone'].initial = company.primary_contact_phone


class ClientMessageForm(forms.ModelForm):
    """Message form for client communication"""
    
    class Meta:
        model = ClientMessage
        fields = ['subject', 'message', 'priority', 'quote', 'claim']
        widgets = {
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'quote': forms.Select(attrs={'class': 'form-control'}),
            'claim': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        company = kwargs.pop('company', None)
        super().__init__(*args, **kwargs)
        
        if company:
            self.fields['quote'].queryset = Quote.objects.filter(
                application__company=company
            )
            self.fields['claim'].queryset = Claim.objects.filter(
                quote__application__company=company
            )
        
        self.fields['quote'].required = False
        self.fields['claim'].required = False


class PaymentForm(forms.Form):
    """Payment processing form"""
    cardholder_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Name on Card'
        })
    )
    card_number = forms.CharField(
        max_length=19,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Card Number'
        })
    )
    expiry_month = forms.ChoiceField(
        choices=[(i, f'{i:02d}') for i in range(1, 13)],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    expiry_year = forms.ChoiceField(
        choices=[(i, i) for i in range(2025, 2036)],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    cvv = forms.CharField(
        max_length=4,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'CVV'
        })
    )
    billing_address = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Billing Address'
        })
    )