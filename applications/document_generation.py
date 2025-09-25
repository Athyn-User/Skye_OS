# applications/document_generation.py

from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.utils import timezone
from django.conf import settings
import json
import logging
from typing import List, Dict, Optional

from .models import Policy, DocumentPackage, DocumentComponent, DocumentTemplate
from .document_service import DocumentService, PDFGenerator

logger = logging.getLogger(__name__)

@login_required
@require_http_methods(["POST"])
def regenerate_component(request, policy_id, component_id):
    """Regenerate a single document component"""
    try:
        policy = get_object_or_404(Policy, id=policy_id)
        component = get_object_or_404(DocumentComponent, id=component_id, package__policy=policy)
        
        # Get the latest document package
        package = component.package
        
        # Initialize document service
        doc_service = DocumentService()
        
        # Regenerate the specific component
        success, error_msg = doc_service.regenerate_component(component)
        
        if success:
            # Update component status
            component.status = 'generated'
            component.generated_at = timezone.now()
            component.save()
            
            # Update package status if needed
            doc_service.update_package_status(package)
            
            return JsonResponse({
                'success': True,
                'message': f'Successfully regenerated {component.component_name}',
                'component': {
                    'id': component.id,
                    'name': component.component_name,
                    'status': component.status,
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
    """Generate all missing documents for a policy"""
    try:
        policy = get_object_or_404(Policy, id=policy_id)
        
        # Get or create the latest document package
        package = DocumentPackage.objects.filter(
            policy=policy,
            status__in=['draft', 'partial', 'error']
        ).order_by('-created_at').first()
        
        if not package:
            # Create new package if none exists
            doc_service = DocumentService()
            package = doc_service.create_document_package(policy)
        
        # Find components that need generation
        missing_components = DocumentComponent.objects.filter(
            package=package,
            status__in=['pending', 'error']
        )
        
        if not missing_components.exists():
            return JsonResponse({
                'success': True,
                'message': 'No missing documents to generate',
                'generated_count': 0
            })
        
        # Generate missing components
        doc_service = DocumentService()
        results = []
        success_count = 0
        
        for component in missing_components:
            success, error_msg = doc_service.regenerate_component(component)
            
            if success:
                success_count += 1
                component.status = 'generated'
                component.generated_at = timezone.now()
                component.save()
            else:
                component.status = 'error'
                component.error_message = error_msg
                component.save()
            
            results.append({
                'component': component.component_name,
                'success': success,
                'error': error_msg if not success else None
            })
        
        # Update package status
        doc_service.update_package_status(package)
        
        return JsonResponse({
            'success': True,
            'message': f'Generated {success_count} of {len(results)} missing documents',
            'generated_count': success_count,
            'total_count': len(results),
            'results': results,
            'package_status': package.status
        })
        
    except Exception as e:
        logger.error(f"Error generating missing documents for policy {policy_id}: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'An error occurred while generating missing documents'
        }, status=500)

@login_required
@require_http_methods(["POST"])
def bulk_document_generation(request):
    """Generate documents for multiple policies"""
    try:
        data = json.loads(request.body)
        policy_ids = data.get('policy_ids', [])
        generation_type = data.get('type', 'missing')  # 'missing', 'all', 'regenerate'
        
        if not policy_ids:
            return JsonResponse({
                'success': False,
                'message': 'No policies selected'
            }, status=400)
        
        # Validate policies exist
        policies = Policy.objects.filter(id__in=policy_ids)
        if len(policies) != len(policy_ids):
            return JsonResponse({
                'success': False,
                'message': 'Some selected policies were not found'
            }, status=400)
        
        # Process each policy
        doc_service = DocumentService()
        results = []
        
        for policy in policies:
            try:
                if generation_type == 'all':
                    # Generate complete new package
                    package = doc_service.create_document_package(policy)
                    success_count = package.components.filter(status='generated').count()
                    total_count = package.components.count()
                    
                elif generation_type == 'regenerate':
                    # Regenerate all components in latest package
                    package = DocumentPackage.objects.filter(
                        policy=policy
                    ).order_by('-created_at').first()
                    
                    if package:
                        success_count = 0
                        components = package.components.all()
                        for component in components:
                            success, _ = doc_service.regenerate_component(component)
                            if success:
                                success_count += 1
                                component.status = 'generated'
                                component.generated_at = timezone.now()
                                component.save()
                        total_count = components.count()
                    else:
                        success_count = 0
                        total_count = 0
                        
                else:  # 'missing' - default
                    # Generate only missing documents
                    package = DocumentPackage.objects.filter(
                        policy=policy
                    ).order_by('-created_at').first()
                    
                    if not package:
                        package = doc_service.create_document_package(policy)
                    
                    missing_components = package.components.filter(
                        status__in=['pending', 'error']
                    )
                    
                    success_count = 0
                    for component in missing_components:
                        success, _ = doc_service.regenerate_component(component)
                        if success:
                            success_count += 1
                            component.status = 'generated'
                            component.generated_at = timezone.now()
                            component.save()
                    
                    total_count = missing_components.count()
                
                # Update package status
                if package:
                    doc_service.update_package_status(package)
                
                results.append({
                    'policy_id': policy.id,
                    'policy_number': policy.policy_number,
                    'success': True,
                    'generated_count': success_count,
                    'total_count': total_count,
                    'package_status': package.status if package else 'no_package'
                })
                
            except Exception as policy_error:
                logger.error(f"Error processing policy {policy.id}: {str(policy_error)}")
                results.append({
                    'policy_id': policy.id,
                    'policy_number': policy.policy_number,
                    'success': False,
                    'error': str(policy_error)
                })
        
        # Calculate summary
        successful_policies = len([r for r in results if r['success']])
        total_generated = sum([r.get('generated_count', 0) for r in results if r['success']])
        
        return JsonResponse({
            'success': True,
            'message': f'Processed {successful_policies} of {len(results)} policies',
            'successful_policies': successful_policies,
            'total_policies': len(results),
            'total_documents_generated': total_generated,
            'results': results
        })
        
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
@require_http_methods(["POST"])
def generate_from_template(request):
    """Generate document from template with dynamic data"""
    try:
        data = json.loads(request.body)
        policy_id = data.get('policy_id')
        template_id = data.get('template_id')
        custom_data = data.get('data', {})
        component_type = data.get('component_type', 'custom')
        
        if not policy_id or not template_id:
            return JsonResponse({
                'success': False,
                'message': 'Policy ID and Template ID are required'
            }, status=400)
        
        policy = get_object_or_404(Policy, id=policy_id)
        template = get_object_or_404(DocumentTemplate, id=template_id)
        
        # Get or create document package
        package = DocumentPackage.objects.filter(
            policy=policy,
            status__in=['draft', 'partial', 'complete']
        ).order_by('-created_at').first()
        
        if not package:
            doc_service = DocumentService()
            package = doc_service.create_document_package(policy)
        
        # Prepare data for template
        template_data = {
            'policy': {
                'policy_number': policy.policy_number,
                'effective_date': policy.effective_date.isoformat() if policy.effective_date else None,
                'expiration_date': policy.expiration_date.isoformat() if policy.expiration_date else None,
                'premium': str(policy.annual_premium) if policy.annual_premium else '0',
                'state_code': policy.state_code,
                'product_type': policy.product.name if policy.product else '',
            },
            'insured': {
                'name': policy.insured_name,
                'address': getattr(policy, 'insured_address', ''),
                'city': getattr(policy, 'insured_city', ''),
                'state': getattr(policy, 'insured_state', ''),
                'zip': getattr(policy, 'insured_zip', ''),
            },
            'custom': custom_data
        }
        
        # Generate document
        pdf_generator = PDFGenerator()
        success, result = pdf_generator.generate_from_template(
            template, 
            template_data, 
            f"{policy.policy_number}_{template.name}_{timezone.now().strftime('%Y%m%d_%H%M%S')}"
        )
        
        if success:
            # Create document component
            component = DocumentComponent.objects.create(
                package=package,
                component_name=f"{template.name} (Custom)",
                component_type=component_type,
                template=template,
                status='generated',
                file_path=result['file_path'],
                file_size=result.get('file_size', 0),
                page_count=result.get('page_count', 0),
                generated_at=timezone.now(),
                order_sequence=package.components.count() + 1
            )
            
            # Update package
            doc_service = DocumentService()
            doc_service.update_package_status(package)
            
            return JsonResponse({
                'success': True,
                'message': f'Successfully generated document from template: {template.name}',
                'component': {
                    'id': component.id,
                    'name': component.component_name,
                    'status': component.status,
                    'pages': component.page_count,
                    'file_size': component.file_size,
                    'generated_at': component.generated_at.isoformat()
                },
                'package_status': package.status
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

# Helper function for getting policy document statistics
def get_policy_document_stats(policy_ids: List[int]) -> Dict:
    """Get document statistics for multiple policies"""
    try:
        from django.db.models import Count, Q
        
        policies = Policy.objects.filter(id__in=policy_ids).prefetch_related(
            'document_packages__components'
        )
        
        stats = {
            'total_policies': len(policies),
            'policies_with_documents': 0,
            'policies_missing_documents': 0,
            'total_documents': 0,
            'documents_by_status': {
                'generated': 0,
                'pending': 0,
                'error': 0
            },
            'policies_by_status': {
                'complete': 0,
                'partial': 0,
                'missing': 0,
                'error': 0
            }
        }
        
        for policy in policies:
            latest_package = policy.document_packages.order_by('-created_at').first()
            
            if latest_package:
                stats['policies_with_documents'] += 1
                stats['total_documents'] += latest_package.components.count()
                
                # Count components by status
                component_counts = latest_package.components.values('status').annotate(
                    count=Count('id')
                )
                
                for item in component_counts:
                    status = item['status']
                    count = item['count']
                    if status in stats['documents_by_status']:
                        stats['documents_by_status'][status] += count
                
                # Determine policy status
                if latest_package.status == 'complete':
                    stats['policies_by_status']['complete'] += 1
                elif latest_package.status in ['partial', 'draft']:
                    stats['policies_by_status']['partial'] += 1
                elif latest_package.status == 'error':
                    stats['policies_by_status']['error'] += 1
            else:
                stats['policies_missing_documents'] += 1
                stats['policies_by_status']['missing'] += 1
        
        return stats
        
    except Exception as e:
        logger.error(f"Error getting policy document stats: {str(e)}")
        return {}