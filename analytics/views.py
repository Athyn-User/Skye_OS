# analytics/views.py

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Avg, Q, F
from django.db.models.functions import TruncMonth, TruncWeek
from django.utils import timezone
from datetime import timedelta, datetime
from decimal import Decimal
import json

from applications.models import Quote, Application, Certificate, Company
from claims.models import Claim, ClaimPayment
from client_portal.models import PaymentRequest


@login_required
def analytics_dashboard(request):
    """Main analytics dashboard with key metrics"""
    
    # Date ranges
    today = timezone.now().date()
    current_month_start = today.replace(day=1)
    last_month_start = (current_month_start - timedelta(days=1)).replace(day=1)
    last_month_end = current_month_start - timedelta(days=1)
    year_start = today.replace(month=1, day=1)
    last_30_days = today - timedelta(days=30)
    last_90_days = today - timedelta(days=90)
    
    # Revenue Metrics
    current_month_revenue = Quote.objects.filter(
        quote_status='accepted',
        quote_date__gte=current_month_start,
        quote_date__lte=today
    ).aggregate(total=Sum('total_premium'))['total'] or Decimal('0')
    
    last_month_revenue = Quote.objects.filter(
        quote_status='accepted',
        quote_date__gte=last_month_start,
        quote_date__lte=last_month_end
    ).aggregate(total=Sum('total_premium'))['total'] or Decimal('0')
    
    ytd_revenue = Quote.objects.filter(
        quote_status='accepted',
        quote_date__gte=year_start,
        quote_date__lte=today
    ).aggregate(total=Sum('total_premium'))['total'] or Decimal('0')
    
    # Calculate growth
    revenue_growth = 0
    if last_month_revenue > 0:
        revenue_growth = ((current_month_revenue - last_month_revenue) / last_month_revenue * 100)
    
    # Policy Metrics
    active_policies = Quote.objects.filter(
        quote_status='accepted',
        expiration_date__gte=today
    ).count()
    
    new_policies_this_month = Quote.objects.filter(
        quote_status='accepted',
        quote_date__gte=current_month_start
    ).count()
    
    expiring_soon = Quote.objects.filter(
        quote_status='accepted',
        expiration_date__gte=today,
        expiration_date__lte=today + timedelta(days=30)
    ).count()
    
    # Claims Metrics
    open_claims = Claim.objects.exclude(
        claim_status__in=['CLOSED', 'DENIED']
    ).count()
    
    claims_this_month = Claim.objects.filter(
        reported_date__gte=current_month_start
    ).count()
    
    total_claims_paid = ClaimPayment.objects.filter(
        payment_date__gte=year_start
    ).exclude(payment_type='RECOVERY').aggregate(
        total=Sum('amount')
    )['total'] or Decimal('0')
    
    # Loss Ratio Calculation
    loss_ratio = 0
    if ytd_revenue > 0:
        loss_ratio = (total_claims_paid / ytd_revenue * 100)
    
    # Client Metrics
    total_clients = Company.objects.filter(is_active=True).count()
    
    # FIXED: Changed from created_date to created_at
    new_clients_this_month = Company.objects.filter(
        created_at__gte=current_month_start
    ).count()
    
    # Revenue by Month (Last 12 months)
    twelve_months_ago = today - timedelta(days=365)
    monthly_revenue = Quote.objects.filter(
        quote_status='accepted',
        quote_date__gte=twelve_months_ago
    ).annotate(
        month=TruncMonth('quote_date')
    ).values('month').annotate(
        revenue=Sum('total_premium')
    ).order_by('month')
    
    # Claims by Type
    claims_by_type = Claim.objects.values('claim_type').annotate(
        count=Count('id'),
        total_paid=Sum('paid_amount')
    ).order_by('-count')
    
    # Top 5 Clients by Premium
    top_clients = Company.objects.filter(
        application__quote__quote_status='accepted',
        application__quote__quote_date__gte=year_start
    ).annotate(
        total_premium=Sum('application__quote__total_premium')
    ).order_by('-total_premium')[:5]
    
    # Conversion Rate
    total_quotes = Quote.objects.filter(
        quote_date__gte=last_30_days
    ).count()
    
    accepted_quotes = Quote.objects.filter(
        quote_date__gte=last_30_days,
        quote_status='accepted'
    ).count()
    
    conversion_rate = 0
    if total_quotes > 0:
        conversion_rate = (accepted_quotes / total_quotes * 100)
    
    # Prepare chart data
    revenue_chart_labels = [item['month'].strftime('%b %Y') for item in monthly_revenue]
    revenue_chart_data = [float(item['revenue']) for item in monthly_revenue]
    
    claims_chart_labels = [item['claim_type'] for item in claims_by_type]
    claims_chart_data = [item['count'] for item in claims_by_type]
    
    context = {
        # Revenue Metrics
        'current_month_revenue': current_month_revenue,
        'last_month_revenue': last_month_revenue,
        'ytd_revenue': ytd_revenue,
        'revenue_growth': revenue_growth,
        
        # Policy Metrics
        'active_policies': active_policies,
        'new_policies_this_month': new_policies_this_month,
        'expiring_soon': expiring_soon,
        
        # Claims Metrics
        'open_claims': open_claims,
        'claims_this_month': claims_this_month,
        'total_claims_paid': total_claims_paid,
        'loss_ratio': loss_ratio,
        
        # Client Metrics
        'total_clients': total_clients,
        'new_clients_this_month': new_clients_this_month,
        'conversion_rate': conversion_rate,
        
        # Chart Data
        'revenue_chart_labels': json.dumps(revenue_chart_labels),
        'revenue_chart_data': json.dumps(revenue_chart_data),
        'claims_chart_labels': json.dumps(claims_chart_labels),
        'claims_chart_data': json.dumps(claims_chart_data),
        
        # Top Lists
        'top_clients': top_clients,
        
        # Date Info
        'report_date': today,
        'month_name': today.strftime('%B %Y'),
    }
    
    return render(request, 'analytics/dashboard.html', context)


