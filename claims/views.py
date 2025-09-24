# claims/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q, Sum, Count, Avg
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from decimal import Decimal

from .models import Claim, ClaimDocument, ClaimNote, ClaimPayment, ClaimReserve
from .forms import (
    ClaimFNOLForm, ClaimUpdateForm, ClaimNoteForm, 
    ClaimPaymentForm, ClaimDocumentForm, ClaimReserveForm
)
from applications.models import Quote, Certificate

@login_required
def claims_dashboard(request):
    """Main claims dashboard with statistics and recent activity"""
    
    # Overall statistics
    total_claims = Claim.objects.count()
    open_claims = Claim.objects.exclude(
        claim_status__in=['CLOSED', 'DENIED']
    ).count()
    
    # Financial statistics
    financial_stats = Claim.objects.aggregate(
        total_reserves=Sum('reserve_amount'),
        total_paid=Sum('paid_amount'),
        total_recovered=Sum('recovered_amount'),
        avg_claim_amount=Avg('paid_amount')
    )
    
    # Claims by status
    claims_by_status = Claim.objects.values('claim_status').annotate(
        count=Count('id')
    ).order_by('claim_status')
    
    # Claims by type
    claims_by_type = Claim.objects.values('claim_type').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Recent claims (last 10)
    recent_claims = Claim.objects.select_related(
        'quote__application__company', 'adjuster'
    ).order_by('-reported_date')[:10]
    
    # Claims needing attention (FNOL or high severity without adjuster)
    attention_claims = Claim.objects.filter(
        Q(claim_status='FNOL') | 
        Q(severity__in=['HIGH', 'CATASTROPHIC'], adjuster__isnull=True)
    ).select_related('quote__application__company')[:10]
    
    # Recent payments
    recent_payments = ClaimPayment.objects.select_related(
        'claim', 'created_by'
    ).order_by('-payment_date')[:10]
    
    context = {
        'total_claims': total_claims,
        'open_claims': open_claims,
        'financial_stats': financial_stats,
        'claims_by_status': claims_by_status,
        'claims_by_type': claims_by_type,
        'recent_claims': recent_claims,
        'attention_claims': attention_claims,
        'recent_payments': recent_payments,
    }
    
    return render(request, 'claims/dashboard.html', context)


@login_required
def claim_list(request):
    """List all claims with filtering and search"""
    
    claims = Claim.objects.select_related(
        'quote__application__company',
        'adjuster'
    ).prefetch_related('documents', 'payments')
    
    # Search functionality
    search = request.GET.get('search')
    if search:
        claims = claims.filter(
            Q(claim_number__icontains=search) |
            Q(claimant_name__icontains=search) |
            Q(quote__application__company__company_name__icontains=search) |
            Q(cause_of_loss__icontains=search)
        )
    
    # Filter by status
    status = request.GET.get('status')
    if status:
        claims = claims.filter(claim_status=status)
    
    # Filter by type
    claim_type = request.GET.get('type')
    if claim_type:
        claims = claims.filter(claim_type=claim_type)
    
    # Filter by adjuster
    adjuster_id = request.GET.get('adjuster')
    if adjuster_id:
        claims = claims.filter(adjuster_id=adjuster_id)
    
    # Filter by severity
    severity = request.GET.get('severity')
    if severity:
        claims = claims.filter(severity=severity)
    
    # Date range filter
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    if date_from:
        claims = claims.filter(date_of_loss__gte=date_from)
    if date_to:
        claims = claims.filter(date_of_loss__lte=date_to)
    
    # Pagination
    paginator = Paginator(claims, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search,
        'current_status': status,
        'current_type': claim_type,
        'current_severity': severity,
        'status_choices': Claim.CLAIM_STATUS,
        'type_choices': Claim.CLAIM_TYPE,
        'severity_choices': Claim.SEVERITY,
    }
    
    return render(request, 'claims/claim_list.html', context)


