from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from documents.portal_models import PortalDocument
from applications.models import Company

@login_required
def company_documents_admin(request, company_id):
    """Internal view showing ALL documents including removed ones"""
    company = get_object_or_404(Company, company_id=company_id)
    
    # Get ALL documents for company (including removed)
    documents = PortalDocument.objects.all_for_company(company).order_by('-uploaded_at')
    
    # Pagination
    paginator = Paginator(documents, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Statistics
    stats = {
        'total': documents.count(),
        'visible': documents.filter(client_visible=True).count(),
        'removed': documents.filter(client_visible=False).count(),
        'archived': documents.exclude(archive_path__isnull=True).count(),
    }
    
    context = {
        'company': company,
        'page_obj': page_obj,
        'stats': stats,
        'show_all': True,
    }
    
    return render(request, 'applications/company_documents_admin.html', context)
