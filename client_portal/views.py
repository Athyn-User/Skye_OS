# client_portal/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Sum, Count
from django.utils import timezone
from django.http import HttpResponse, JsonResponse, FileResponse
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
from decimal import Decimal

from .models import ClientProfile, ClientDocument, PaymentRequest, ClientActivity, ClientMessage
from .forms import (
    ClientLoginForm, ClientProfileForm, ClientClaimForm, 
    ClientMessageForm, PaymentForm
)
from .decorators import client_login_required
from applications.models import Company, Quote, Certificate
from claims.models import Claim, ClaimNote
import mimetypes


def track_activity(user, activity_type, description, request, **kwargs):
    """Helper function to track client portal activities"""
    ClientActivity.objects.create(
        user=user,
        activity_type=activity_type,
        description=description,
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        session_key=request.session.session_key or '',
        **kwargs
    )


def client_login_view(request):
    """Client portal login"""
    if request.user.is_authenticated:
        if hasattr(request.user, 'client_profile'):
            return redirect('client_portal:dashboard')
    
    if request.method == 'POST':
        form = ClientLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            
            user = authenticate(request, username=username, password=password)
            if user:
                # Check if user has client profile
                if hasattr(user, 'client_profile'):
                    if user.client_profile.portal_access_enabled:
                        login(request, user)
                        
                        # Update last login info
                        profile = user.client_profile
                        profile.last_login_date = timezone.now()
                        profile.last_login_ip = request.META.get('REMOTE_ADDR')
                        profile.save()
                        
                        # Track activity
                        track_activity(user, 'LOGIN', 'Client portal login', request)
                        
                        messages.success(request, f'Welcome back, {user.first_name}!')
                        return redirect('client_portal:dashboard')
                    else:
                        messages.error(request, 'Your portal access has been disabled. Please contact support.')
                else:
                    messages.error(request, 'You do not have client portal access.')
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = ClientLoginForm()
    
    return render(request, 'client_portal/login.html', {'form': form})


def client_logout_view(request):
    """Client portal logout"""
    if request.user.is_authenticated:
        track_activity(request.user, 'LOGOUT', 'Client portal logout', request)
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('client_portal:login')


