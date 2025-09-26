# File: applications/location_views.py
# Views for location management - designed for dozens of locations

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q, Sum, Count
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.forms import modelformset_factory
from datetime import date
import json

from .models import Policy, Quote
from .location_models import PolicyLocation, LocationSchedule, LocationScheduleItem, LocationEndorsement
from .location_forms import PolicyLocationForm, LocationScheduleForm, BulkLocationForm


@login_required
def policy_locations(request, policy_id):
    """Main location management page for a policy"""
    policy = get_object_or_404(Policy, policy_id=policy_id)
    
    # Get search and filter parameters
    search = request.GET.get('search', '')
    state_filter = request.GET.get('state', '')
    occupancy_filter = request.GET.get('occupancy', '')
    active_only = request.GET.get('active_only', 'true') == 'true'
    
    # Build location query
    locations = policy.locations.all()
    
    if active_only:
        locations = locations.filter(is_active=True)
    
    if search:
        locations = locations.filter(
            Q(location_name__icontains=search) |
            Q(street_address__icontains=search) |
            Q(city__icontains=search) |
            Q(location_number__icontains=search)
        )
    
    if state_filter:
        locations = locations.filter(state=state_filter)
    
    if occupancy_filter:
        locations = locations.filter(primary_occupancy=occupancy_filter)
    
    # Pagination for large numbers of locations
    paginator = Paginator(locations.order_by('location_number'), 20)  # 20 locations per page
    page_number = request.GET.get('page')
    page_locations = paginator.get_page(page_number)
    
    # Summary statistics
    total_locations = policy.locations.filter(is_active=True).count()
    total_building_limit = policy.locations.filter(is_active=True).aggregate(
        total=Sum('building_limit')
    )['total'] or 0
    total_contents_limit = policy.locations.filter(is_active=True).aggregate(
        total=Sum('contents_limit')
    )['total'] or 0
    
    # Get unique values for filters
    states = policy.locations.values_list('state', flat=True).distinct().order_by('state')
    occupancies = policy.locations.exclude(primary_occupancy='').values_list(
        'primary_occupancy', flat=True
    ).distinct().order_by('primary_occupancy')
    
    # Get existing schedules
    schedules = LocationSchedule.objects.filter(policy=policy).order_by('schedule_name')
    
    context = {
        'policy': policy,
        'locations': page_locations,
        'total_locations': total_locations,
        'total_building_limit': total_building_limit,
        'total_contents_limit': total_contents_limit,
        'states': states,
        'occupancies': occupancies,
        'schedules': schedules,
        'search': search,
        'state_filter': state_filter,
        'occupancy_filter': occupancy_filter,
        'active_only': active_only,
    }
    
    return render(request, 'applications/policy_locations.html', context)


@login_required
def add_location(request, policy_id):
    """Add a single location to a policy"""
    policy = get_object_or_404(Policy, policy_id=policy_id)
    
    if request.method == 'POST':
        form = PolicyLocationForm(request.POST)
        if form.is_valid():
            location = form.save(commit=False)
            location.policy = policy
            
            # Auto-generate location number if not provided
            if not location.location_number:
                max_location = policy.locations.aggregate(
                    max_num=models.Max('location_number')
                )['max_num']
                try:
                    next_num = int(max_location) + 1 if max_location else 1
                    location.location_number = f"{next_num:03d}"
                except (ValueError, TypeError):
                    location.location_number = f"{policy.locations.count() + 1:03d}"
            
            location.created_by = request.user
            location.save()
            
            messages.success(request, f'Location {location.location_number} added successfully!')
            return redirect('applications:policy_locations', policy_id=policy_id)
    else:
        form = PolicyLocationForm(initial={
            'effective_date': policy.effective_date,
            'building_limit': 0,
            'contents_limit': 0,
        })
    
    context = {
        'policy': policy,
        'form': form,
        'action': 'Add',
    }
    
    return render(request, 'applications/location_form.html', context)


@login_required
def edit_location(request, policy_id, location_id):
    """Edit an existing location"""
    policy = get_object_or_404(Policy, policy_id=policy_id)
    location = get_object_or_404(PolicyLocation, location_id=location_id, policy=policy)
    
    if request.method == 'POST':
        form = PolicyLocationForm(request.POST, instance=location)
        if form.is_valid():
            form.save()
            messages.success(request, f'Location {location.location_number} updated successfully!')
            return redirect('applications:policy_locations', policy_id=policy_id)
    else:
        form = PolicyLocationForm(instance=location)
    
    context = {
        'policy': policy,
        'location': location,
        'form': form,
        'action': 'Edit',
    }
    
    return render(request, 'applications/location_form.html', context)


@login_required
def bulk_add_locations(request, policy_id):
    """Bulk add multiple locations at once"""
    policy = get_object_or_404(Policy, policy_id=policy_id)
    
    # Create formset for multiple locations
    LocationFormSet = modelformset_factory(
        PolicyLocation, 
        form=BulkLocationForm, 
        extra=5,  # Start with 5 empty forms
        can_delete=True
    )
    
    if request.method == 'POST':
        formset = LocationFormSet(request.POST)
        if formset.is_valid():
            locations_added = 0
            
            for form in formset:
                if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                    location = form.save(commit=False)
                    location.policy = policy
                    location.created_by = request.user
                    location.effective_date = location.effective_date or policy.effective_date
                    
                    # Auto-generate location number if not provided
                    if not location.location_number:
                        max_location = policy.locations.aggregate(
                            max_num=models.Max('location_number')
                        )['max_num']
                        try:
                            next_num = int(max_location) + locations_added + 1 if max_location else locations_added + 1
                            location.location_number = f"{next_num:03d}"
                        except (ValueError, TypeError):
                            location.location_number = f"{policy.locations.count() + locations_added + 1:03d}"
                    
                    location.save()
                    locations_added += 1
            
            if locations_added > 0:
                messages.success(request, f'{locations_added} locations added successfully!')
                return redirect('applications:policy_locations', policy_id=policy_id)
            else:
                messages.warning(request, 'No locations were added.')
    else:
        formset = LocationFormSet(queryset=PolicyLocation.objects.none())
    
    context = {
        'policy': policy,
        'formset': formset,
    }
    
    return render(request, 'applications/bulk_location_form.html', context)


@login_required
def location_schedule_list(request, policy_id):
    """List all location schedules for a policy"""
    policy = get_object_or_404(Policy, policy_id=policy_id)
    schedules = LocationSchedule.objects.filter(policy=policy).order_by('schedule_name')
    
    context = {
        'policy': policy,
        'schedules': schedules,
    }
    
    return render(request, 'applications/location_schedules.html', context)


@login_required
def create_location_schedule(request, policy_id):
    """Create a new location schedule"""
    policy = get_object_or_404(Policy, policy_id=policy_id)
    
    if request.method == 'POST':
        form = LocationScheduleForm(request.POST)
        if form.is_valid():
            schedule = form.save(commit=False)
            schedule.policy = policy
            schedule.created_by = request.user
            schedule.save()
            
            # Add locations based on criteria
            schedule.add_locations_by_criteria()
            
            messages.success(request, f'Schedule "{schedule.schedule_name}" created with {schedule.total_locations} locations!')
            return redirect('applications:edit_location_schedule', policy_id=policy_id, schedule_id=schedule.schedule_id)
    else:
        form = LocationScheduleForm()
    
    context = {
        'policy': policy,
        'form': form,
        'available_locations': policy.locations.filter(is_active=True).order_by('location_number'),
    }
    
    return render(request, 'applications/location_schedule_form.html', context)


@login_required
def edit_location_schedule(request, policy_id, schedule_id):
    """Edit location schedule and manage included locations"""
    policy = get_object_or_404(Policy, policy_id=policy_id)
    schedule = get_object_or_404(LocationSchedule, schedule_id=schedule_id, policy=policy)
    
    if request.method == 'POST':
        form = LocationScheduleForm(request.POST, instance=schedule)
        if form.is_valid():
            form.save()
            
            # Handle manual location selection
            if 'selected_locations' in request.POST:
                selected_location_ids = request.POST.getlist('selected_locations')
                
                # Clear existing items
                schedule.items.all().delete()
                
                # Add selected locations
                for i, location_id in enumerate(selected_location_ids, 1):
                    try:
                        location = PolicyLocation.objects.get(
                            location_id=location_id, 
                            policy=policy
                        )
                        LocationScheduleItem.objects.create(
                            schedule=schedule,
                            location=location,
                            sequence_order=i
                        )
                    except PolicyLocation.DoesNotExist:
                        continue
                
                schedule.calculate_totals()
            
            messages.success(request, f'Schedule "{schedule.schedule_name}" updated!')
            return redirect('applications:location_schedule_list', policy_id=policy_id)
    else:
        form = LocationScheduleForm(instance=schedule)
    
    # Get current schedule items
    schedule_items = schedule.items.select_related('location').order_by('sequence_order')
    
    # Get available locations not in schedule
    included_location_ids = [item.location.location_id for item in schedule_items]
    available_locations = policy.locations.filter(is_active=True).exclude(
        location_id__in=included_location_ids
    ).order_by('location_number')
    
    context = {
        'policy': policy,
        'schedule': schedule,
        'form': form,
        'schedule_items': schedule_items,
        'available_locations': available_locations,
    }
    
    return render(request, 'applications/edit_location_schedule.html', context)