@login_required
def claim_detail(request, pk):
    """Detailed view of a single claim"""
    
    claim = get_object_or_404(
        Claim.objects.select_related(
            'quote__application__company',
            'quote__application__broker',
            'certificate',
            'adjuster',
            'created_by'
        ),
        pk=pk
    )
    
    # Get related data
    documents = claim.documents.select_related('uploaded_by').order_by('-uploaded_date')
    notes = claim.notes.select_related('created_by').order_by('-created_date')
    payments = claim.payments.select_related('created_by', 'approved_by').order_by('-payment_date')
    reserves = claim.reserves.select_related('created_by').order_by('-effective_date')
    
    # Calculate financial summary
    total_paid = payments.filter(payment_type__in=['INDEMNITY', 'MEDICAL', 'EXPENSE', 'LEGAL', 'DEDUCTIBLE']).aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
    total_recovered = payments.filter(payment_type='RECOVERY').aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
    
    context = {
        'claim': claim,
        'documents': documents,
        'notes': notes,
        'payments': payments,
        'reserves': reserves,
        'total_paid': total_paid,
        'total_recovered': total_recovered,
        'net_paid': total_paid - total_recovered,
    }
    
    return render(request, 'claims/claim_detail.html', context)


@login_required
def claim_fnol(request):
    """First Notice of Loss - Create new claim"""
    
    if request.method == 'POST':
        form = ClaimFNOLForm(request.POST)
        if form.is_valid():
            claim = form.save(commit=False)
            claim.created_by = request.user
            claim.save()
            
            # Create initial reserve if provided
            if form.cleaned_data.get('initial_reserve'):
                ClaimReserve.objects.create(
                    claim=claim,
                    reserve_type='INITIAL',
                    amount=form.cleaned_data['initial_reserve'],
                    reason='Initial reserve set at FNOL',
                    effective_date=timezone.now().date(),
                    created_by=request.user
                )
                claim.reserve_amount = form.cleaned_data['initial_reserve']
                claim.save()
            
            # Create initial note
            ClaimNote.objects.create(
                claim=claim,
                note_type='GENERAL',
                subject='First Notice of Loss',
                content=f"Claim reported by {request.user.get_full_name() or request.user.username}. "
                       f"Loss Description: {claim.loss_description}",
                created_by=request.user
            )
            
            messages.success(request, f'Claim {claim.claim_number} has been created successfully!')
            return redirect('claims:claim_detail', pk=claim.pk)
    else:
        # Pre-populate if quote_id is provided
        quote_id = request.GET.get('quote_id')
        initial = {}
        if quote_id:
            try:
                quote = Quote.objects.select_related('application__company').get(pk=quote_id)
                initial = {
                    'quote': quote,
                    'claimant_name': quote.application.company.company_name,
                    'claimant_email': quote.application.company.primary_contact_email,
                    'claimant_phone': quote.application.company.primary_contact_phone,
                }
            except Quote.DoesNotExist:
                pass
        
        form = ClaimFNOLForm(initial=initial)
    
    return render(request, 'claims/fnol_form.html', {'form': form})


@login_required
def claim_update(request, pk):
    """Update claim information"""
    
    claim = get_object_or_404(Claim, pk=pk)
    
    if request.method == 'POST':
        form = ClaimUpdateForm(request.POST, instance=claim)
        if form.is_valid():
            old_status = claim.claim_status
            claim = form.save()
            
            # Track status changes
            new_status = claim.claim_status
            if old_status != new_status:
                ClaimNote.objects.create(
                    claim=claim,
                    note_type='INTERNAL',
                    subject='Status Change',
                    content=f'Status changed from {old_status} to {new_status}',
                    created_by=request.user
                )
                
                # Update relevant dates based on status
                if new_status == 'APPROVED':
                    claim.approved_date = timezone.now()
                elif new_status == 'SETTLED':
                    claim.settled_date = timezone.now()
                elif new_status == 'CLOSED':
                    claim.closed_date = timezone.now()
                elif new_status == 'REOPENED':
                    claim.reopened_date = timezone.now()
                
                claim.save()
            
            messages.success(request, 'Claim updated successfully!')
            return redirect('claims:claim_detail', pk=claim.pk)
    else:
        form = ClaimUpdateForm(instance=claim)
    
    return render(request, 'claims/claim_form.html', {
        'form': form,
        'claim': claim,
        'is_update': True
    })