@login_required
def revenue_report(request):
    """Detailed revenue analysis"""
    
    # Get date range from request or default to last 12 months
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=365)
    
    if request.GET.get('start_date'):
        start_date = datetime.strptime(request.GET.get('start_date'), '%Y-%m-%d').date()
    if request.GET.get('end_date'):
        end_date = datetime.strptime(request.GET.get('end_date'), '%Y-%m-%d').date()
    
    # Revenue by Product
    revenue_by_product = Quote.objects.filter(
        quote_status='accepted',
        quote_date__gte=start_date,
        quote_date__lte=end_date
    ).values(
        'application__product__product_name'
    ).annotate(
        count=Count('id'),
        total=Sum('total_premium'),
        average=Avg('total_premium')
    ).order_by('-total')
    
    # Revenue by Broker
    revenue_by_broker = Quote.objects.filter(
        quote_status='accepted',
        quote_date__gte=start_date,
        quote_date__lte=end_date
    ).values(
        'application__broker__broker_name'
    ).annotate(
        count=Count('id'),
        total=Sum('total_premium'),
        commission=Sum('commission_amount')
    ).order_by('-total')
    
    # Monthly Trend
    monthly_trend = Quote.objects.filter(
        quote_status='accepted',
        quote_date__gte=start_date,
        quote_date__lte=end_date
    ).annotate(
        month=TruncMonth('quote_date')
    ).values('month').annotate(
        new_business=Sum('total_premium', filter=Q(quote_version=1)),
        renewals=Sum('total_premium', filter=Q(quote_version__gt=1)),
        total=Sum('total_premium')
    ).order_by('month')
    
    # Payment Collection Status
    collection_status = PaymentRequest.objects.filter(
        due_date__gte=start_date,
        due_date__lte=end_date
    ).aggregate(
        total_billed=Sum('amount'),
        total_collected=Sum('paid_amount'),
        pending=Sum('amount', filter=Q(status='PENDING')),
        overdue=Sum('amount', filter=Q(status='PENDING', due_date__lt=timezone.now().date()))
    )
    
    context = {
        'start_date': start_date,
        'end_date': end_date,
        'revenue_by_product': revenue_by_product,
        'revenue_by_broker': revenue_by_broker,
        'monthly_trend': monthly_trend,
        'collection_status': collection_status,
    }
    
    return render(request, 'analytics/revenue_report.html', context)


