from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import HttpResponse, Http404, FileResponse
from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.db.models import Q
from django.utils import timezone
import os
import mimetypes
from .models import Document, DocumentCategory, DocumentAccessLog
from applications.models import Application, Quote, Company

def document_list(request):
    documents = Document.objects.select_related('document_category', 'application', 'quote', 'company').filter(is_current_version=True)
    
    # Filter by category
    category_id = request.GET.get('category')
    if category_id:
        documents = documents.filter(document_category_id=category_id)
    
    # Search functionality
    search = request.GET.get('search')
    if search:
        documents = documents.filter(
            Q(document_name__icontains=search) |
            Q(description__icontains=search) |
            Q(original_filename__icontains=search)
        )
    
    categories = DocumentCategory.objects.filter(is_active=True)
    
    context = {
        'documents': documents,
        'categories': categories,
        'current_category': category_id,
        'search_query': search,
    }
    return render(request, 'documents/document_list.html', context)

def document_detail(request, pk):
    document = get_object_or_404(Document, pk=pk)
    
    # Log the access
    DocumentAccessLog.objects.create(
        document=document,
        accessed_by=request.user if request.user.is_authenticated else None,
        access_type='view',
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT', '')
    )
    
    # Get document versions
    versions = Document.objects.filter(
        Q(parent_document=document) | Q(pk=document.pk)
    ).order_by('-version_number')
    
    context = {
        'document': document,
        'versions': versions,
    }
    return render(request, 'documents/document_detail.html', context)

def document_upload(request):
    if request.method == 'POST':
        try:
            # Get form data
            uploaded_file = request.FILES.get('file')
            document_name = request.POST.get('document_name')
            category_id = request.POST.get('category')
            description = request.POST.get('description', '')
            application_id = request.POST.get('application')
            quote_id = request.POST.get('quote')
            company_id = request.POST.get('company')
            
            if not uploaded_file:
                messages.error(request, 'No file selected.')
                return redirect('documents:document_upload')
            
            if not document_name:
                document_name = uploaded_file.name
            
            # Create file path
            file_extension = os.path.splitext(uploaded_file.name)[1]
            safe_filename = f"{timezone.now().strftime('%Y%m%d_%H%M%S')}_{uploaded_file.name}"
            file_path = f"documents/{safe_filename}"
            
            # Save file
            saved_path = default_storage.save(file_path, ContentFile(uploaded_file.read()))
            
            # Create document record
            document = Document.objects.create(
                document_category_id=category_id,
                application_id=application_id if application_id else None,
                quote_id=quote_id if quote_id else None,
                company_id=company_id if company_id else None,
                document_name=document_name,
                original_filename=uploaded_file.name,
                file_path=saved_path,
                file_size_bytes=uploaded_file.size,
                mime_type=uploaded_file.content_type or mimetypes.guess_type(uploaded_file.name)[0] or 'application/octet-stream',
                file_extension=file_extension,
                description=description,
                uploaded_by=request.user if request.user.is_authenticated else None,
            )
            
            messages.success(request, f'Document "{document.document_name}" uploaded successfully!')
            return redirect('documents:document_detail', pk=document.pk)
            
        except Exception as e:
            messages.error(request, f'Error uploading file: {str(e)}')
            return redirect('documents:document_upload')
    
    # GET request - show upload form
    categories = DocumentCategory.objects.filter(is_active=True)
    applications = Application.objects.filter(application_status__in=['received', 'in_progress', 'quoted'])[:50]
    quotes = Quote.objects.filter(quote_status__in=['draft', 'presented'])[:50]
    companies = Company.objects.filter(is_active=True)[:50]
    
    context = {
        'categories': categories,
        'applications': applications,
        'quotes': quotes,
        'companies': companies,
    }
    return render(request, 'documents/document_upload.html', context)

def document_download(request, pk):
    document = get_object_or_404(Document, pk=pk)
    
    # Log the access
    DocumentAccessLog.objects.create(
        document=document,
        accessed_by=request.user if request.user.is_authenticated else None,
        access_type='download',
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT', '')
    )
    
    try:
        # Check if file exists
        if not default_storage.exists(document.file_path):
            raise Http404("Document file not found.")
        
        # Get file
        file_obj = default_storage.open(document.file_path, 'rb')
        
        response = FileResponse(
            file_obj,
            content_type=document.mime_type,
            filename=document.original_filename
        )
        
        return response
        
    except Exception as e:
        messages.error(request, f'Error downloading file: {str(e)}')
        return redirect('documents:document_detail', pk=document.pk)

def document_delete(request, pk):
    document = get_object_or_404(Document, pk=pk)
    
    if request.method == 'POST':
        try:
            # Delete file from storage
            if default_storage.exists(document.file_path):
                default_storage.delete(document.file_path)
            
            # Log the access
            DocumentAccessLog.objects.create(
                document=document,
                accessed_by=request.user if request.user.is_authenticated else None,
                access_type='delete',
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            document_name = document.document_name
            document.delete()
            
            messages.success(request, f'Document "{document_name}" deleted successfully!')
            return redirect('documents:document_list')
            
        except Exception as e:
            messages.error(request, f'Error deleting document: {str(e)}')
            return redirect('documents:document_detail', pk=document.pk)
    
    context = {'document': document}
    return render(request, 'documents/document_delete.html', context)