@client_login_required
def dashboard_view(request):
    """Client portal dashboard"""
    print("Dashboard view reached!")  # Add this line
    profile = request.user.client_profile
    company = profile.company
    
    # Get statistics
    active_policies = Quote.objects.filter(
        application__company=company,
        quote_status='accepted',
        expiration_date__gte=timezone.now().date()
    ).count()
    
    active_certificates = Certificate.objects.filter(
        quote__application__company=company,
        certificate_status='issued',
        expiration_date__gte=timezone.now().date()
    ).count()
    
    open_claims = Claim.objects.filter(
        quote__application__company=company
    ).exclude(claim_status__in=['CLOSED', 'DENIED']).count()
    
    pending_payments = PaymentRequest.objects.filter(
        company=company,
        status='PENDING',
        show_in_portal=True
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
    
    # Recent items
    recent_documents = ClientDocument.objects.filter(
        company=company,
        is_visible=True
    ).order_by('-uploaded_date')[:5]
    
    recent_messages = ClientMessage.objects.filter(
        Q(company=company) & (Q(to_user=request.user) | Q(from_user=request.user))
    ).order_by('-sent_date')[:5]
    
    upcoming_payments = PaymentRequest.objects.filter(
        company=company,
        status='PENDING',
        show_in_portal=True
    ).order_by('due_date')[:5]
    
    context = {
        'profile': profile,
        'company': company,
        'active_policies': active_policies,
        'active_certificates': active_certificates,
        'open_claims': open_claims,
        'pending_payments': pending_payments,
        'recent_documents': recent_documents,
        'recent_messages': recent_messages,
        'upcoming_payments': upcoming_payments,
    }
    
    return render(request, 'client_portal/dashboard.html', context)


@client_login_required
def policies_view(request):
    """View policies/quotes"""
    profile = request.user.client_profile
    company = profile.company
    
    # Get all quotes for the company
    quotes = Quote.objects.filter(
        application__company=company
    ).select_related('application').order_by('-quote_date')
    
    # Filter by status if requested
    status = request.GET.get('status')
    if status:
        quotes = quotes.filter(quote_status=status)
    
    # Pagination
    paginator = Paginator(quotes, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'current_status': status,
    }
    
    track_activity(request.user, 'VIEW_POLICY', 'Viewed policies list', request)
    
    return render(request, 'client_portal/policies.html', context)


@client_login_required
def certificates_view(request):
    """View certificates"""
    profile = request.user.client_profile
    company = profile.company
    
    certificates = Certificate.objects.filter(
        quote__application__company=company
    ).select_related('quote__application').order_by('-issued_date')
    
    # Filter by status
    status = request.GET.get('status')
    if status:
        certificates = certificates.filter(certificate_status=status)
    
    # Pagination
    paginator = Paginator(certificates, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'current_status': status,
    }
    
    track_activity(request.user, 'VIEW_CERTIFICATE', 'Viewed certificates list', request)
    
    return render(request, 'client_portal/certificates.html', context)


@client_login_required
def claims_view(request):
    """View and track claims"""
    profile = request.user.client_profile
    company = profile.company
    
    claims = Claim.objects.filter(
        quote__application__company=company
    ).select_related('quote__application', 'adjuster').order_by('-reported_date')
    
    # Filter by status
    status = request.GET.get('status')
    if status:
        claims = claims.filter(claim_status=status)
    
    # Pagination
    paginator = Paginator(claims, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'current_status': status,
    }
    
    track_activity(request.user, 'VIEW_CLAIM', 'Viewed claims list', request)
    
    return render(request, 'client_portal/claims.html', context)


@client_login_required
def claim_detail_view(request, claim_id):
    """View claim details"""
    profile = request.user.client_profile
    company = profile.company
    
    claim = get_object_or_404(
        Claim,
        id=claim_id,
        quote__application__company=company
    )
    
    # Get public notes only
    notes = claim.notes.filter(is_public=True).order_by('-created_date')
    
    # Get related documents
    documents = ClientDocument.objects.filter(
        company=company,
        claim=claim,
        is_visible=True
    )
    
    context = {
        'claim': claim,
        'notes': notes,
        'documents': documents,
    }
    
    track_activity(
        request.user, 'VIEW_CLAIM', 
        f'Viewed claim {claim.claim_number}', 
        request, 
        claim=claim
    )
    
    return render(request, 'client_portal/claim_detail.html', context)


@client_login_required
def submit_claim_view(request):
    """Submit a new claim (FNOL)"""
    profile = request.user.client_profile
    company = profile.company
    
    if request.method == 'POST':
        form = ClientClaimForm(request.POST, request.FILES, company=company)
        if form.is_valid():
            claim = form.save(commit=False)
            claim.created_by = request.user
            claim.save()
            
            # Create a note about online submission
            ClaimNote.objects.create(
                claim=claim,
                note_type='GENERAL',
                subject='Claim Submitted Online',
                content=f'Claim submitted via client portal by {request.user.get_full_name()}',
                is_public=False,
                created_by=request.user
            )
            
            # Track activity
            track_activity(
                request.user, 'SUBMIT_CLAIM',
                f'Submitted claim for {claim.cause_of_loss}',
                request,
                claim=claim
            )
            
            messages.success(request, f'Your claim has been submitted successfully. Claim number: {claim.claim_number}')
            return redirect('client_portal:claim_detail', claim_id=claim.id)
    else:
        form = ClientClaimForm(company=company)
    
    return render(request, 'client_portal/submit_claim.html', {'form': form})


@client_login_required
def documents_view(request):
    """View and download documents - using PortalDocument for dual storage"""
    profile = request.user.client_profile
    company = profile.company
    
    # Get documents from PortalDocument (dual storage system)
    documents = PortalDocument.objects.visible_to_client(company).order_by('-uploaded_at')
    
    # Filter by type
    doc_type = request.GET.get('type')
    if doc_type:
        documents = documents.filter(document_type=doc_type)
    
    # Pagination
    paginator = Paginator(documents, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'current_type': doc_type,
        'document_types': PortalDocument.DOCUMENT_TYPES,
    }
    
    return render(request, 'client_portal/documents.html', context)


@client_login_required
def download_document_view(request, document_id):
    """Download a document"""
    profile = request.user.client_profile
    company = profile.company
    
    document = get_object_or_404(
        PortalDocument,
        document_id=document_id,
        company=company,
        client_visible=True
    )
    
    # Track activity
    track_activity(
        request.user, 'DOWNLOAD_DOCUMENT',
        f'Downloaded {document.document_name}',
        request
    )
    
    # Serve the file
    file_path = document.get_active_path()
    
    try:
        # Ensure the document name has the correct extension
        if '.' not in document.document_name:
            # Try to get extension from the file path
            import os
            _, ext = os.path.splitext(file_path)
            download_name = f"{document.document_name}{ext}"
        else:
            download_name = document.document_name
            
        mime_type, _ = mimetypes.guess_type(file_path)
        
        response = FileResponse(
            open(file_path, 'rb'),
            content_type=mime_type or 'application/octet-stream'
        )
        response['Content-Disposition'] = f'attachment; filename="{download_name}"'
        return response
    except FileNotFoundError:
        messages.error(request, 'File not found.')
        return redirect('client_portal:documents')


@client_login_required
def payments_view(request):
    """View and make payments"""
    profile = request.user.client_profile
    company = profile.company
    
    payments = PaymentRequest.objects.filter(
        company=company,
        show_in_portal=True
    ).order_by('due_date', '-created_date')
    
    # Filter by status
    status = request.GET.get('status', 'PENDING')
    if status:
        payments = payments.filter(status=status)
    
    # Calculate totals
    pending_total = payments.filter(status='PENDING').aggregate(
        total=Sum('amount')
    )['total'] or Decimal('0')
    
    # Pagination
    paginator = Paginator(payments, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'current_status': status,
        'pending_total': pending_total,
    }
    
    return render(request, 'client_portal/payments.html', context)


@client_login_required
@require_POST
def make_payment_view(request, payment_id):
    """Process a payment (mock implementation)"""
    profile = request.user.client_profile
    company = profile.company
    
    payment_request = get_object_or_404(
        PaymentRequest,
        id=payment_id,
        company=company,
        status='PENDING',
        allow_online_payment=True
    )
    
    # This is a mock payment processing
    # In production, integrate with payment gateway (Stripe, PayPal, etc.)
    
    payment_request.status = 'COMPLETED'
    payment_request.paid_date = timezone.now()
    payment_request.paid_amount = payment_request.amount
    payment_request.payment_method = 'Online Portal'
    payment_request.transaction_id = f'PORTAL-{timezone.now().timestamp()}'
    payment_request.save()
    
    # Track activity
    track_activity(
        request.user, 'MAKE_PAYMENT',
        f'Made payment of ${payment_request.amount}',
        request,
        quote=payment_request.quote
    )
    
    messages.success(request, f'Payment of ${payment_request.amount} processed successfully!')
    return redirect('client_portal:payments')


@client_login_required
def profile_view(request):
    """View and update profile"""
    profile = request.user.client_profile
    
    if request.method == 'POST':
        form = ClientProfileForm(request.POST, instance=profile, user=request.user)
        if form.is_valid():
            form.save()
            
            # Track activity
            track_activity(
                request.user, 'UPDATE_PROFILE',
                'Updated profile information',
                request
            )
            
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('client_portal:profile')
    else:
        form = ClientProfileForm(instance=profile, user=request.user)
    
    return render(request, 'client_portal/profile.html', {'form': form})

def test_view(request):
    from django.http import HttpResponse
    return HttpResponse("Client Portal is working!")
# Add these imports for dual storage
from documents.portal_models import PortalDocument
from documents.services import DualStorageService

@client_login_required
def upload_document_view(request):
    """Client uploads a document with dual storage"""
    profile = request.user.client_profile  # Note: might be clientprofile not client_profile
    company = profile.company
    
    if request.method == 'POST' and request.FILES.get('file'):
        uploaded_file = request.FILES['file']
        
        # Prepare document data
        document_data = {
            'document_name': request.POST.get('document_name', uploaded_file.name),
            'document_type': request.POST.get('document_type', 'general'),
            'description': request.POST.get('description', ''),
            'uploaded_by_id': request.user.id,
        }
        
        # Add optional relationships if provided
        if request.POST.get('application_id'):
            document_data['application_id'] = request.POST.get('application_id')
        if request.POST.get('quote_id'):
            document_data['quote_id'] = request.POST.get('quote_id')
        if request.POST.get('policy_id'):
            document_data['policy_id'] = request.POST.get('policy_id')
        
        # Save with dual storage
        try:
            document = DualStorageService.save_with_dual_storage(
                uploaded_file, 
                company.company_id, 
                document_data
            )
            
            # Track activity
            track_activity(
                request.user, 'UPLOAD_DOCUMENT',
                f'Uploaded document {document.document_name}',
                request
            )
            
            messages.success(request, f'Document "{document.document_name}" uploaded successfully!')
            return redirect('client_portal:documents')
        except Exception as e:
            messages.error(request, f'Error uploading document: {str(e)}')
    
    return render(request, 'client_portal/upload_document.html')


@client_login_required
def remove_document_view(request, document_id):
    """Client removes a document from their view (soft delete)"""
    profile = request.user.client_profile
    company = profile.company
    
    document = get_object_or_404(
        PortalDocument,
        document_id=document_id,
        company=company,
        client_visible=True
    )
    
    if request.method == 'POST':
        reason = request.POST.get('reason', 'Removed by client')
        document.remove_from_client_view(reason)
        
        # Track activity
        track_activity(
            request.user, 'REMOVE_DOCUMENT',
            f'Removed document {document.document_name}',
            request
        )
        
        messages.info(request, 'Document has been removed from your view.')
        return redirect('client_portal:documents')
    
    return render(request, 'client_portal/confirm_remove.html', {'document': document})


@client_login_required
def portal_documents_view(request):
    """View portal documents with dual storage (replacement for documents_view)"""
    profile = request.user.client_profile
    company = profile.company
    
    # Only show client-visible documents
    documents = PortalDocument.objects.visible_to_client(company).order_by('-uploaded_at')
    
    # Filter by type if requested
    doc_type = request.GET.get('type')
    if doc_type:
        documents = documents.filter(document_type=doc_type)
    
    # Pagination
    paginator = Paginator(documents, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'current_type': doc_type,
        'document_types': PortalDocument.DOCUMENT_TYPES,
    }
    
    return render(request, 'client_portal/documents.html', context)
