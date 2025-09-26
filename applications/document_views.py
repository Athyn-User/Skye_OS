# File: applications/document_views.py
# Views for document generation and management - Enhanced with API endpoints

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse, FileResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.conf import settings
from django.utils import timezone
from django.db.models import Q, Count, Max
from datetime import datetime
import os
import json
import logging

from .models import Policy
from .document_models import (
    DocumentTemplate, PolicyDocumentPackage, 
    EndorsementDocument, DocumentDelivery, DocumentComponent
)
from .document_generator import DocumentGenerator
from .endorsement_generator import EndorsementGenerator
from .document_service import EnhancedDocumentService
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

logger = logging.getLogger(__name__)

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
    """View policy document package - generate documents if they don't exist"""
    policy = get_object_or_404(Policy, policy_id=policy_id)
    
    # Get current package
    package = PolicyDocumentPackage.objects.filter(
        policy=policy,
        is_current=True
    ).first()
    
    # If no package exists, generate documents first
    if not package:
        try:
            # Use enhanced service to generate documents
            service = EnhancedDocumentService()
            package = service.create_document_package(policy)
            
            messages.success(request, f'Policy documents generated successfully! Package: {package.package_number}')
            
        except Exception as e:
            messages.error(request, f'Error generating documents: {str(e)}')
            return redirect('applications:policy_detail', policy_id=policy_id)
    
    # Get all packages (for version history)
    all_packages = PolicyDocumentPackage.objects.filter(
        policy=policy
    ).order_by('-package_version')
    
    # Get components for current package
    components = package.components.all().order_by('sequence_order') if package else []
    
    # Get available templates for adding components - using template_id instead of id
    available_templates = DocumentTemplate.objects.filter(
        product=policy.quote.application.product,
        is_active=True
    ).exclude(
        template_id__in=components.values_list('template_id', flat=True)
    ) if package and components else DocumentTemplate.objects.filter(
        product=policy.quote.application.product,
        is_active=True
    )
    
    context = {
        'policy': policy,
        'package': package,
        'all_packages': all_packages,
        'components': components,
        'available_templates': available_templates,
        'has_documents': bool(package),
        'latest_package': package,
    }
    
    return render(request, 'applications/policy_documents_enhanced.html', context)

# Enhanced API Endpoints for JavaScript Integration

@login_required
@require_http_methods(["GET"])
def get_document_status(request, policy_id):
    """Get current status of all document components for a policy - API endpoint"""
    try:
        policy = get_object_or_404(Policy, policy_id=policy_id)
        
        # Get latest document package
        package = PolicyDocumentPackage.objects.filter(
            policy=policy,
            is_current=True
        ).first()
        
        if not package:
            return JsonResponse({
                'success': True,
                'package_status': 'no_package',
                'components': [],
                'package': None
            })
        
        # Get component statuses
        components = []
        for component in package.components.all().order_by('sequence_order'):
            components.append({
                'id': component.component_id,
                'name': component.component_name,
                'type': component.component_type,
                'status': component.component_status,
                'pages': component.page_count or 0,
                'file_size': component.file_size or 0,
                'generated_at': component.generated_at.isoformat() if component.generated_at else None,
                'error_message': getattr(component, 'error_message', None),
                'template_name': component.template.template_name if component.template else None,
                'sequence_order': component.sequence_order
            })
        
        return JsonResponse({
            'success': True,
            'package_status': package.package_status,
            'components': components,
            'package': {
                'id': package.package_id,
                'number': package.package_number,
                'total_pages': getattr(package, 'total_pages', 0),
                'file_size': getattr(package, 'file_size', 0),
                'generated_date': package.generated_date.isoformat() if getattr(package, 'generated_date', None) else None,
                'version': package.package_version
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting document status for policy {policy_id}: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'Error retrieving document status'
        }, status=500)

@login_required
@require_http_methods(["POST"])
def regenerate_component(request, policy_id, component_id):
    """Regenerate a single document component - API endpoint"""
    try:
        policy = get_object_or_404(Policy, policy_id=policy_id)
        component = get_object_or_404(
            DocumentComponent, 
            component_id=component_id, 
            package__policy=policy
        )
        
        # Use enhanced document service
        service = EnhancedDocumentService()
        success, error_msg = service.regenerate_component(component)
        
        if success:
            # Refresh component data
            component.refresh_from_db()
            return JsonResponse({
                'success': True,
                'message': f'Successfully regenerated {component.component_name}',
                'component': {
                    'id': component.component_id,
                    'name': component.component_name,
                    'status': component.component_status,
                    'pages': component.page_count or 0,
                    'file_size': component.file_size or 0,
                    'generated_at': component.generated_at.isoformat() if component.generated_at else None
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'message': f'Failed to regenerate component: {error_msg}'
            }, status=400)
            
    except Exception as e:
        logger.error(f"Error regenerating component {component_id}: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'An error occurred while regenerating the component'
        }, status=500)

@login_required
@require_http_methods(["POST"])
def generate_missing_documents(request, policy_id):
    """Generate all missing documents for a policy - API endpoint"""
    try:
        policy = get_object_or_404(Policy, policy_id=policy_id)
        
        # Use enhanced document service
        service = EnhancedDocumentService()
        result = service.generate_missing_documents(policy)
        
        return JsonResponse(result)
        
    except Exception as e:
        logger.error(f"Error generating missing documents for policy {policy_id}: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'An error occurred while generating missing documents'
        }, status=500)

@login_required
@require_http_methods(["POST"])
def bulk_document_generation(request):
    """Generate documents for multiple policies - API endpoint"""
    try:
        data = json.loads(request.body)
        policy_ids = data.get('policy_ids', [])
        generation_type = data.get('type', 'missing')
        
        if not policy_ids:
            return JsonResponse({
                'success': False,
                'message': 'No policies selected'
            }, status=400)
        
        # Convert string IDs to integers
        try:
            policy_ids = [int(pid) for pid in policy_ids]
        except (ValueError, TypeError):
            return JsonResponse({
                'success': False,
                'message': 'Invalid policy IDs provided'
            }, status=400)
        
        # Use enhanced document service
        service = EnhancedDocumentService()
        result = service.bulk_generate_documents(policy_ids, generation_type)
        
        return JsonResponse(result)
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        logger.error(f"Error in bulk document generation: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'An error occurred during bulk generation'
        }, status=500)

@login_required
@require_http_methods(["GET"])
def get_available_templates(request):
    """Get available templates - ALLOWS DUPLICATE COMPONENTS"""
    try:
        policy_id = request.GET.get('policy_id')
        template_type = request.GET.get('type')
        state_code = request.GET.get('state', 'CA')
        
        if not policy_id:
            return JsonResponse({
                'success': False,
                'message': 'Policy ID is required'
            }, status=400)
        
        # Get policy and product
        policy = get_object_or_404(Policy, policy_id=policy_id)
        templates = DocumentTemplate.objects.filter(
            Q(product=policy.quote.application.product) | Q(product__isnull=True),
            is_active=True
        )
        
        if template_type:
            templates = templates.filter(template_type=template_type)
        
        # Get existing components count (for reference only)
        existing_component_counts = {}
        current_package = PolicyDocumentPackage.objects.filter(
            policy=policy,
            is_current=True
        ).first()
        
        if current_package:
            from django.db.models import Count
            component_counts = current_package.components.values('template_id').annotate(
                count=Count('template_id')
            )
            existing_component_counts = {
                item['template_id']: item['count'] 
                for item in component_counts
            }
        
        # Build template list - ALLOW ALL TEMPLATES
        applicable_templates = []
        for template in templates.order_by('template_type', 'template_name'):
            # Check state applicability
            if hasattr(template, 'is_applicable_to_state'):
                if not template.is_applicable_to_state(state_code):
                    continue
            
            # Count how many times this template is already used
            usage_count = existing_component_counts.get(template.template_id, 0)
            usage_text = f" (Used {usage_count}x)" if usage_count > 0 else ""
            
            applicable_templates.append({
                'id': template.template_id,
                'name': template.template_name,
                'code': template.template_code,
                'type': template.template_type,
                'format': template.template_format,
                'description': f"{template.template_name} - {template.get_template_type_display()}{usage_text}",
                'has_file': bool(getattr(template, 'storage_path', None)),
                'usage_count': usage_count,
                'disabled': False  # NEVER DISABLE - allow duplicates
            })
        
        return JsonResponse({
            'success': True,
            'templates': applicable_templates,
            'total_count': len(applicable_templates),
            'debug': {
                'policy_id': policy_id,
                'total_active_templates': DocumentTemplate.objects.filter(is_active=True).count(),
                'product_templates': templates.count(),
                'existing_components': sum(existing_component_counts.values())
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting available templates: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'Error loading templates',
            'error': str(e)
        }, status=500)
        
    except Exception as e:
        logger.error(f"Error getting available templates: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'Error loading templates',
            'error': str(e)  # Include error for debugging
        }, status=500)

@login_required
@require_http_methods(["POST"])
def create_document_package(request, policy_id):
    """Create a document package for a policy - API endpoint"""
    try:
        policy = get_object_or_404(Policy, policy_id=policy_id)
        
        # Parse request data
        data = json.loads(request.body) if request.body else {}
        force_regenerate = data.get('force_regenerate', False)
        
        # Use enhanced document service
        service = EnhancedDocumentService()
        package = service.create_document_package(policy, force_regenerate)
        
        return JsonResponse({
            'success': True,
            'message': f'Document package created: {package.package_number}',
            'package': {
                'id': package.package_id,
                'number': package.package_number,
                'status': package.package_status,
                'version': package.package_version,
                'component_count': package.components.count(),
                'generated_count': package.components.filter(component_status='generated').count()
            }
        })
        
    except Exception as e:
        logger.error(f"Error creating document package for policy {policy_id}: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'Error creating document package: {str(e)}'
        }, status=500)

@login_required
@require_http_methods(["POST"])
def add_component(request, policy_id):
    """Add a new component to policy document package - ALLOWS DUPLICATES"""
    try:
        policy = get_object_or_404(Policy, policy_id=policy_id)
        
        data = json.loads(request.body)
        template_id = data.get('template_id')
        
        if not template_id:
            return JsonResponse({
                'success': False,
                'message': 'Template ID is required'
            }, status=400)
        
        template = get_object_or_404(DocumentTemplate, template_id=template_id)
        
        # Get current package
        package = PolicyDocumentPackage.objects.filter(
            policy=policy,
            is_current=True
        ).first()
        
        if not package:
            return JsonResponse({
                'success': False,
                'message': 'No document package found for this policy'
            }, status=400)
        
        # REMOVE the duplicate check - allow multiple components from same template
        # Count existing components of this type for naming
        existing_count = DocumentComponent.objects.filter(
            package=package,
            template=template
        ).count()
        
        # Create component name with sequence if duplicate
        if existing_count > 0:
            component_name = f"{template.template_name} ({existing_count + 1})"
        else:
            component_name = template.template_name
        
        # Get next sequence order
        max_sequence = package.components.aggregate(
            max_seq=Max('sequence_order')
        )['max_seq'] or 0
        
        # Create new component - ALWAYS ALLOW
        component = DocumentComponent.objects.create(
            package=package,
            template=template,
            component_type=template.template_type,
            component_name=component_name,  # Use the potentially modified name
            sequence_order=max_sequence + 1,
            component_status='pending'
        )
        
        logger.info(f"Created component {component.component_id}: {component_name} (Template: {template.template_code})")
        
        # Generate the component
        service = EnhancedDocumentService()
        success, error_msg = service.regenerate_component(component)
        
        if success:
            component.refresh_from_db()
            return JsonResponse({
                'success': True,
                'message': f'Component "{component_name}" added successfully',
                'component': {
                    'id': component.component_id,
                    'name': component.component_name,
                    'type': component.component_type,
                    'status': component.component_status,
                    'pages': component.page_count or 0,
                    'file_size': component.file_size or 0,
                    'sequence_order': component.sequence_order,
                    'template_name': template.template_name,
                    'template_code': template.template_code
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'message': f'Component created but generation failed: {error_msg}'
            }, status=400)
            
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        logger.error(f"Error adding component to policy {policy_id}: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'An error occurred while adding the component: {str(e)}'
        }, status=500)

