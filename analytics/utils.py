# analytics/utils.py

from django.db.models import Sum, Count, Avg, Q
from datetime import datetime, timedelta
from decimal import Decimal


def calculate_growth_rate(current, previous):
    """Calculate percentage growth rate"""
    if previous == 0:
        return 100 if current > 0 else 0
    return ((current - previous) / previous) * 100


def get_date_range(period='month'):
    """Get start and end dates for common periods"""
    today = datetime.now().date()
    
    if period == 'month':
        start = today.replace(day=1)
        if today.month == 12:
            end = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            end = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
    
    elif period == 'quarter':
        quarter = (today.month - 1) // 3
        start = today.replace(month=quarter * 3 + 1, day=1)
        if quarter == 3:
            end = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            end = today.replace(month=(quarter + 1) * 3 + 1, day=1) - timedelta(days=1)
    
    elif period == 'year':
        start = today.replace(month=1, day=1)
        end = today.replace(month=12, day=31)
    
    else:  # default to last 30 days
        start = today - timedelta(days=30)
        end = today
    
    return start, end


def format_currency(amount):
    """Format amount as currency"""
    if amount is None:
        return "$0"
    return "${:,.2f}".format(amount)


def calculate_loss_ratio(claims_paid, premium_earned):
    """Calculate loss ratio as percentage"""
    if premium_earned == 0:
        return 0
    return (claims_paid / premium_earned) * 100


def get_risk_score(company):
    """Calculate risk score for a company based on claims history"""
    from claims.models import Claim
    from applications.models import Quote
    
    # Get claims and premium data
    total_claims = Claim.objects.filter(
        quote__application__company=company
    ).aggregate(
        total=Sum('paid_amount')
    )['total'] or Decimal('0')
    
    total_premium = Quote.objects.filter(
        application__company=company,
        quote_status='accepted'
    ).aggregate(
        total=Sum('total_premium')
    )['total'] or Decimal('0')
    
    if total_premium == 0:
        return 'N/A'
    
    loss_ratio = (total_claims / total_premium) * 100
    
    if loss_ratio < 40:
        return 'Low'
    elif loss_ratio < 70:
        return 'Medium'
    else:
        return 'High'


def get_retention_rate(start_date, end_date):
    """Calculate client retention rate"""
    from applications.models import Company
    
    # Clients at start of period
    # FIXED: Changed from created_date to created_at
    clients_start = Company.objects.filter(
        created_at__lt=start_date,
        is_active=True
    ).count()
    
    # Clients retained (still active with policies)
    # FIXED: Changed from created_date to created_at and fixed relationship paths
    clients_retained = Company.objects.filter(
        created_at__lt=start_date,
        is_active=True,
        application__quote__quote_status='accepted',
        application__quote__expiration_date__gte=end_date
    ).distinct().count()
    
    if clients_start == 0:
        return 0
    
    return (clients_retained / clients_start) * 100