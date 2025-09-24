# File: applications/document_views.py
# Views for document generation and management

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse, FileResponse
from django.contrib.auth.decorators import login_required
from django.conf import settings
import os

from .models import Policy
from .document_models import (
    DocumentTemplate, PolicyDocumentPackage, 
    EndorsementDocument, DocumentDelivery
)
from .document_generator import DocumentGenerator
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

def generate_policy_documents(request, policy_id):
    """Generate policy document package"""
    policy = get_object_or_404(Policy, policy_id=policy_id)
    
    # Check if documents already exist
    existing_package = PolicyDocumentPackage.objects.filter(
        policy=policy,
        is_current=True
    ).first()
    
    if existing_package and not request.GET.get('regenerate'):
        messages.info(request, 'Policy documents already generated.')
        return redirect('applications:view_policy_documents', policy_id=policy_id)
    
    try:
        # Generate the documents
        generator = DocumentGenerator()
        package = generator.generate_policy_package(policy, reissue=bool(existing_package))
        
        messages.success(request, f'Policy documents generated successfully! Package: {package.package_number}')
        return redirect('applications:view_policy_documents', policy_id=policy_id)
        
    except Exception as e:
        messages.error(request, f'Error generating documents: {str(e)}')
        return redirect('applications:policy_detail', policy_id=policy_id)

def view_policy_documents(request, policy_id):
    """View policy document package"""
    policy = get_object_or_404(Policy, policy_id=policy_id)
    
    # Get current package
    package = PolicyDocumentPackage.objects.filter(
        policy=policy,
        is_current=True
    ).first()
    
    if not package:
        messages.warning(request, 'No documents generated for this policy yet.')
        return redirect('applications:policy_detail', policy_id=policy_id)
    
    # Get all packages (for version history)
    all_packages = PolicyDocumentPackage.objects.filter(
        policy=policy
    ).order_by('-package_version')
    
    context = {
        'policy': policy,
        'package': package,
        'all_packages': all_packages,
        'components': package.components.all().order_by('sequence_order'),
    }
    
    return render(request, 'applications/policy_documents.html', context)

def download_policy_package(request, package_id):
    """Download policy PDF package"""
    package = get_object_or_404(PolicyDocumentPackage, package_id=package_id)
    
    # Get file path
    file_path = os.path.join(settings.MEDIA_ROOT, 'documents', package.combined_pdf_path)
    
    if not os.path.exists(file_path):
        messages.error(request, 'Document file not found.')
        return redirect('applications:policy_detail', policy_id=package.policy.policy_id)
    
    # Return file
    response = FileResponse(
        open(file_path, 'rb'),
        content_type='application/pdf'
    )
    response['Content-Disposition'] = f'attachment; filename="{package.package_number}.pdf"'
    
    return response

def manage_templates(request):
    """Manage document templates"""
    templates = DocumentTemplate.objects.all().order_by('template_type', 'default_sequence')
    
    # Group by type
    grouped_templates = {}
    for template in templates:
        template_type = template.get_template_type_display()
        if template_type not in grouped_templates:
            grouped_templates[template_type] = []
        grouped_templates[template_type].append(template)
    
    context = {
        'grouped_templates': grouped_templates,
        'total_count': templates.count(),
    }
    
    return render(request, 'applications/manage_templates.html', context)

def upload_template_file(request, template_id):
    """Upload PDF file for a template"""
    template = get_object_or_404(DocumentTemplate, template_id=template_id)
    
    if request.method == 'POST' and request.FILES.get('pdf_file'):
        pdf_file = request.FILES['pdf_file']
        
        # Validate file type
        if not pdf_file.name.lower().endswith('.pdf'):
            messages.error(request, 'Please upload a PDF file.')
            return redirect('applications:manage_templates')
        
        # Create storage path
        file_path = f'templates/{template.template_code.lower()}.pdf'
        full_path = os.path.join(settings.MEDIA_ROOT, 'documents', file_path)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        # Save file
        with open(full_path, 'wb+') as destination:
            for chunk in pdf_file.chunks():
                destination.write(chunk)
        
        # Update template
        template.storage_path = file_path
        template.save()
        
        messages.success(request, f'PDF uploaded for {template.template_name}')
    
    return redirect('applications:manage_templates')

def test_generate_policy(request, policy_id):
    """Quick test to generate a basic policy document"""
    policy = get_object_or_404(Policy, policy_id=policy_id)
    
    try:
        # Check if we have templates
        templates = DocumentTemplate.objects.filter(
            product=policy.quote.application.product,
            is_active=True
        )
        
        if not templates.exists():
            messages.warning(request, 'No templates found for this product.')
            return redirect('applications:policy_detail', policy_id=policy_id)
        
        # Generate the package
        generator = DocumentGenerator()
        package = generator.generate_policy_package(policy)
        
        messages.success(request, f'Documents generated! Package: {package.package_number}')
        return redirect('applications:view_policy_documents', policy_id=policy_id)
        
    except Exception as e:
        messages.error(request, f'Error: {str(e)}')
        return redirect('applications:policy_detail', policy_id=policy_id)

