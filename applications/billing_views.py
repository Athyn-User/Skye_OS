from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db import models
from django.db.models import Sum, Q, Count
from .models import Policy, PaymentRecord, BillingSchedule, Commission, FinancialSummary
from datetime import date, timedelta
from decimal import Decimal
import calendar

def billing_dashboard(request):
    '''Main billing and financial dashboard'''
    today = date.today()
    
    # Payment metrics
    overdue_payments = PaymentRecord.objects.filter(
        payment_status='pending',
        due_date__lt=today
    ).aggregate(
        count=Count('payment_id'),
        amount=Sum('amount_due')
    )
    
    upcoming_payments = PaymentRecord.objects.filter(
        payment_status='pending',
        due_date__gte=today,
        due_date__lte=today + timedelta(days=30)
    ).aggregate(
        count=models.Count('payment_id'),
        amount=models.Sum('amount_due')
    )
    
    # Revenue metrics for current month
    current_month_start = today.replace(day=1)
    monthly_revenue = PaymentRecord.objects.filter(
        payment_status='paid',
        payment_date__gte=current_month_start
    ).aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0
    
    # Recent payment activity
    recent_payments = PaymentRecord.objects.select_related(
        'policy__quote__application__company'
    ).filter(
        payment_status='paid'
    ).order_by('-payment_date')[:10]
    
    context = {
        'overdue_payments': overdue_payments,
        'upcoming_payments': upcoming_payments,
        'monthly_revenue': monthly_revenue,
        'recent_payments': recent_payments,
        'title': 'Billing Dashboard'
    }
    return render(request, 'billing/billing_dashboard.html', context)

def payment_list(request):
    '''List all payment records with filtering'''
    payments = PaymentRecord.objects.select_related(
        'policy__quote__application__company'
    ).all()
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        payments = payments.filter(payment_status=status_filter)
    
    # Filter by overdue
    if request.GET.get('overdue'):
        payments = payments.filter(
            payment_status='pending',
            due_date__lt=date.today()
        )
    
    # Pagination
    paginator = Paginator(payments, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'payments': page_obj,
        'status_filter': status_filter,
        'title': 'Payment Management'
    }
    return render(request, 'billing/payment_list.html', context)

def create_billing_schedule(request, policy_id):
    '''Create installment payment schedule for a policy'''
    policy = get_object_or_404(Policy, policy_id=policy_id)
    
    if hasattr(policy, 'billingschedule'):
        messages.warning(request, 'Billing schedule already exists for this policy')
        return redirect('applications:policy_detail', policy_id=policy_id)
    
    if request.method == 'POST':
        frequency = request.POST.get('billing_frequency')
        first_payment_date = request.POST.get('first_payment_date')
        
        # Calculate installments based on frequency
        installments_map = {
            'monthly': 12,
            'quarterly': 4,
            'semi_annual': 2,
            'annual': 1
        }
        
        installments_count = installments_map.get(frequency, 1)
        installment_amount = policy.annual_premium / installments_count
        
        # Create billing schedule
        billing_schedule = BillingSchedule.objects.create(
            policy=policy,
            billing_frequency=frequency,
            total_premium=policy.annual_premium,
            installments_count=installments_count,
            installment_amount=installment_amount,
            first_payment_date=first_payment_date
        )
        
        # Create payment records for each installment
        payment_date = date.fromisoformat(first_payment_date)
        for i in range(1, installments_count + 1):
            PaymentRecord.objects.create(
                policy=policy,
                billing_schedule=billing_schedule,
                installment_number=i,
                due_date=payment_date,
                amount_due=installment_amount
            )
            
            # Calculate next payment date
            if frequency == 'monthly':
                if payment_date.month == 12:
                    payment_date = payment_date.replace(year=payment_date.year + 1, month=1)
                else:
                    payment_date = payment_date.replace(month=payment_date.month + 1)
            elif frequency == 'quarterly':
                payment_date = payment_date + timedelta(days=90)
            elif frequency == 'semi_annual':
                payment_date = payment_date + timedelta(days=180)
        
        messages.success(request, f'Billing schedule created with {installments_count} installments')
        return redirect('applications:policy_detail', policy_id=policy_id)
    
    context = {
        'policy': policy,
        'title': f'Create Billing Schedule - {policy.policy_number}'
    }
    return render(request, 'billing/create_billing_schedule.html', context)