@login_required
def claim_assign_adjuster(request, pk):
    """Assign or reassign adjuster to claim"""
    
    claim = get_object_or_404(Claim, pk=pk)
    
    if request.method == 'POST':
        adjuster_id = request.POST.get('adjuster_id')
        if adjuster_id:
            from django.contrib.auth.models import User
            adjuster = get_object_or_404(User, pk=adjuster_id)
            
            old_adjuster = claim.adjuster
            claim.adjuster = adjuster
            claim.assigned_date = timezone.now()
            
            if claim.claim_status == 'FNOL':
                claim.claim_status = 'ASSIGNED'
            
            claim.save()
            
            # Create note about assignment
            note_content = f'Claim assigned to {adjuster.get_full_name() or adjuster.username}'
            if old_adjuster:
                note_content = f'Claim reassigned from {old_adjuster.get_full_name() or old_adjuster.username} to {adjuster.get_full_name() or adjuster.username}'
            
            ClaimNote.objects.create(
                claim=claim,
                note_type='INTERNAL',
                subject='Adjuster Assignment',
                content=note_content,
                created_by=request.user
            )
            
            messages.success(request, f'Claim assigned to {adjuster.get_full_name() or adjuster.username}')
        
        return redirect('claims:claim_detail', pk=claim.pk)
    
    # Get available adjusters (users with appropriate permissions)
    from django.contrib.auth.models import User
    adjusters = User.objects.filter(
        is_active=True,
        groups__name='Adjusters'  # Assuming you have an Adjusters group
    ).order_by('last_name', 'first_name')
    
    return render(request, 'claims/assign_adjuster.html', {
        'claim': claim,
        'adjusters': adjusters
    })


@login_required
def claim_add_note(request, pk):
    """Add a note to a claim"""
    
    claim = get_object_or_404(Claim, pk=pk)
    
    if request.method == 'POST':
        form = ClaimNoteForm(request.POST)
        if form.is_valid():
            note = form.save(commit=False)
            note.claim = claim
            note.created_by = request.user
            note.save()
            
            messages.success(request, 'Note added successfully!')
            return redirect('claims:claim_detail', pk=claim.pk)
    else:
        form = ClaimNoteForm()
    
    return render(request, 'claims/add_note.html', {
        'form': form,
        'claim': claim
    })


@login_required
def claim_add_payment(request, pk):
    """Add a payment to a claim"""
    
    claim = get_object_or_404(Claim, pk=pk)
    
    if request.method == 'POST':
        form = ClaimPaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.claim = claim
            payment.created_by = request.user
            payment.save()
            
            # Update claim's paid amount
            if payment.payment_type == 'RECOVERY':
                claim.recovered_amount += payment.amount
            else:
                claim.paid_amount += payment.amount
            claim.save()
            
            # Create note about payment
            ClaimNote.objects.create(
                claim=claim,
                note_type='SETTLEMENT',
                subject=f'Payment Processed - ${payment.amount}',
                content=f'{payment.payment_type} payment of ${payment.amount} to {payment.payee_name}',
                created_by=request.user
            )
            
            messages.success(request, 'Payment added successfully!')
            return redirect('claims:claim_detail', pk=claim.pk)
    else:
        form = ClaimPaymentForm()
    
    return render(request, 'claims/add_payment.html', {
        'form': form,
        'claim': claim
    })


@login_required
def claim_add_document(request, pk):
    """Upload a document to a claim"""
    
    claim = get_object_or_404(Claim, pk=pk)
    
    if request.method == 'POST':
        form = ClaimDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.claim = claim
            document.uploaded_by = request.user
            document.save()
            
            messages.success(request, 'Document uploaded successfully!')
            return redirect('claims:claim_detail', pk=claim.pk)
    else:
        form = ClaimDocumentForm()
    
    return render(request, 'claims/add_document.html', {
        'form': form,
        'claim': claim
    })