@login_required
@require_http_methods(["POST"])
def delete_component(request, policy_id, component_id):
    """Delete a component from policy document package - API endpoint"""
    try:
        policy = get_object_or_404(Policy, policy_id=policy_id)
        component = get_object_or_404(
            DocumentComponent, 
            component_id=component_id, 
            package__policy=policy
        )
        
        component_name = component.component_name
        package = component.package
        
        # Delete associated file if exists
        if hasattr(component, 'file_path') and component.file_path:
            file_path = os.path.join(settings.MEDIA_ROOT, 'documents', component.file_path)
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except OSError:
                    logger.warning(f"Could not delete file: {file_path}")
        
        # Delete the component
        component.delete()
        
        # Update package status
        service = EnhancedDocumentService()
        service.update_package_status(package)
        
        return JsonResponse({
            'success': True,
            'message': f'Component "{component_name}" deleted successfully'
        })
        
    except Exception as e:
        logger.error(f"Error deleting component {component_id}: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'An error occurred while deleting the component'
        }, status=500)

@login_required
@require_http_methods(["GET"])
def get_bulk_policies(request):
    """Get policies for bulk operations - API endpoint"""
    try:
        search = request.GET.get('search', '')
        product_type = request.GET.get('product_type', '')
        status_filter = request.GET.get('status', '')
        
        policies = Policy.objects.select_related(
            'quote__application__company',
            'quote__application__product'
        ).all()
        
        if search:
            policies = policies.filter(
                Q(policy_number__icontains=search) |
                Q(quote__application__company__company_name__icontains=search)
            )
        
        if product_type:
            policies = policies.filter(
                quote__application__product__product_name__icontains=product_type
            )
        
        if status_filter:
            policies = policies.filter(policy_status=status_filter)
        
        policies = policies.order_by('-created_at')[:50]
        
        policy_data = []
        for policy in policies:
            # Get latest package status
            latest_package = PolicyDocumentPackage.objects.filter(
                policy=policy,
                is_current=True
            ).first()
            
            policy_data.append({
                'id': policy.policy_id,
                'policy_number': policy.policy_number,
                'insured_name': policy.quote.application.company.company_name,
                'product_type': policy.quote.application.product.product_name,
                'policy_status': policy.policy_status,
                'document_status': latest_package.package_status if latest_package else 'no_documents',
                'document_count': latest_package.components.count() if latest_package else 0,
                'last_generated': latest_package.generated_date.isoformat() if latest_package and getattr(latest_package, 'generated_date', None) else None
            })
        
        # Get statistics
        total_policies = Policy.objects.count()
        policies_with_docs = PolicyDocumentPackage.objects.filter(is_current=True).count()
        policies_without_docs = total_policies - policies_with_docs
        
        stats = {
            'total_policies': total_policies,
            'policies_with_documents': policies_with_docs,
            'policies_missing_documents': policies_without_docs,
            'total_documents': DocumentComponent.objects.filter(
                component_status='generated'
            ).count()
        }
        
        return JsonResponse({
            'success': True,
            'policies': policy_data,
            'stats': stats
        })
        
    except Exception as e:
        logger.error(f"Error getting bulk policies: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'Error loading policies'
        }, status=500)

# Existing functions continue below...

def download_policy_package(request, package_id):
    """Download policy PDF package - combines all components into one PDF"""
    package = get_object_or_404(PolicyDocumentPackage, package_id=package_id)
    
    try:
        # Check if combined PDF already exists
        combined_pdf_path = getattr(package, 'combined_pdf_path', None)
        if combined_pdf_path:
            file_path = os.path.join(settings.MEDIA_ROOT, 'documents', combined_pdf_path)
            if os.path.exists(file_path):
                # Return existing combined file
                response = FileResponse(
                    open(file_path, 'rb'),
                    content_type='application/pdf'
                )
                response['Content-Disposition'] = f'attachment; filename="{package.package_number}_Complete.pdf"'
                return response
        
        # Need to create combined PDF from components
        components = package.components.filter(
            component_status='generated'
        ).order_by('sequence_order')
        
        if not components.exists():
            messages.error(request, 'No generated components available for download.')
            return redirect('applications:view_policy_documents', policy_id=package.policy.policy_id)
        
        # Combine PDFs using PyPDF2 or similar
        combined_pdf = combine_component_pdfs(components)
        
        if combined_pdf:
            # Save combined PDF
            combined_filename = f"{package.package_number}_Complete_{timezone.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            combined_dir = os.path.join(settings.MEDIA_ROOT, 'documents', 'combined')
            os.makedirs(combined_dir, exist_ok=True)
            combined_file_path = os.path.join(combined_dir, combined_filename)
            
            with open(combined_file_path, 'wb') as output_file:
                output_file.write(combined_pdf)
            
            # Update package with combined PDF path
            if hasattr(package, 'combined_pdf_path'):
                package.combined_pdf_path = f'combined/{combined_filename}'
                package.save()
            
            # Return combined file
            response = FileResponse(
                open(combined_file_path, 'rb'),
                content_type='application/pdf'
            )
            response['Content-Disposition'] = f'attachment; filename="{package.package_number}_Complete.pdf"'
            return response
        else:
            messages.error(request, 'Failed to combine PDF components.')
            return redirect('applications:view_policy_documents', policy_id=package.policy.policy_id)
    
    except Exception as e:
        logger.error(f"Error downloading package {package_id}: {str(e)}")
        messages.error(request, f'Error downloading package: {str(e)}')
        return redirect('applications:view_policy_documents', policy_id=package.policy.policy_id)

def combine_component_pdfs(components):
    """Combine multiple PDF components into one PDF - FIXED to preserve headers"""
    try:
        from PyPDF2 import PdfWriter, PdfReader
        import io
        import os
        from django.conf import settings
        
        logger.info(f"Combining {len(components)} PDF components into package")
        
        writer = PdfWriter()
        total_pages_added = 0
        
        for component in components:
            if not hasattr(component, 'file_path') or not component.file_path:
                logger.warning(f"Component {component.component_name} has no file path, skipping")
                continue
                
            file_path = os.path.join(settings.MEDIA_ROOT, 'documents', component.file_path)
            if not os.path.exists(file_path):
                logger.warning(f"Component file not found: {file_path}, skipping")
                continue
            
            try:
                logger.info(f"Adding component: {component.component_name} ({component.component_type})")
                
                with open(file_path, 'rb') as pdf_file:
                    reader = PdfReader(pdf_file)
                    
                    # Add all pages from this component
                    pages_in_component = len(reader.pages)
                    for page_num, page in enumerate(reader.pages):
                        try:
                            # Create a copy of the page to avoid reference issues
                            writer.add_page(page)
                            total_pages_added += 1
                            
                            logger.debug(f"Added page {page_num + 1}/{pages_in_component} from {component.component_name}")
                            
                        except Exception as page_error:
                            logger.error(f"Error adding page {page_num + 1} from {component.component_name}: {str(page_error)}")
                            continue
                    
                    logger.info(f"Successfully added {pages_in_component} pages from {component.component_name}")
                    
            except Exception as component_error:
                logger.error(f"Error reading component PDF {component.component_name}: {str(component_error)}")
                continue
        
        if total_pages_added == 0:
            logger.error("No pages were successfully added to the combined PDF")
            return None
        
        # Write combined PDF to bytes
        output_buffer = io.BytesIO()
        writer.write(output_buffer)
        output_buffer.seek(0)
        
        logger.info(f"Successfully combined PDF with {total_pages_added} total pages")
        
        return output_buffer.getvalue()
        
    except ImportError:
        logger.error("PyPDF2 not available for PDF combining")
        # Fallback if PyPDF2 not available - use reportlab to create a simple combined document
        return create_simple_combined_pdf(components)
    except Exception as e:
        logger.error(f"Error combining PDFs: {str(e)}")
        return None

def create_simple_combined_pdf(components):
    """Create a simple combined PDF using reportlab as fallback - UPDATED"""
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        import io
        
        logger.info("Using fallback PDF creation method")
        
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        
        # Title page
        p.setFont("Helvetica-Bold", 20)
        p.drawString(72, 750, "Policy Document Package")
        
        y = 700
        p.setFont("Helvetica", 12)
        
        # List components
        p.drawString(72, y, "This package contains the following components:")
        y -= 30
        
        for i, component in enumerate(components, 1):
            p.drawString(90, y, f"{i}. {component.component_name}")
            y -= 20
            
            if hasattr(component, 'file_path') and component.file_path:
                file_path = os.path.join(settings.MEDIA_ROOT, 'documents', component.file_path)
                if os.path.exists(file_path):
                    p.drawString(110, y, f"✓ File available: {component.file_path}")
                else:
                    p.drawString(110, y, "✗ File not found")
            else:
                p.drawString(110, y, "✗ No file generated")
            
            y -= 25
            
            if y < 100:  # Start new page if needed
                p.showPage()
                y = 750
        
        p.showPage()
        p.save()
        
        buffer.seek(0)
        return buffer.getvalue()
        
    except Exception as e:
        logger.error(f"Error creating simple combined PDF: {str(e)}")
        return None

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

def document_dashboard(request):
    """Main dashboard for document management"""
    from datetime import timedelta
    
    # Get statistics
    total_templates = DocumentTemplate.objects.count()
    active_templates = DocumentTemplate.objects.filter(is_active=True).count()
    
    # Document packages statistics
    total_packages = PolicyDocumentPackage.objects.count()
    packages_this_month = PolicyDocumentPackage.objects.filter(
        generated_date__gte=timezone.now() - timedelta(days=30)
    ).count()
    
    # Endorsements statistics
    total_endorsements = EndorsementDocument.objects.count()
    
    # Recent activity - using generated_date instead of created_at
    recent_packages = PolicyDocumentPackage.objects.select_related('policy').order_by('-generated_date')[:5]
    
    # Recent endorsements - check if this model has created_at field
    try:
        recent_endorsements = EndorsementDocument.objects.select_related('policy').order_by('-created_at')[:5]
    except:
        # Fallback if EndorsementDocument doesn't have created_at
        recent_endorsements = EndorsementDocument.objects.select_related('policy').order_by('-endorsement_id')[:5]
    
    # Policies needing documents
    policies_without_docs = Policy.objects.filter(
        document_packages__isnull=True,
        policy_status='active'
    ).select_related('quote__application__company')[:10]
    
    context = {
        'total_templates': total_templates,
        'active_templates': active_templates,
        'total_packages': total_packages,
        'packages_this_month': packages_this_month,
        'total_endorsements': total_endorsements,
        'recent_packages': recent_packages,
        'recent_endorsements': recent_endorsements,
        'policies_without_docs': policies_without_docs,
    }
    
    return render(request, 'applications/document_dashboard.html', context)

# Enhanced Functions - Component Management (existing functions remain)

@login_required
@require_http_methods(["GET"])
def view_component(request, component_id):
    """View a document component PDF"""
    try:
        component = get_object_or_404(DocumentComponent, component_id=component_id)
        
        if component.component_status != 'generated' or not hasattr(component, 'file_path') or not component.file_path:
            return HttpResponse('Component not available', status=404)
        
        # Check if file exists
        full_path = os.path.join(settings.MEDIA_ROOT, 'documents', component.file_path)
        if not os.path.exists(full_path):
            return HttpResponse('File not found', status=404)
        
        # Serve PDF file
        with open(full_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/pdf')
            response['Content-Disposition'] = f'inline; filename="{component.component_name}.pdf"'
            return response
            
    except Exception as e:
        logger.error(f"Error viewing component {component_id}: {str(e)}")
        return HttpResponse('Error loading component', status=500)

@login_required
@require_http_methods(["POST"])
def replace_component_file(request, component_id):
    """Replace a component's file with uploaded file"""
    try:
        component = get_object_or_404(DocumentComponent, component_id=component_id)
        
        if 'file' not in request.FILES:
            return JsonResponse({
                'success': False,
                'message': 'No file provided'
            }, status=400)
        
        uploaded_file = request.FILES['file']
        
        # Validate file type
        if not uploaded_file.name.lower().endswith('.pdf'):
            return JsonResponse({
                'success': False,
                'message': 'Only PDF files are allowed'
            }, status=400)
        
        # Save uploaded file
        upload_dir = os.path.join(settings.MEDIA_ROOT, 'documents', 'uploads')
        os.makedirs(upload_dir, exist_ok=True)
        
        filename = f"{component.package.policy.policy_number}_{component.component_name}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        file_path = os.path.join(upload_dir, filename)
        
        with open(file_path, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)
        
        # Update component
        old_file_path = getattr(component, 'file_path', None)
        component.file_path = f'uploads/{filename}'
        component.file_size = uploaded_file.size
        component.component_status = 'generated'
        component.generated_at = timezone.now()
        component.save()
        
        # Remove old file if exists
        if old_file_path:
            old_full_path = os.path.join(settings.MEDIA_ROOT, 'documents', old_file_path)
            if os.path.exists(old_full_path):
                try:
                    os.remove(old_full_path)
                except OSError:
                    pass
        
        return JsonResponse({
            'success': True,
            'message': 'Component file replaced successfully',
            'component': {
                'id': component.component_id,
                'name': component.component_name,
                'status': component.component_status,
                'file_size': component.file_size,
                'generated_at': component.generated_at.isoformat() if component.generated_at else None
            }
        })
        
    except Exception as e:
        logger.error(f"Error replacing component file {component_id}: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'Error replacing component file'
        }, status=500)

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
        if hasattr(template, 'storage_path') and template.storage_path:
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
        service = EnhancedDocumentService()
        package = service.create_document_package(policy)
        
        messages.success(request, f'Documents generated! Package: {package.package_number}')
        return redirect('applications:view_policy_documents', policy_id=policy_id)
        
    except Exception as e:
        messages.error(request, f'Error: {str(e)}')
        return redirect('applications:policy_detail', policy_id=policy_id)

