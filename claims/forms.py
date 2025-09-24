# claims/forms.py

from django import forms
from django.contrib.auth.models import User
from decimal import Decimal
from .models import Claim, ClaimDocument, ClaimNote, ClaimPayment, ClaimReserve
from applications.models import Quote, Certificate


class ClaimFNOLForm(forms.ModelForm):
    """First Notice of Loss form for creating new claims"""
    
    initial_reserve = forms.DecimalField(
        required=False,
        max_digits=12,
        decimal_places=2,
        min_value=Decimal('0'),
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Initial reserve amount'
        }),
        help_text='Optional: Set an initial reserve for this claim'
    )
    
    class Meta:
        model = Claim
        fields = [
            'quote', 'certificate', 'claim_type', 'severity',
            'claimant_name', 'claimant_phone', 'claimant_email', 'claimant_address',
            'is_insured', 'date_of_loss', 'time_of_loss', 'location_of_loss',
            'loss_description', 'cause_of_loss', 'estimated_loss', 'deductible',
            'police_report_number', 'injuries_reported', 'property_damage',
            'subrogation_possible', 'litigation_pending'
        ]
        widgets = {
            'quote': forms.Select(attrs={'class': 'form-control'}),
            'certificate': forms.Select(attrs={'class': 'form-control'}),
            'claim_type': forms.Select(attrs={'class': 'form-control'}),
            'severity': forms.Select(attrs={'class': 'form-control'}),
            'claimant_name': forms.TextInput(attrs={'class': 'form-control'}),
            'claimant_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'claimant_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'claimant_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_insured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'date_of_loss': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'time_of_loss': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'location_of_loss': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'loss_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'cause_of_loss': forms.TextInput(attrs={'class': 'form-control'}),
            'estimated_loss': forms.NumberInput(attrs={'class': 'form-control'}),
            'deductible': forms.NumberInput(attrs={'class': 'form-control'}),
            'police_report_number': forms.TextInput(attrs={'class': 'form-control'}),
            'injuries_reported': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'property_damage': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'subrogation_possible': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'litigation_pending': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Customize quote queryset to show meaningful information
        self.fields['quote'].queryset = Quote.objects.select_related(
            'application__company'
        ).order_by('-created_at')
        
        # Customize certificate queryset
        if 'certificate' in self.fields:
            self.fields['certificate'].queryset = Certificate.objects.select_related(
                'quote__application__company'
            ).order_by('-created_at')
            self.fields['certificate'].required = False


class ClaimUpdateForm(forms.ModelForm):
    """Form for updating existing claim information"""
    
    class Meta:
        model = Claim
        fields = [
            'claim_status', 'severity', 'adjuster',
            'claimant_name', 'claimant_phone', 'claimant_email', 'claimant_address',
            'location_of_loss', 'loss_description', 'cause_of_loss',
            'estimated_loss', 'deductible', 'reserve_amount',
            'police_report_number', 'injuries_reported', 'property_damage',
            'subrogation_possible', 'litigation_pending', 'internal_notes'
        ]
        widgets = {
            'claim_status': forms.Select(attrs={'class': 'form-control'}),
            'severity': forms.Select(attrs={'class': 'form-control'}),
            'adjuster': forms.Select(attrs={'class': 'form-control'}),
            'claimant_name': forms.TextInput(attrs={'class': 'form-control'}),
            'claimant_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'claimant_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'claimant_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'location_of_loss': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'loss_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'cause_of_loss': forms.TextInput(attrs={'class': 'form-control'}),
            'estimated_loss': forms.NumberInput(attrs={'class': 'form-control'}),
            'deductible': forms.NumberInput(attrs={'class': 'form-control'}),
            'reserve_amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'police_report_number': forms.TextInput(attrs={'class': 'form-control'}),
            'injuries_reported': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'property_damage': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'subrogation_possible': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'litigation_pending': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'internal_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Limit adjuster choices to active users
        self.fields['adjuster'].queryset = User.objects.filter(
            is_active=True
        ).order_by('last_name', 'first_name')
        self.fields['adjuster'].required = False


class ClaimNoteForm(forms.ModelForm):
    """Form for adding notes to a claim"""
    
    class Meta:
        model = ClaimNote
        fields = ['note_type', 'subject', 'content', 'is_public']
        widgets = {
            'note_type': forms.Select(attrs={'class': 'form-control'}),
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'is_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ClaimPaymentForm(forms.ModelForm):
    """Form for adding payments to a claim"""
    
    class Meta:
        model = ClaimPayment
        fields = [
            'payment_type', 'payment_method', 'payee_name',
            'amount', 'check_number', 'payment_date',
            'cleared_date', 'notes'
        ]
        widgets = {
            'payment_type': forms.Select(attrs={'class': 'form-control'}),
            'payment_method': forms.Select(attrs={'class': 'form-control'}),
            'payee_name': forms.TextInput(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'check_number': forms.TextInput(attrs={'class': 'form-control'}),
            'payment_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'cleared_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class ClaimDocumentForm(forms.ModelForm):
    """Form for uploading documents to a claim"""
    
    class Meta:
        model = ClaimDocument
        fields = ['document_type', 'document_name', 'description', 'file']
        widgets = {
            'document_type': forms.Select(attrs={'class': 'form-control'}),
            'document_name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
        }


class ClaimReserveForm(forms.ModelForm):
    """Form for adjusting claim reserves"""
    
    class Meta:
        model = ClaimReserve
        fields = ['reserve_type', 'amount', 'reason', 'effective_date']
        widgets = {
            'reserve_type': forms.Select(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'effective_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }


class ClaimSearchForm(forms.Form):
    """Form for searching and filtering claims"""
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by claim number, claimant name, company, or cause...'
        })
    )
    
    status = forms.ChoiceField(
        required=False,
        choices=[('', 'All Statuses')] + Claim.CLAIM_STATUS,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    claim_type = forms.ChoiceField(
        required=False,
        choices=[('', 'All Types')] + Claim.CLAIM_TYPE,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    severity = forms.ChoiceField(
        required=False,
        choices=[('', 'All Severities')] + Claim.SEVERITY,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )