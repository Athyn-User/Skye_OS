# applications/policy_views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q, Count, Sum, F
from django.utils import timezone
from datetime import timedelta, date
from django.core.paginator import Paginator
from .models import Policy, PolicyRenewal, Quote, Application, Company, Certificate

def policy_list(request):
    """Display list of all policies with filtering options"""
    policies = Policy.objects.select_related(
        'quote__application__company',
        'quote__application__product',
        'quote__application__broker'
    ).all()
    
    # Filter by status
    status = request.GET.get('status')
    if status:
        policies = policies.filter(policy_status=status)
    
    # Search functionality
    search = request.GET.get('search')
    if search:
        policies = policies.filter(
            Q(policy_number__icontains=search) |
            Q(quote__application__company__company_name__icontains=search) |
            Q(quote__application__product__product_name__icontains=search)
        )
    
    # Filter by expiring soon (next 60 days)
    expiring_soon = request.GET.get('expiring')
    if expiring_soon:
        sixty_days = timezone.now().date() + timedelta(days=60)
        policies = policies.filter(
            expiration_date__lte=sixty_days,
            expiration_date__gte=timezone.now().date(),
            policy_status='active'
        )
    
    # Add status indicators
    for policy in policies:
        days_until_exp = (policy.expiration_date - timezone.now().date()).days
        if policy.policy_status == 'expired':
            policy.status_color = 'danger'
            policy.status_badge = 'Expired'
        elif policy.policy_status == 'cancelled':
            policy.status_color = 'secondary'
            policy.status_badge = 'Cancelled'
        elif days_until_exp < 0:
            policy.status_color = 'danger'
            policy.status_badge = 'Expired'
        elif days_until_exp <= 30:
            policy.status_color = 'warning'
            policy.status_badge = f'Expiring in {days_until_exp} days'
        else:
            policy.status_color = 'success'
            policy.status_badge = 'Active'
        policy.days_until_expiration = days_until_exp
    
    # Pagination
    paginator = Paginator(policies, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Statistics for the header
    total_policies = Policy.objects.count()
    active_policies = Policy.objects.filter(policy_status='active').count()
    expiring_count = Policy.objects.filter(
        expiration_date__lte=timezone.now().date() + timedelta(days=60),
        expiration_date__gte=timezone.now().date(),
        policy_status='active'
    ).count()
    
    context = {
        'policies': page_obj,
        'page_obj': page_obj,
        'current_status': status,
        'search_query': search,
        'total_policies': total_policies,
        'active_policies': active_policies,
        'expiring_count': expiring_count,
        'is_expiring_filter': expiring_soon,
    }
    return render(request, 'applications/policy_list.html', context)

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Policy

@login_required
def policy_detail(request, policy_id):
    """Display detailed policy information with sidebar navigation"""
    policy = get_object_or_404(Policy, policy_id=policy_id)
    
    # Calculate days until expiration
    from datetime import date
    today = date.today()
    days_until_expiration = (policy.expiration_date - today).days
    days_expired = abs(days_until_expiration) if days_until_expiration < 0 else 0
    
    # Check if renewal is needed
    needs_renewal = days_until_expiration <= 60 and policy.auto_renewal
    
    # Check if documents exist
    has_documents = hasattr(policy, 'documentpackage_set') and policy.documentpackage_set.exists()
    latest_package = None
    if has_documents:
        latest_package = policy.documentpackage_set.order_by('-generated_date').first()
    
    # Count related objects for sidebar badges (safe access)
    location_count = 0
    additional_insured_count = 0
    endorsement_count = 0
    certificate_count = 0
    
    # Try to get counts if the relationships exist
    try:
        if hasattr(policy, 'locations'):
            location_count = policy.locations.count()
    except:
        pass
        
    try:
        if hasattr(policy, 'additional_insureds'):
            additional_insured_count = policy.additional_insureds.count()
    except:
        pass
        
    try:
        if hasattr(policy, 'endorsements'):
            endorsement_count = policy.endorsements.count()
    except:
        pass
        
    try:
        # Certificates might be through quote
        if hasattr(policy.quote, 'certificate_set'):
            certificate_count = policy.quote.certificate_set.count()
    except:
        pass
    
    # Check for billing
    has_billing = hasattr(policy, 'billingschedule')
    pending_payments = 0
    if has_billing:
        try:
            from .models import PaymentRecord
            pending_payments = PaymentRecord.objects.filter(
                policy=policy,
                payment_status='pending'
            ).count()
        except:
            pass
    
    context = {
        'policy': policy,
        'object': policy,  # For sidebar compatibility
        'object_type': 'policy',  # For sidebar
        'active_tab': 'overview',  # Current page for sidebar
        'sidebar_title': 'Policy Navigation',
        'icon_type': 'file-contract',
        
        # Days calculation
        'days_until_expiration': days_until_expiration,
        'days_expired': days_expired,
        'needs_renewal': needs_renewal,
        
        # Document status
        'has_documents': has_documents,
        'latest_package': latest_package,
        
        # Billing status
        'has_billing': has_billing,
        
        # Sidebar badge counts
        'location_count': location_count,
        'additional_insured_count': additional_insured_count,
        'endorsement_count': endorsement_count,
        'certificate_count': certificate_count,
        'pending_payments': pending_payments,
    }
    
    return render(request, 'applications/policy_detail.html', context)

def policy_from_quote(request, quote_id):
    """Convert an accepted quote to a policy"""
    quote = get_object_or_404(Quote, quote_id=quote_id)
    
    # Check if quote is accepted
    if quote.quote_status != 'accepted':
        messages.error(request, 'Only accepted quotes can be converted to policies.')
        return redirect('applications:quote_detail', pk=quote_id)
    
    # Check if policy already exists for this quote
    existing_policy = Policy.objects.filter(quote=quote).first()
    if existing_policy:
        messages.info(request, 'A policy already exists for this quote.')
        return redirect('applications:policy_detail', policy_id=existing_policy.policy_id)
    
    if request.method == 'POST':
        try:
            # Generate policy number based on quote but WITHOUT version number
            product_code = quote.application.product.document_code or 'GEN'
            policy_number = f'POL-{product_code}-{quote.base_number}-{quote.sequence_number:02d}'
            # Note: We do NOT add version number for new policies
            
            # Create the policy
            policy = Policy.objects.create(
                quote=quote,
                policy_number=policy_number,
                base_number=quote.base_number,  # Inherit from quote
                sequence_number=quote.sequence_number,  # Inherit from quote
                version_number=None,  # NEW POLICY - no version number
                effective_date=quote.effective_date,
                expiration_date=quote.expiration_date,
                annual_premium=quote.total_premium,
                billing_frequency=request.POST.get('billing_frequency', 'annual'),
                policy_status='active',
                auto_renewal=request.POST.get('auto_renewal') == 'on',  # Handle checkbox
                created_by=request.user if request.user.is_authenticated else None
            )
            
            # Update application status
            quote.application.application_status = 'bound'
            quote.application.bound_premium = quote.total_premium
            quote.application.save()
            
            messages.success(request, f'Policy {policy.policy_number} created successfully!')
            return redirect('applications:policy_detail', policy_id=policy.policy_id)
            
        except Exception as e:
            messages.error(request, f'Error creating policy: {str(e)}')
            # Fall through to show the form again
    
    # For GET request or if there was an error, show the conversion form
    # Show the proposed policy number WITHOUT version
    proposed_number = f"POL-{quote.application.product.document_code or 'GEN'}-{quote.base_number}-{quote.sequence_number:02d}"
    
    context = {
        'quote': quote,
        'proposed_policy_number': proposed_number,
    }
    return render(request, 'applications/policy_from_quote.html', context)

def policy_renew(request, policy_id):
    """Initiate policy renewal process"""
    policy = get_object_or_404(Policy, policy_id=policy_id)
    
    if request.method == 'POST':
        try:
            # Create a new quote for renewal
            renewal_quote = Quote.objects.create(
                application=policy.quote.application,
                quote_number=f"QTE-REN-{policy.policy_number[4:]}",
                quote_version=1,
                effective_date=policy.expiration_date + timedelta(days=1),
                expiration_date=policy.expiration_date + timedelta(days=365),
                quote_status='draft',
                total_premium=policy.annual_premium * 1.05,  # 5% increase as default
                commission_amount=policy.quote.commission_amount,
                special_conditions=f"Renewal of Policy {policy.policy_number}"
            )
            
            messages.success(request, f'Renewal quote {renewal_quote.quote_number} created!')
            return redirect('applications:quote_detail', pk=renewal_quote.quote_id)
            
        except Exception as e:
            messages.error(request, f'Error creating renewal: {str(e)}')
    
    context = {
        'policy': policy,
    }
    return render(request, 'applications/policy_renew.html', context)

def renewal_dashboard(request):
    """Main renewal dashboard with overview and statistics"""
    today = timezone.now().date()
    
    # Get policies expiring in next 90 days that haven't been renewed yet
    ninety_days_from_now = today + timedelta(days=90)
    
    upcoming_renewals = Policy.objects.filter(
        expiration_date__lte=ninety_days_from_now,
        expiration_date__gte=today,
        policy_status='active',
        auto_renewal=True  # Only show policies marked for renewal
    ).select_related(
        'quote__application__company',
        'quote__application__product',
        'quote__application__broker'
    ).exclude(
        # Exclude policies that already have a renewal in progress
        renewals__renewal_status__in=['quoted', 'accepted']
    ).order_by('expiration_date')
    
    # Add days until expiration for each policy
    for policy in upcoming_renewals:
        policy.days_until_expiration = (policy.expiration_date - today).days
        policy.urgency_class = ''
        if policy.days_until_expiration <= 0:
            policy.urgency_class = 'table-danger'
        elif policy.days_until_expiration <= 15:
            policy.urgency_class = 'table-warning'
        elif policy.days_until_expiration <= 30:
            policy.urgency_class = 'table-info'
    
    # Get overdue renewals (policies that expired without renewal)
    overdue_renewals = Policy.objects.filter(
        expiration_date__lt=today,
        policy_status='active',
        auto_renewal=True
    ).select_related(
        'quote__application__company'
    ).exclude(
        renewals__renewal_status='accepted'
    ).order_by('-expiration_date')
    
    # Get recent renewal activity (last 30 days)
    thirty_days_ago = today - timedelta(days=30)
    recent_renewals = PolicyRenewal.objects.filter(
        created_at__gte=thirty_days_ago
    ).select_related(
        'original_policy__quote__application__company',
        'renewal_quote',
        'renewal_policy'
    ).order_by('-created_at')[:10]
    
    # Statistics for the dashboard
    total_upcoming = upcoming_renewals.count()
    total_overdue = overdue_renewals.count()
    
    # Policies needing immediate attention (expiring in 15 days)
    urgent_count = Policy.objects.filter(
        expiration_date__lte=today + timedelta(days=15),
        expiration_date__gte=today,
        policy_status='active'
    ).count()
    
    # Calculate potential renewal revenue
    potential_revenue = upcoming_renewals.aggregate(
        total=Sum('annual_premium')
    )['total'] or 0
    
    # Get renewal statistics by status
    renewal_stats = PolicyRenewal.objects.filter(
        created_at__gte=thirty_days_ago
    ).values('renewal_status').annotate(
        count=Count('renewal_id')
    )
    
    # Process into a dictionary for easy template access
    stats_dict = {
        'pending': 0,
        'quoted': 0,
        'accepted': 0,
        'declined': 0,
        'non_renewed': 0
    }
    for stat in renewal_stats:
        stats_dict[stat['renewal_status']] = stat['count']
    
    # Get policies by time until renewal
    expires_7_days = Policy.objects.filter(
        expiration_date__lte=today + timedelta(days=7),
        expiration_date__gte=today,
        policy_status='active'
    ).count()
    
    expires_30_days = Policy.objects.filter(
        expiration_date__lte=today + timedelta(days=30),
        expiration_date__gt=today + timedelta(days=7),
        policy_status='active'
    ).count()
    
    expires_60_days = Policy.objects.filter(
        expiration_date__lte=today + timedelta(days=60),
        expiration_date__gt=today + timedelta(days=30),
        policy_status='active'
    ).count()
    
    expires_90_days = Policy.objects.filter(
        expiration_date__lte=today + timedelta(days=90),
        expiration_date__gt=today + timedelta(days=60),
        policy_status='active'
    ).count()
    
    context = {
        'upcoming_renewals': upcoming_renewals,
        'overdue_renewals': overdue_renewals,
        'recent_renewals': recent_renewals,
        'total_upcoming': total_upcoming,
        'total_overdue': total_overdue,
        'urgent_count': urgent_count,
        'potential_revenue': potential_revenue,
        'renewal_stats': stats_dict,
        'expires_7_days': expires_7_days,
        'expires_30_days': expires_30_days,
        'expires_60_days': expires_60_days,
        'expires_90_days': expires_90_days,
        'today': today,
    }
    
    return render(request, 'applications/renewal_dashboard.html', context)

def renewal_process(request, policy_id):
    """Process a policy renewal - create or update renewal record"""
    policy = get_object_or_404(Policy, policy_id=policy_id)
    
    # Check if renewal already exists
    existing_renewal = PolicyRenewal.objects.filter(
        original_policy=policy,
        renewal_status__in=['pending', 'quoted']
    ).first()
    
    if existing_renewal:
        # Redirect to edit existing renewal
        return redirect('applications:renewal_detail', renewal_id=existing_renewal.renewal_id)
    
    if request.method == 'POST':
        try:
            # Get form data
            proposed_premium = request.POST.get('proposed_premium')
            premium_change_notes = request.POST.get('premium_change_notes', '')
            renewal_notes = request.POST.get('renewal_notes', '')
            
            # Calculate premium change percentage
            original_premium = float(policy.annual_premium)
            new_premium = float(proposed_premium)
            premium_change_percent = ((new_premium - original_premium) / original_premium) * 100
            
            # Create renewal quote
            renewal_quote = Quote.objects.create(
                application=policy.quote.application,
                quote_number=f"REN-{policy.policy_number}-{timezone.now().strftime('%Y%m%d')}",
                quote_version=1,
                effective_date=policy.expiration_date + timedelta(days=1),
                expiration_date=policy.expiration_date + timedelta(days=365),
                quote_status='draft',
                total_premium=new_premium,
                commission_amount=policy.quote.commission_amount,
                special_conditions=f"Renewal of Policy {policy.policy_number}\n{premium_change_notes}"
            )
            
            # Create renewal record
            renewal = PolicyRenewal.objects.create(
                original_policy=policy,
                renewal_quote=renewal_quote,
                renewal_status='quoted',
                renewal_date=policy.expiration_date,
                notice_sent_date=timezone.now().date(),
                response_due_date=policy.expiration_date - timedelta(days=15),
                proposed_premium=new_premium,
                premium_change_percent=premium_change_percent,
                notes=renewal_notes
            )
            
            messages.success(request, f'Renewal quote created for policy {policy.policy_number}')
            return redirect('applications:renewal_detail', renewal_id=renewal.renewal_id)
            
        except Exception as e:
            messages.error(request, f'Error creating renewal: {str(e)}')
    
    # Calculate suggested premium (you can adjust this logic)
    suggested_premium = policy.annual_premium  # Start with same premium
    
    context = {
        'policy': policy,
        'suggested_premium': suggested_premium,
        'expiration_date': policy.expiration_date,
        'new_effective_date': policy.expiration_date + timedelta(days=1),
        'new_expiration_date': policy.expiration_date + timedelta(days=365),
    }
    
    return render(request, 'applications/renewal_process.html', context)

def renewal_detail(request, renewal_id):
    """View and manage a specific renewal"""
    renewal = get_object_or_404(PolicyRenewal, renewal_id=renewal_id)
    
    # Calculate days until renewal
    today = timezone.now().date()
    days_until_renewal = (renewal.original_policy.expiration_date - today).days
    days_expired = abs(days_until_renewal) if days_until_renewal < 0 else 0
    
    context = {
        'renewal': renewal,
        'policy': renewal.original_policy,
        'renewal_quote': renewal.renewal_quote,
        'days_until_renewal': days_until_renewal,
        'days_expired': days_expired,
        'can_accept': renewal.renewal_status == 'quoted' and days_until_renewal >= -30,  # Allow 30 days grace period
    }
    
    return render(request, 'applications/renewal_detail.html', context)

def renewal_accept(request, renewal_id):
    """Accept a renewal and create new policy"""
    renewal = get_object_or_404(PolicyRenewal, renewal_id=renewal_id)
    
    if renewal.renewal_status != 'quoted':
        messages.error(request, 'This renewal cannot be accepted in its current state.')
        return redirect('applications:renewal_detail', renewal_id=renewal_id)
    
    if request.method == 'POST':
        try:
            # Update renewal quote status
            renewal.renewal_quote.quote_status = 'accepted'
            renewal.renewal_quote.save()
            
            # Generate new policy number with incremented sequence
            product_code = renewal.original_policy.quote.application.product.document_code or 'GEN'
            base_number = renewal.original_policy.base_number
            new_sequence = renewal.original_policy.sequence_number + 1
            
            # Renewal policy number: increment sequence, NO version number
            new_policy_number = f"POL-{product_code}-{base_number}-{new_sequence:02d}"
            
            # Create new policy
            new_policy = Policy.objects.create(
                policy_number=new_policy_number,
                quote=renewal.renewal_quote,
                base_number=base_number,  # Keep same base
                sequence_number=new_sequence,  # Increment sequence for renewal
                version_number=None,  # No version for new renewal
                parent_policy=renewal.original_policy,  # Link to previous policy
                original_policy=renewal.original_policy.original_policy or renewal.original_policy,  # Track the first in chain
                effective_date=renewal.renewal_quote.effective_date,
                expiration_date=renewal.renewal_quote.expiration_date,
                annual_premium=renewal.proposed_premium,
                billing_frequency=renewal.original_policy.billing_frequency,
                policy_status='active',
                auto_renewal=renewal.original_policy.auto_renewal,
                created_by=request.user if request.user.is_authenticated else None
            )
            
            # Update renewal record
            renewal.renewal_policy = new_policy
            renewal.renewal_status = 'accepted'
            renewal.save()
            
            # Update original policy status
            renewal.original_policy.policy_status = 'expired'
            renewal.original_policy.save()
            
            # Create transaction record
            from applications.models import PolicyTransaction
            PolicyTransaction.objects.create(
                policy=new_policy,
                transaction_type='renewal',
                effective_date=new_policy.effective_date,
                premium_change=renewal.proposed_premium - renewal.original_policy.annual_premium,
                description=f'Renewal of policy {renewal.original_policy.policy_number}',
                processed_by=request.user if request.user.is_authenticated else None
            )
            
            messages.success(request, f'Renewal accepted. New policy {new_policy.policy_number} created.')
            return redirect('applications:policy_detail', policy_id=new_policy.policy_id)
            
        except Exception as e:
            messages.error(request, f'Error accepting renewal: {str(e)}')
    
    context = {
        'renewal': renewal,
        'policy': renewal.original_policy,
        'new_policy_number': f"POL-{renewal.original_policy.quote.application.product.document_code or 'GEN'}-{renewal.original_policy.base_number}-{(renewal.original_policy.sequence_number + 1):02d}",  # Show preview
    }
    
    return render(request, 'applications/renewal_accept.html', context)