@login_required
@require_http_methods(["GET"])
def component_version_history(request, component_id):
    """Get version history for a component"""
    try:
        component = get_object_or_404(DocumentComponent, component_id=component_id)
        
        # For now, return basic info (you could expand this with a ComponentVersion model)
        history = [{
            'version': 1,
            'generated_at': component.generated_at.isoformat() if component.generated_at else None,
            'status': component.component_status,
            'file_size': getattr(component, 'file_size', 0) or 0,
            'page_count': getattr(component, 'page_count', 0) or 0,
            'created_by': 'System',
            'changes': 'Initial generation'
        }]
        
        return JsonResponse({
            'success': True,
            'component': {
                'id': component.component_id,
                'name': component.component_name,
                'type': component.component_type
            },
            'history': history
        })
        
    except Exception as e:
        logger.error(f"Error loading component history {component_id}: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'Error loading component history'
        }, status=500)

@login_required
@require_http_methods(["POST"])
def email_document_package(request, policy_id):
    """Email document package to recipients"""
    try:
        policy = get_object_or_404(Policy, policy_id=policy_id)
        data = json.loads(request.body)
        
        recipients = data.get('recipients', [])
        subject = data.get('subject', f'Policy Documents - {policy.policy_number}')
        message = data.get('message', 'Please find attached policy documents.')
        
        if not recipients:
            return JsonResponse({
                'success': False,
                'message': 'No recipients provided'
            }, status=400)
        
        # Get latest document package
        package = PolicyDocumentPackage.objects.filter(
            policy=policy,
            is_current=True,
            package_status='generated'
        ).first()
        
        if not package:
            return JsonResponse({
                'success': False,
                'message': 'No complete document package available'
            }, status=400)
        
        # TODO: Implement email sending logic
        # This would integrate with Django's email system
        
        # For now, return success (you'd implement actual email sending)
        return JsonResponse({
            'success': True,
            'message': f'Document package would be emailed to {len(recipients)} recipients (email not configured yet)'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        logger.error(f"Error sending email for policy {policy_id}: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'Error sending email'
        }, status=500)

@login_required
@require_http_methods(["POST"])
def generate_from_template(request):
    """Generate document from template with dynamic data - API endpoint"""
    try:
        data = json.loads(request.body)
        policy_id = data.get('policy_id')
        template_id = data.get('template_id')
        custom_data = data.get('data', {})
        
        if not policy_id or not template_id:
            return JsonResponse({
                'success': False,
                'message': 'Policy ID and Template ID are required'
            }, status=400)
        
        policy = get_object_or_404(Policy, policy_id=policy_id)
        template = get_object_or_404(DocumentTemplate, template_id=template_id)
        
        # Use enhanced document service
        service = EnhancedDocumentService()
        success, result = service.generate_from_template(policy, template, custom_data)
        
        if success:
            return JsonResponse({
                'success': True,
                'message': f'Successfully generated document from template: {template.template_name}',
                **result
            })
        else:
            return JsonResponse({
                'success': False,
                'message': f'Failed to generate document: {result.get("error", "Unknown error")}'
            }, status=400)
            
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        logger.error(f"Error generating document from template: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'An error occurred while generating the document'
        }, status=500)

def merge_document_packages(request, policy_id):
    """Merge multiple document packages"""
    try:
        policy = get_object_or_404(Policy, policy_id=policy_id)
        
        # This would implement package merging logic
        return JsonResponse({
            'success': True,
            'message': 'Document package merge feature coming soon'
        })
        
    except Exception as e:
        logger.error(f"Error merging packages for policy {policy_id}: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'Error merging packages'
        }, status=500)