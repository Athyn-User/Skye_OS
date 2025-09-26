from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from documents.portal_models import PortalDocument
from applications.models import Company

@login_required
def company_files_view(request, company_id):
    """Internal view for underwriters to see all client-uploaded files"""
    company = get_object_or_404(Company, company_id=company_id)
    
    # Get ALL documents for this company (including removed ones)
    documents = PortalDocument.objects.filter(company=company).order_by('-uploaded_at')
    
    # Filter options
    doc_type = request.GET.get('type')
    visibility = request.GET.get('visibility', 'all')
    
    if doc_type:
        documents = documents.filter(document_type=doc_type)
    
    if visibility == 'visible':
        documents = documents.filter(client_visible=True)
    elif visibility == 'removed':
        documents = documents.filter(client_visible=False)
    
    # Statistics
    stats = {
        'total': PortalDocument.objects.filter(company=company).count(),
        'visible': PortalDocument.objects.filter(company=company, client_visible=True).count(),
        'removed': PortalDocument.objects.filter(company=company, client_visible=False).count(),
        'loss_runs': PortalDocument.objects.filter(company=company, document_type='loss_run').count(),
        'applications': PortalDocument.objects.filter(company=company, document_type='application').count(),
        'financial': PortalDocument.objects.filter(company=company, document_type='financial').count(),
    }
    
    # Pagination
    paginator = Paginator(documents, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'company': company,
        'page_obj': page_obj,
        'stats': stats,
        'current_type': doc_type,
        'current_visibility': visibility,
        'document_types': PortalDocument.DOCUMENT_TYPES,
    }
    
    return render(request, 'applications/company_files.html', context)

@login_required
def download_company_file(request, company_id, document_id):
    """Download file from company archive (internal use)"""
    company = get_object_or_404(Company, company_id=company_id)
    document = get_object_or_404(PortalDocument, document_id=document_id, company=company)
    
    # Use archive path for internal downloads
    file_path = document.get_archive_path() or document.get_active_path()
    
    import os
    import mimetypes
    from django.http import FileResponse
    
    if '.' not in document.document_name:
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

@login_required
def view_company_file(request, company_id, document_id):
    """View file in browser (internal use)"""
    company = get_object_or_404(Company, company_id=company_id)
    document = get_object_or_404(PortalDocument, document_id=document_id, company=company)
    
    # Use archive path for internal viewing
    file_path = document.get_archive_path() or document.get_active_path()
    
    import os
    import mimetypes
    from django.http import FileResponse
    
    mime_type, _ = mimetypes.guess_type(file_path)
    
    # For PDFs and images, display inline. For other files, download
    if mime_type and (mime_type.startswith('image/') or mime_type == 'application/pdf'):
        disposition = 'inline'
    else:
        disposition = 'attachment'
    
    if '.' not in document.document_name:
        _, ext = os.path.splitext(file_path)
        filename = f"{document.document_name}{ext}"
    else:
        filename = document.document_name
    
    response = FileResponse(
        open(file_path, 'rb'),
        content_type=mime_type or 'application/octet-stream'
    )
    response['Content-Disposition'] = f'{disposition}; filename="{filename}"'
    
    return response