@login_required
def claims_report(request):
    """Detailed claims analysis"""
    
    # Get date range
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=365)
    
    if request.GET.get('start_date'):
        start_date = datetime.strptime(request.GET.get('start_date'), '%Y-%m-%d').date()
    if request.GET.get('end_date'):
        end_date = datetime.strptime(request.GET.get('end_date'), '%Y-%m-%d').date()
    
    claims = Claim.objects.filter(
        reported_date__gte=start_date,
        reported_date__lte=end_date
    )
    
    # Claims Summary
    claims_summary = claims.aggregate(
        total_claims=Count('id'),
        open_claims=Count('id', filter=~Q(claim_status__in=['CLOSED', 'DENIED'])),
        approved_claims=Count('id', filter=Q(claim_status='APPROVED')),
        denied_claims=Count('id', filter=Q(claim_status='DENIED')),
        avg_processing_time=Avg(F('closed_date') - F('reported_date')),
        total_reserved=Sum('reserve_amount'),
        total_paid=Sum('paid_amount'),
        total_recovered=Sum('recovered_amount')
    )
    
    # Claims by Type and Severity
    claims_by_type = claims.values('claim_type').annotate(
        count=Count('id'),
        avg_amount=Avg('paid_amount'),
        total_paid=Sum('paid_amount')
    ).order_by('-count')
    
    claims_by_severity = claims.values('severity').annotate(
        count=Count('id'),
        avg_amount=Avg('paid_amount'),
        total_paid=Sum('paid_amount')
    ).order_by('severity')
    
    # Monthly Claims Trend
    monthly_claims = claims.annotate(
        month=TruncMonth('reported_date')
    ).values('month').annotate(
        count=Count('id'),
        total_paid=Sum('paid_amount')
    ).order_by('month')
    
    # Top Loss Causes
    top_causes = claims.values('cause_of_loss').annotate(
        count=Count('id'),
        total_paid=Sum('paid_amount')
    ).order_by('-count')[:10]
    
    # Adjuster Performance
    adjuster_performance = claims.filter(
        adjuster__isnull=False
    ).values(
        'adjuster__first_name',
        'adjuster__last_name'
    ).annotate(
        count=Count('id'),
        avg_time_to_close=Avg(F('closed_date') - F('assigned_date')),
        total_paid=Sum('paid_amount')
    ).order_by('-count')
    
    context = {
        'start_date': start_date,
        'end_date': end_date,
        'claims_summary': claims_summary,
        'claims_by_type': claims_by_type,
        'claims_by_severity': claims_by_severity,
        'monthly_claims': monthly_claims,
        'top_causes': top_causes,
        'adjuster_performance': adjuster_performance,
    }
    
    return render(request, 'analytics/claims_report.html', context)


@login_required
def client_report(request):
    """Client analytics and retention metrics"""
    
    today = timezone.now().date()
    year_ago = today - timedelta(days=365)
    
    # Client Summary
    total_clients = Company.objects.filter(is_active=True).count()
    
    # FIXED: Changed from created_date to created_at
    new_clients = Company.objects.filter(
        created_at__gte=year_ago
    ).count()
    
    # Client Segmentation by Premium
    client_segments = Company.objects.filter(
        is_active=True
    ).annotate(
        annual_premium=Sum(
            'application__quote__total_premium',
            filter=Q(
                application__quote__quote_status='accepted',
                application__quote__quote_date__gte=year_ago
            )
        )
    ).values('annual_premium').annotate(
        count=Count('id')
    )
    
    # Categorize clients
    small_clients = sum(1 for seg in client_segments if seg['annual_premium'] and seg['annual_premium'] < 10000)
    medium_clients = sum(1 for seg in client_segments if seg['annual_premium'] and 10000 <= seg['annual_premium'] < 50000)
    large_clients = sum(1 for seg in client_segments if seg['annual_premium'] and seg['annual_premium'] >= 50000)
    
    # Retention Rate
    # FIXED: Changed from created_date to created_at
    clients_year_ago = Company.objects.filter(
        created_at__lte=year_ago
    ).count()
    
    # FIXED: Changed from created_date to created_at
    retained_clients = Company.objects.filter(
        created_at__lte=year_ago,
        is_active=True,
        application__quote__quote_status='accepted',
        application__quote__expiration_date__gte=today
    ).distinct().count()
    
    retention_rate = 0
    if clients_year_ago > 0:
        retention_rate = (retained_clients / clients_year_ago * 100)
    
    # Top Clients by Premium
    top_clients = Company.objects.filter(
        is_active=True
    ).annotate(
        total_premium=Sum(
            'application__quote__total_premium',
            filter=Q(
                application__quote__quote_status='accepted',
                application__quote__quote_date__gte=year_ago
            )
        ),
        policy_count=Count(
            'application__quote',
            filter=Q(
                application__quote__quote_status='accepted'
            )
        ),
        claim_count=Count(
            'application__quote__claim'
        )
    ).order_by('-total_premium')[:20]
    
    # Client Growth Trend
    # FIXED: Changed from created_date to created_at
    monthly_clients = Company.objects.filter(
        created_at__gte=year_ago
    ).annotate(
        month=TruncMonth('created_at')
    ).values('month').annotate(
        new=Count('id')
    ).order_by('month')
    
    context = {
        'total_clients': total_clients,
        'new_clients': new_clients,
        'small_clients': small_clients,
        'medium_clients': medium_clients,
        'large_clients': large_clients,
        'retention_rate': retention_rate,
        'top_clients': top_clients,
        'monthly_clients': monthly_clients,
    }
    
    return render(request, 'analytics/client_report.html', context)