def create_endorsement(request, policy_id):
    """Create an endorsement for a policy"""
    policy = get_object_or_404(Policy, policy_id=policy_id)
    
    if request.method == 'POST':
        template_code = request.POST.get('template_code')
        effective_date = request.POST.get('effective_date')
        
        # Collect endorsement data
        endorsement_data = {
            'additional_insured_name': request.POST.get('additional_insured_name', ''),
            'additional_insured_address': request.POST.get('additional_insured_address', ''),
            'description': request.POST.get('description', ''),
            'waiver_party': request.POST.get('waiver_party', ''),
        }
        
        try:
            generator = EndorsementGenerator()
            endorsement = generator.create_endorsement(
                policy=policy,
                template_code=template_code,
                endorsement_data=endorsement_data,
                effective_date=datetime.strptime(effective_date, '%Y-%m-%d').date() if effective_date else None
            )
            
            messages.success(request, f'Endorsement {endorsement.endorsement_number} created successfully!')
            return redirect('applications:view_endorsements', policy_id=policy_id)
            
        except Exception as e:
            messages.error(request, f'Error creating endorsement: {str(e)}')
    
    # Get available endorsement templates
    endorsement_templates = DocumentTemplate.objects.filter(
        template_type='endorsement',
        product=policy.quote.application.product,
        is_active=True
    )
    
    context = {
        'policy': policy,
        'templates': endorsement_templates,
        'today': datetime.now().date().isoformat(),
    }
    
    return render(request, 'applications/create_endorsement.html', context)

def view_endorsements(request, policy_id):
    """View all endorsements for a policy"""
    policy = get_object_or_404(Policy, policy_id=policy_id)
    endorsements = EndorsementDocument.objects.filter(
        policy=policy
    ).order_by('-endorsement_sequence')
    
    context = {
        'policy': policy,
        'endorsements': endorsements,
    }
    
    return render(request, 'applications/view_endorsements.html', context)

def download_endorsement(request, endorsement_id):
    """Download an endorsement PDF"""
    endorsement = get_object_or_404(EndorsementDocument, endorsement_id=endorsement_id)
    
    file_path = os.path.join(settings.MEDIA_ROOT, 'documents', endorsement.document_path)
    
    if not os.path.exists(file_path):
        messages.error(request, 'Endorsement file not found.')
        return redirect('applications:view_endorsements', policy_id=endorsement.policy.policy_id)
    
    response = FileResponse(
        open(file_path, 'rb'),
        content_type='application/pdf'
    )
    response['Content-Disposition'] = f'attachment; filename="{endorsement.endorsement_number}.pdf"'
    
    return response

def upload_templates_page(request):
    """Display the upload interface"""
    # Get templates that need files (static and hybrid)
    templates_needing_files = DocumentTemplate.objects.filter(
        template_format__in=['static', 'hybrid']
    ).order_by('template_type', 'template_code')
    
    context = {
        'templates_needing_files': templates_needing_files,
    }
    
    return render(request, 'applications/upload_templates.html', context)

def bulk_upload_templates(request):
    """Handle bulk upload of PDF templates"""
    if request.method == 'POST' and request.FILES.getlist('pdf_files'):
        uploaded_count = 0
        errors = []
        
        for pdf_file in request.FILES.getlist('pdf_files'):
            try:
                # Extract template code from filename
                filename = pdf_file.name
                template_code = filename.replace('.pdf', '').replace('.PDF', '').upper()
                
                # Try to find matching template
                try:
                    template = DocumentTemplate.objects.get(template_code=template_code)
                except DocumentTemplate.DoesNotExist:
                    # Try without the product suffix
                    template_code_parts = template_code.split('-')
                    if len(template_code_parts) > 2:
                        base_code = '-'.join(template_code_parts[:-1])
                        try:
                            template = DocumentTemplate.objects.get(
                                template_code__startswith=base_code
                            )
                        except (DocumentTemplate.DoesNotExist, DocumentTemplate.MultipleObjectsReturned):
                            errors.append(f"No template found for {filename}")
                            continue
                    else:
                        errors.append(f"No template found for {filename}")
                        continue
                
                # Save the file
                file_path = f'templates/{template.template_code.lower()}.pdf'
                full_path = os.path.join(settings.MEDIA_ROOT, 'documents', file_path)
                
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                
                with open(full_path, 'wb+') as destination:
                    for chunk in pdf_file.chunks():
                        destination.write(chunk)
                
                # Update template
                template.storage_path = file_path
                template.save()
                uploaded_count += 1
                
            except Exception as e:
                errors.append(f"Error with {filename}: {str(e)}")
        
        if uploaded_count:
            messages.success(request, f'{uploaded_count} files uploaded successfully!')
        
        if errors:
            for error in errors:
                messages.error(request, error)
    
    return redirect('applications:upload_templates_page')

def verify_template_files(request):
    """Verify which templates have files and which are missing"""
    templates = DocumentTemplate.objects.filter(
        template_format__in=['static', 'hybrid']
    )
    
    results = {
        'has_file': [],
        'missing_file': [],
        'file_not_found': []
    }
    
    for template in templates:
        if template.storage_path:
            file_path = os.path.join(settings.MEDIA_ROOT, 'documents', template.storage_path)
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                results['has_file'].append({
                    'template': template,
                    'size': file_size
                })
            else:
                results['file_not_found'].append(template)
        else:
            results['missing_file'].append(template)
    
    context = {
        'results': results,
        'total_templates': templates.count(),
        'files_ok': len(results['has_file']),
        'files_missing': len(results['missing_file']),
        'files_not_found': len(results['file_not_found']),
    }
    
    return render(request, 'applications/verify_templates.html', context)
