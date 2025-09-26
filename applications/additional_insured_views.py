# Path: applications/additional_insured_views.py
# Views for managing additional insureds

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.forms import modelformset_factory
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from datetime import date

from .models import Policy, Certificate
from .additional_insured_models import (
    AdditionalInsured,
    AdditionalInsuredCertificate,
    AdditionalInsuredSchedule
)
from .additional_insured_forms import (
    AdditionalInsuredForm,
    BulkAdditionalInsuredForm,
    AdditionalInsuredScheduleForm,
    AdditionalInsuredSearchForm
)


@login_required
def additional_insured_list(request, policy_id):
    """Main list view for additional insureds"""
    policy = get_object_or_404(Policy, policy_id=policy_id)
    
    # Initialize search form
    search_form = AdditionalInsuredSearchForm(request.GET)
    
    # Base queryset
    ais = policy.additional_insureds.all()
    
    # Apply filters
    if search_form.is_valid():
        # Search filter
        search = search_form.cleaned_data.get('search')
        if search:
            ais = ais.filter(
                Q(name__icontains=search) |
                Q(ai_number__icontains=search) |
                Q(contact_name__icontains=search)
            )
        
        # Type filter
        ai_type = search_form.cleaned_data.get('ai_type')
        if ai_type:
            ais = ais.filter(ai_type=ai_type)
        
        # Certificate filter
        cert_required = search_form.cleaned_data.get('certificate_required')
        if cert_required == 'yes':
            ais = ais.filter(certificate_required=True)
        elif cert_required == 'no':
            ais = ais.filter(certificate_required=False)
        
        # Active filter
        if search_form.cleaned_data.get('active_only'):
            ais = ais.filter(is_active=True)
    
    # Order by AI number
    ais = ais.order_by('ai_number')
    
    # Pagination
    paginator = Paginator(ais, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Summary statistics
    total_ais = policy.additional_insureds.filter(is_active=True).count()
    cert_required_count = policy.additional_insureds.filter(
        is_active=True,
        certificate_required=True
    ).count()
    
    # Count by type
    type_counts = policy.additional_insureds.filter(is_active=True).values(
        'ai_type'
    ).annotate(count=Count('ai_type'))
    
    context = {
        'policy': policy,
        'additional_insureds': page_obj,
        'search_form': search_form,
        'total_ais': total_ais,
        'cert_required_count': cert_required_count,
        'type_counts': type_counts,
        'object': policy,
        'object_type': 'policy',
        'active_tab': 'additional_insureds',
    }
    
    return render(request, 'applications/additional_insured_list.html', context)


@login_required
def add_additional_insured(request, policy_id):
    """Add a new additional insured"""
    policy = get_object_or_404(Policy, policy_id=policy_id)
    
    if request.method == 'POST':
        form = AdditionalInsuredForm(request.POST)
        if form.is_valid():
            ai = form.save(commit=False)
            ai.policy = policy
            ai.created_by = request.user
            
            # Auto-generate AI number if not provided
            if not ai.ai_number:
                existing_numbers = policy.additional_insureds.values_list(
                    'ai_number', flat=True
                )
                # Extract numbers and find the next one
                max_num = 0
                for num in existing_numbers:
                    try:
                        # Extract numeric part from AI-001 format
                        numeric = int(num.split('-')[1])
                        max_num = max(max_num, numeric)
                    except (IndexError, ValueError):
                        continue
                ai.ai_number = f"AI-{max_num + 1:03d}"
            
            ai.save()
            messages.success(request, f'Additional Insured {ai.name} added successfully!')
            
            # Check if need to generate certificate
            if ai.certificate_required:
                messages.info(
                    request,
                    f'Certificate required for {ai.name}. '
                    f'<a href="/policies/{policy_id}/additional-insureds/{ai.additional_insured_id}/certificate/" '
                    f'class="alert-link">Generate Certificate</a>',
                    extra_tags='safe'
                )
            
            return redirect('applications:additional_insured_list', policy_id=policy_id)
    else:
        # Set default effective date
        initial_data = {
            'effective_date': policy.effective_date,
            'certificate_required': True,
        }
        form = AdditionalInsuredForm(initial=initial_data)
    
    context = {
        'policy': policy,
        'form': form,
        'action': 'Add',
    }
    
    return render(request, 'applications/additional_insured_form.html', context)


@login_required
def edit_additional_insured(request, policy_id, ai_id):
    """Edit an existing additional insured"""
    policy = get_object_or_404(Policy, policy_id=policy_id)
    ai = get_object_or_404(AdditionalInsured, additional_insured_id=ai_id, policy=policy)
    
    if request.method == 'POST':
        form = AdditionalInsuredForm(request.POST, instance=ai)
        if form.is_valid():
            form.save()
            messages.success(request, f'Additional Insured {ai.name} updated successfully!')
            return redirect('applications:additional_insured_list', policy_id=policy_id)
    else:
        form = AdditionalInsuredForm(instance=ai)
    
    context = {
        'policy': policy,
        'additional_insured': ai,
        'form': form,
        'action': 'Edit',
    }
    
    return render(request, 'applications/additional_insured_form.html', context)


@login_required
@require_http_methods(["POST"])
def delete_additional_insured(request, policy_id, ai_id):
    """Soft delete an additional insured"""
    policy = get_object_or_404(Policy, policy_id=policy_id)
    ai = get_object_or_404(AdditionalInsured, additional_insured_id=ai_id, policy=policy)
    
    # Soft delete
    ai.is_active = False
    ai.save()
    
    messages.success(request, f'Additional Insured {ai.name} has been deactivated.')
    return redirect('applications:additional_insured_list', policy_id=policy_id)


@login_required
def bulk_add_additional_insureds(request, policy_id):
    """Bulk add multiple additional insureds"""
    policy = get_object_or_404(Policy, policy_id=policy_id)
    
    # Create formset for bulk entry
    AIFormSet = modelformset_factory(
        AdditionalInsured,
        form=BulkAdditionalInsuredForm,
        extra=5,
        can_delete=False
    )
    
    if request.method == 'POST':
        formset = AIFormSet(request.POST)
        if formset.is_valid():
            ais_added = 0
            
            for form in formset:
                if form.cleaned_data and form.cleaned_data.get('name'):
                    ai = form.save(commit=False)
                    ai.policy = policy
                    ai.created_by = request.user
                    ai.effective_date = policy.effective_date
                    
                    # Auto-generate AI number
                    if not ai.ai_number:
                        max_num = 0
                        for existing in policy.additional_insureds.all():
                            try:
                                num = int(existing.ai_number.split('-')[1])
                                max_num = max(max_num, num)
                            except:
                                continue
                        ai.ai_number = f"AI-{max_num + ais_added + 1:03d}"
                    
                    ai.save()
                    ais_added += 1
            
            if ais_added > 0:
                messages.success(request, f'{ais_added} Additional Insureds added successfully!')
                return redirect('applications:additional_insured_list', policy_id=policy_id)
            else:
                messages.warning(request, 'No Additional Insureds were added.')
    else:
        formset = AIFormSet(queryset=AdditionalInsured.objects.none())
    
    context = {
        'policy': policy,
        'formset': formset,
    }
    
    return render(request, 'applications/bulk_additional_insured_form.html', context)


@login_required
def generate_ai_certificate(request, policy_id, ai_id):
    """Generate or link a certificate for an additional insured"""
    policy = get_object_or_404(Policy, policy_id=policy_id)
    ai = get_object_or_404(AdditionalInsured, additional_insured_id=ai_id, policy=policy)
    
    # Check if certificate already exists
    existing_cert = ai.get_latest_certificate()
    if existing_cert:
        messages.info(request, f'Certificate already exists for {ai.name}')
        return redirect('applications:certificate_detail', 
                       certificate_id=existing_cert.certificate.certificate_id)
    
    # Redirect to certificate creation with pre-filled data
    # Store AI info in session for certificate creation
    request.session['ai_for_certificate'] = {
        'ai_id': ai.additional_insured_id,
        'holder_name': ai.name,
        'holder_address': ai.address_line_1,
        'holder_city': ai.city,
        'holder_state': ai.state,
        'holder_zip': ai.zip_code,
        'contact_name': ai.contact_name,
        'contact_email': ai.contact_email,
    }
    
    # Redirect to certificate creation
    # Assuming you have a certificate creation view
    return redirect('applications:certificate_create')


@login_required
def create_ai_schedule(request, policy_id):
    """Create a schedule of additional insureds"""
    policy = get_object_or_404(Policy, policy_id=policy_id)
    
    if request.method == 'POST':
        form = AdditionalInsuredScheduleForm(request.POST)
        if form.is_valid():
            schedule = form.save(commit=False)
            schedule.policy = policy
            schedule.created_by = request.user
            schedule.save()
            
            # Add AIs based on criteria
            schedule.add_ais_by_criteria()
            
            messages.success(
                request,
                f'Schedule "{schedule.schedule_name}" created with {schedule.total_ais} Additional Insureds!'
            )
            return redirect('applications:additional_insured_list', policy_id=policy_id)
    else:
        form = AdditionalInsuredScheduleForm()
    
    context = {
        'policy': policy,
        'form': form,
        'available_ais': policy.additional_insureds.filter(is_active=True),
    }
    
    return render(request, 'applications/ai_schedule_form.html', context)