@login_required
@require_http_methods(["POST"])
def delete_location(request, policy_id, location_id):
    """Soft delete a location (mark as inactive)"""
    policy = get_object_or_404(Policy, policy_id=policy_id)
    location = get_object_or_404(PolicyLocation, location_id=location_id, policy=policy)
    
    # Soft delete - just mark as inactive
    location.is_active = False
    location.termination_date = date.today()
    location.save()
    
    messages.success(request, f'Location {location.location_number} has been deactivated.')
    return redirect('applications:policy_locations', policy_id=policy_id)


@login_required
@require_http_methods(["GET"])
def location_api(request, policy_id):
    """API endpoint for location data (for AJAX functionality)"""
    policy = get_object_or_404(Policy, policy_id=policy_id)
    
    action = request.GET.get('action')
    
    if action == 'search':
        query = request.GET.get('q', '')
        locations = policy.locations.filter(
            Q(location_name__icontains=query) |
            Q(street_address__icontains=query) |
            Q(city__icontains=query) |
            Q(location_number__icontains=query),
            is_active=True
        )[:10]  # Limit for performance
        
        results = []
        for location in locations:
            results.append({
                'id': location.location_id,
                'text': f"{location.location_number} - {location.street_address}, {location.city}, {location.state}",
                'building_limit': str(location.building_limit),
                'contents_limit': str(location.contents_limit),
            })
        
        return JsonResponse({'results': results})
    
    elif action == 'totals':
        # Return summary totals
        totals = policy.locations.filter(is_active=True).aggregate(
            total_locations=Count('location_id'),
            total_building=Sum('building_limit'),
            total_contents=Sum('contents_limit'),
        )
        return JsonResponse(totals)
    
    return JsonResponse({'error': 'Invalid action'}, status=400)


@login_required
def generate_locations_schedule_endorsement(request, policy_id, schedule_id):
    """Generate a Locations Schedule endorsement from a schedule"""
    policy = get_object_or_404(Policy, policy_id=policy_id)
    schedule = get_object_or_404(LocationSchedule, schedule_id=schedule_id, policy=policy)
    
    try:
        from .document_models import DocumentTemplate, EndorsementDocument
        from .endorsement_generator import EndorsementGenerator
        
        # Find the Locations Schedule template
        template = DocumentTemplate.objects.filter(
            template_type='endorsement',
            template_name__icontains='locations schedule',
            product=policy.quote.application.product,
            is_active=True
        ).first()
        
        if not template:
            messages.error(request, 'Locations Schedule endorsement template not found.')
            return redirect('applications:location_schedule_list', policy_id=policy_id)
        
        # Prepare endorsement data with schedule information
        endorsement_data = {
            'schedule_id': schedule.schedule_id,
            'schedule_name': schedule.schedule_name,
            'total_locations': schedule.total_locations,
            'total_building_limit': str(schedule.total_building_limit),
            'total_contents_limit': str(schedule.total_contents_limit),
            'description': f'Schedule of {schedule.total_locations} locations',
        }
        
        # Generate the endorsement
        generator = EndorsementGenerator()
        endorsement = generator.create_endorsement(
            policy=policy,
            template_code=template.template_code,
            endorsement_data=endorsement_data,
            effective_date=date.today()
        )
        
        # Link the schedule to the endorsement
        LocationEndorsement.objects.create(
            policy=policy,
            endorsement_document=endorsement,
            schedule=schedule,
            endorsement_number=endorsement.endorsement_number,
            effective_date=endorsement.effective_date,
            action_type='add_locations',
            description=f'Locations Schedule: {schedule.schedule_name}',
            created_by=request.user
        )
        
        messages.success(request, f'Locations Schedule endorsement {endorsement.endorsement_number} created successfully!')
        return redirect('applications:view_endorsements', policy_id=policy_id)
        
    except Exception as e:
        messages.error(request, f'Error creating endorsement: {str(e)}')
        return redirect('applications:location_schedule_list', policy_id=policy_id)



@login_required
def quote_locations(request, quote_id):
    """Manage locations for a quote"""
    quote = get_object_or_404(Quote, quote_id=quote_id)
    
    context = {
        'object': quote,
        'object_type': 'quote',
        'page_title': 'Company Locations',
        'active_tab': 'locations',
        'icon': 'fa-map-marker-alt',
        'description': 'Manage locations for this quote.',
        'features': [
            'Add multiple quote locations',
            'Calculate location-based pricing',
            'Preview location schedules',
            'Import location data'
        ]
    }
    return render(request, 'applications/placeholder_page.html', context)

@login_required
def add_quote_location(request, quote_id):
    """Add a location to a quote"""
    # Implement actual functionality
    pass