@login_required
def claim_adjust_reserve(request, pk):
    """Adjust claim reserve"""
    
    claim = get_object_or_404(Claim, pk=pk)
    
    if request.method == 'POST':
        form = ClaimReserveForm(request.POST)
        if form.is_valid():
            reserve = form.save(commit=False)
            reserve.claim = claim
            reserve.created_by = request.user
            reserve.save()
            
            # Update claim's reserve amount
            claim.reserve_amount = reserve.amount
            claim.save()
            
            # Create note about reserve adjustment
            ClaimNote.objects.create(
                claim=claim,
                note_type='INTERNAL',
                subject=f'Reserve Adjustment - ${reserve.amount}',
                content=f'{reserve.reserve_type}: {reserve.reason}',
                created_by=request.user
            )
            
            messages.success(request, 'Reserve adjusted successfully!')
            return redirect('claims:claim_detail', pk=claim.pk)
    else:
        form = ClaimReserveForm(initial={'effective_date': timezone.now().date()})
    
    return render(request, 'claims/adjust_reserve.html', {
        'form': form,
        'claim': claim,
        'current_reserve': claim.reserve_amount
    })


@login_required
def claim_approve(request, pk):
    """Approve a claim"""
    
    claim = get_object_or_404(Claim, pk=pk)
    
    if request.method == 'POST':
        claim.claim_status = 'APPROVED'
        claim.approved_date = timezone.now()
        claim.save()
        
        ClaimNote.objects.create(
            claim=claim,
            note_type='INTERNAL',
            subject='Claim Approved',
            content=f'Claim approved by {request.user.get_full_name() or request.user.username}',
            created_by=request.user
        )
        
        messages.success(request, f'Claim {claim.claim_number} has been approved!')
        return redirect('claims:claim_detail', pk=claim.pk)
    
    return render(request, 'claims/approve_claim.html', {'claim': claim})


@login_required
def claim_deny(request, pk):
    """Deny a claim"""
    
    claim = get_object_or_404(Claim, pk=pk)
    
    if request.method == 'POST':
        denial_reason = request.POST.get('denial_reason')
        
        claim.claim_status = 'DENIED'
        claim.denial_reason = denial_reason
        claim.closed_date = timezone.now()
        claim.save()
        
        ClaimNote.objects.create(
            claim=claim,
            note_type='INTERNAL',
            subject='Claim Denied',
            content=f'Claim denied by {request.user.get_full_name() or request.user.username}. Reason: {denial_reason}',
            created_by=request.user
        )
        
        messages.success(request, f'Claim {claim.claim_number} has been denied.')
        return redirect('claims:claim_detail', pk=claim.pk)
    
    return render(request, 'claims/deny_claim.html', {'claim': claim})


@login_required
def claim_close(request, pk):
    """Close a claim"""
    
    claim = get_object_or_404(Claim, pk=pk)
    
    if request.method == 'POST':
        claim.claim_status = 'CLOSED'
        claim.closed_date = timezone.now()
        claim.save()
        
        ClaimNote.objects.create(
            claim=claim,
            note_type='INTERNAL',
            subject='Claim Closed',
            content=f'Claim closed by {request.user.get_full_name() or request.user.username}',
            created_by=request.user
        )
        
        messages.success(request, f'Claim {claim.claim_number} has been closed.')
        return redirect('claims:claim_detail', pk=claim.pk)
    
    return render(request, 'claims/close_claim.html', {'claim': claim})


@login_required
def claim_reopen(request, pk):
    """Reopen a closed claim"""
    
    claim = get_object_or_404(Claim, pk=pk)
    
    if request.method == 'POST':
        reason = request.POST.get('reason')
        
        claim.claim_status = 'REOPENED'
        claim.reopened_date = timezone.now()
        claim.save()
        
        ClaimNote.objects.create(
            claim=claim,
            note_type='INTERNAL',
            subject='Claim Reopened',
            content=f'Claim reopened by {request.user.get_full_name() or request.user.username}. Reason: {reason}',
            created_by=request.user
        )
        
        messages.success(request, f'Claim {claim.claim_number} has been reopened.')
        return redirect('claims:claim_detail', pk=claim.pk)
    
    return render(request, 'claims/reopen_claim.html', {'claim': claim})