def record_payment(request, payment_id):
    '''Record a payment for an installment'''
    payment = get_object_or_404(PaymentRecord, payment_id=payment_id)
    
    if request.method == 'POST':
        try:
            amount_paid = Decimal(request.POST.get('amount_paid', 0))
            payment_method = request.POST.get('payment_method')
            reference_number = request.POST.get('reference_number', '')
            notes = request.POST.get('notes', '')
            
            payment.amount_paid = amount_paid
            payment.payment_method = payment_method
            payment.payment_date = date.today()
            payment.reference_number = reference_number
            payment.notes = notes
            payment.processed_by = request.user
            
            # Update payment status based on amount
            if amount_paid >= payment.amount_due:
                payment.payment_status = 'paid'
            else:
                payment.payment_status = 'pending'  # Partial payment
            
            payment.save()
            
            messages.success(request, f'Payment recorded: ')
            return JsonResponse({'success': True})
            
        except (ValueError, TypeError) as e:
            return JsonResponse({'success': False, 'error': 'Invalid payment amount'})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def commission_report(request):
    '''Commission tracking and reporting'''
    commissions = Commission.objects.select_related(
        'policy__quote__application__company', 'broker'
    ).all()
    
    # Calculate totals
    total_owed = commissions.filter(commission_status__in=['pending', 'calculated']).aggregate(
        Sum('commission_amount')
    )['commission_amount__sum'] or 0
    
    total_paid = commissions.filter(commission_status='paid').aggregate(
        Sum('commission_amount')
    )['commission_amount__sum'] or 0
    
    context = {
        'commissions': commissions,
        'total_owed': total_owed,
        'total_paid': total_paid,
        'title': 'Commission Report'
    }
    return render(request, 'billing/commission_report.html', context)

@login_required
def policy_billing(request, policy_id):
    """View billing information for a specific policy (sidebar navigation)"""
    policy = get_object_or_404(Policy, policy_id=policy_id)
    
    # Check if billing schedule exists
    has_billing_schedule = hasattr(policy, 'billingschedule')
    billing_schedule = None
    payment_records = []
    pending_payments = 0
    total_paid = 0
    total_due = 0
    
    if has_billing_schedule:
        billing_schedule = policy.billingschedule
        payment_records = PaymentRecord.objects.filter(
            policy=policy
        ).order_by('due_date')
        
        # Calculate payment statistics
        pending_payments = payment_records.filter(
            payment_status='pending'
        ).count()
        
        total_paid = payment_records.filter(
            payment_status='paid'
        ).aggregate(
            total=Sum('amount_paid')
        )['total'] or 0
        
        total_due = payment_records.filter(
            payment_status='pending'
        ).aggregate(
            total=Sum('amount_due')
        )['total'] or 0
    
    # Check for overdue payments
    overdue_payments = []
    if payment_records:
        today = date.today()
        overdue_payments = payment_records.filter(
            payment_status='pending',
            due_date__lt=today
        )
    
    context = {
        'policy': policy,
        'object': policy,  # For sidebar compatibility
        'object_type': 'policy',  # For sidebar compatibility
        'active_tab': 'billing',  # For sidebar highlighting
        'has_billing_schedule': has_billing_schedule,
        'billing_schedule': billing_schedule,
        'payment_records': payment_records,
        'pending_payments': pending_payments,
        'total_paid': total_paid,
        'total_due': total_due,
        'overdue_payments': overdue_payments,
        'title': f'Billing - Policy {policy.policy_number}'
    }
    
    # Check if the billing template exists, otherwise use placeholder
    try:
        return render(request, 'billing/policy_billing.html', context)
    except:
        # If template doesn't exist, use the placeholder template
        context.update({
            'page_title': 'Billing & Payments',
            'icon': 'fa-credit-card',
            'description': 'Manage billing and payment schedules for this policy.',
            'features': [
                'View payment schedule',
                'Process payments',
                'Track payment history',
                'Generate invoices',
                'Manage payment methods'
            ]
        })
        return render(request, 'applications/placeholder_page.html', context)