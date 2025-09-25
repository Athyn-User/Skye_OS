# File: applications/document_service.py
# Enhanced service building on your existing models - Fixed imports

from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Max  # Fixed: Added explicit Max import
from django.utils import timezone
from django.conf import settings
import json
import logging
import os
from typing import List, Dict, Optional, Tuple

from .models import Policy
from .document_models import (
    DocumentTemplate, PolicyDocumentPackage, DocumentComponent, 
    EndorsementDocument, DocumentDelivery
)

logger = logging.getLogger(__name__)

class EnhancedDocumentService:
    """Enhanced service building on your existing document models"""
    
    def __init__(self):
        self.media_root = getattr(settings, 'MEDIA_ROOT', '/tmp')
    
    def regenerate_component(self, component: DocumentComponent) -> Tuple[bool, Optional[str]]:
        """Regenerate a single document component"""
        try:
            # Update component status to pending
            component.component_status = 'pending'
            component.error_message = None
            component.save()
            
            # Generate the component based on its template
            if component.template:
                success, result = self._generate_from_template(component)
            else:
                success, result = self._generate_standard_component(component)
            
            if success:
                # Update component with generated file info
                component.file_path = result.get('file_path')
                component.file_size = result.get('file_size', 0)
                component.page_count = result.get('page_count', 0)
                component.component_status = 'generated'
                component.generated_at = timezone.now()
                component.error_message = None
            else:
                component.component_status = 'error'
                component.error_message = result.get('error', 'Generation failed')
            
            component.save()
            
            # Update package status
            self.update_package_status(component.package)
            
            return success, component.error_message
            
        except Exception as e:
            error_msg = f"Error regenerating component {component.component_id}: {str(e)}"
            logger.error(error_msg)
            component.component_status = 'error'
            component.error_message = error_msg
            component.save()
            return False, error_msg
    
    def generate_missing_documents(self, policy: Policy) -> Dict:
        """Generate all missing documents for a policy"""
        try:
            # Get or create the latest document package
            package = PolicyDocumentPackage.objects.filter(
                policy=policy,
                is_current=True
            ).first()
            
            if not package:
                # Create new package
                package = self.create_document_package(policy)
            
            # Find components that need generation
            missing_components = DocumentComponent.objects.filter(
                package=package,
                component_status__in=['pending', 'error']
            )
            
            if not missing_components.exists():
                return {
                    'success': True,
                    'message': 'No missing documents to generate',
                    'generated_count': 0,
                    'total_count': 0
                }
            
            # Generate missing components
            results = []
            success_count = 0
            
            for component in missing_components:
                success, error_msg = self.regenerate_component(component)
                
                if success:
                    success_count += 1
                
                results.append({
                    'component': component.component_name,
                    'success': success,
                    'error': error_msg if not success else None
                })
            
            # Update package status
            self.update_package_status(package)
            
            return {
                'success': True,
                'message': f'Generated {success_count} of {len(results)} missing documents',
                'generated_count': success_count,
                'total_count': len(results),
                'results': results,
                'package_status': package.package_status
            }
            
        except Exception as e:
            logger.error(f"Error generating missing documents for policy {policy.policy_id}: {str(e)}")
            return {
                'success': False,
                'message': f'Error generating missing documents: {str(e)}'
            }
    
    def bulk_generate_documents(self, policy_ids: List[int], generation_type: str = 'missing') -> Dict:
        """Generate documents for multiple policies"""
        try:
            # Validate policies exist
            policies = Policy.objects.filter(policy_id__in=policy_ids)
            if len(policies) != len(policy_ids):
                return {
                    'success': False,
                    'message': 'Some selected policies were not found'
                }
            
            # Process each policy
            results = []
            
            for policy in policies:
                try:
                    if generation_type == 'all':
                        # Generate complete new package
                        package = self.create_document_package(policy, force_regenerate=True)
                        success_count = package.components.filter(component_status='generated').count()
                        total_count = package.components.count()
                        
                    elif generation_type == 'regenerate':
                        # Regenerate all components in latest package
                        package = PolicyDocumentPackage.objects.filter(
                            policy=policy,
                            is_current=True
                        ).first()
                        
                        if package:
                            success_count = 0
                            components = package.components.all()
                            for component in components:
                                success, _ = self.regenerate_component(component)
                                if success:
                                    success_count += 1
                            total_count = components.count()
                        else:
                            success_count = 0
                            total_count = 0
                            
                    else:  # 'missing' - default
                        result = self.generate_missing_documents(policy)
                        success_count = result.get('generated_count', 0)
                        total_count = result.get('total_count', 0)
                        package = PolicyDocumentPackage.objects.filter(
                            policy=policy,
                            is_current=True
                        ).first()
                    
                    results.append({
                        'policy_id': policy.policy_id,
                        'policy_number': policy.policy_number,
                        'success': True,
                        'generated_count': success_count,
                        'total_count': total_count,
                        'package_status': package.package_status if package else 'no_package'
                    })
                    
                except Exception as policy_error:
                    logger.error(f"Error processing policy {policy.policy_id}: {str(policy_error)}")
                    results.append({
                        'policy_id': policy.policy_id,
                        'policy_number': policy.policy_number,
                        'success': False,
                        'error': str(policy_error)
                    })
            
            # Calculate summary
            successful_policies = len([r for r in results if r['success']])
            total_generated = sum([r.get('generated_count', 0) for r in results if r['success']])
            
            return {
                'success': True,
                'message': f'Processed {successful_policies} of {len(results)} policies',
                'successful_policies': successful_policies,
                'total_policies': len(results),
                'total_documents_generated': total_generated,
                'results': results
            }
            
        except Exception as e:
            logger.error(f"Error in bulk document generation: {str(e)}")
            return {
                'success': False,
                'message': f'Error during bulk generation: {str(e)}'
            }
    
    def generate_from_template(self, policy: Policy, template: DocumentTemplate, custom_data: Dict = None) -> Tuple[bool, Dict]:
        """Generate document from template with dynamic data"""
        try:
            # Get or create document package
            package = PolicyDocumentPackage.objects.filter(
                policy=policy,
                is_current=True
            ).first()
            
            if not package:
                package = self.create_document_package(policy)
            
            # Prepare template data
            template_data = self._prepare_template_data(policy, template, custom_data or {})
            
            # Generate document
            success, result = self._generate_document_from_template(template, template_data, policy)
            
            if success:
                # Create document component
                component = DocumentComponent.objects.create(
                    package=package,
                    template=template,
                    component_type=template.template_type,
                    component_name=f"{template.template_name} (Custom)",
                    sequence_order=package.components.count() + 1,
                    file_path=result['file_path'],
                    file_size=result.get('file_size', 0),
                    page_count=result.get('page_count', 0),
                    component_status='generated',
                    component_data=template_data,
                    generated_at=timezone.now()
                )
                
                # Update package
                self.update_package_status(package)
                
                return True, {
                    'component': {
                        'id': component.component_id,
                        'name': component.component_name,
                        'status': component.component_status,
                        'pages': component.page_count,
                        'file_size': component.file_size,
                        'generated_at': component.generated_at.isoformat()
                    },
                    'package_status': package.package_status
                }
            else:
                return False, result
                
        except Exception as e:
            logger.error(f"Error generating from template: {str(e)}")
            return False, {'error': str(e)}
    
    def create_document_package(self, policy: Policy, force_regenerate: bool = False) -> PolicyDocumentPackage:
        """Create a complete document package for a policy"""
        try:
            # Check if we should create new package
            if not force_regenerate:
                existing_package = PolicyDocumentPackage.objects.filter(
                    policy=policy,
                    is_current=True,
                    package_status__in=['draft', 'generated']
                ).first()
                
                if existing_package:
                    return existing_package
            
            # Mark old packages as not current
            PolicyDocumentPackage.objects.filter(
                policy=policy
            ).update(is_current=False)
            
            # Determine package version
            latest_version = PolicyDocumentPackage.objects.filter(
                policy=policy
            ).aggregate(max_version=Max('package_version'))['max_version'] or 0
            
            new_version = latest_version + 1 if force_regenerate else latest_version
            
            # Create new package
            package = PolicyDocumentPackage.objects.create(
                policy=policy,
                package_number=self._generate_package_number(policy, new_version),
                package_version=new_version,
                package_status='draft',
                is_current=True,
                state_code=getattr(policy, 'state_code', 'CA'),
                created_by=None  # Set from request context if available
            )
            
            # Create standard components
            self._create_standard_components(package)
            
            # Generate all components
            self._generate_all_components(package)
            
            # Update package status
            self.update_package_status(package)
            
            return package
            
        except Exception as e:
            logger.error(f"Error creating document package for policy {policy.policy_id}: {str(e)}")
            raise
    
    def update_package_status(self, package: PolicyDocumentPackage):
        """Update package status based on component statuses"""
        try:
            components = package.components.all()
            if not components.exists():
                package.package_status = 'draft'
                package.save()
                return
            
            component_statuses = list(components.values_list('component_status', flat=True))
            
            if all(status == 'generated' for status in component_statuses):
                package.package_status = 'generated'
                package.total_pages = sum([c.page_count or 0 for c in components])
                package.file_size = sum([c.file_size or 0 for c in components])
            elif any(status == 'generated' for status in component_statuses):
                package.package_status = 'draft'  # Partial generation
                package.total_pages = sum([c.page_count or 0 for c in components if c.component_status == 'generated'])
                package.file_size = sum([c.file_size or 0 for c in components if c.component_status == 'generated'])
            else:
                package.package_status = 'draft'
            
            package.save()
            
        except Exception as e:
            logger.error(f"Error updating package status {package.package_id}: {str(e)}")
    
    def _generate_package_number(self, policy: Policy, version: int) -> str:
        """Generate package number"""
        base = policy.policy_number
        if version == 0:
            return f"{base}-DOC"
        else:
            return f"{base}-DOC-{version:02d}"
    
    def _create_standard_components(self, package: PolicyDocumentPackage):
        """Create standard document components based on policy product"""
        try:
            policy = package.policy
            product = policy.quote.application.product
            
            # Get applicable templates for this product and state
            templates = DocumentTemplate.objects.filter(
                product=product,
                is_active=True
            ).order_by('default_sequence')
            
            # Filter by state if applicable
            state_code = getattr(policy, 'state_code', 'CA')  # Default to CA
            applicable_templates = []
            
            for template in templates:
                # Check if template has is_applicable_to_state method
                if hasattr(template, 'is_applicable_to_state'):
                    if template.is_applicable_to_state(state_code):
                        applicable_templates.append(template)
                else:
                    # Default behavior - include all templates
                    applicable_templates.append(template)
            
            # Create components for each template
            for idx, template in enumerate(applicable_templates, 1):
                DocumentComponent.objects.create(
                    package=package,
                    template=template,
                    component_type=template.template_type,
                    component_name=template.template_name,
                    sequence_order=idx,
                    component_status='pending'
                )
                
        except Exception as e:
            logger.error(f"Error creating standard components for package {package.package_id}: {str(e)}")
            raise
    
    def _generate_all_components(self, package: PolicyDocumentPackage):
        """Generate all components in a package"""
        try:
            components = package.components.filter(component_status='pending').order_by('sequence_order')
            
            for component in components:
                try:
                    success, _ = self.regenerate_component(component)
                    # Component status is updated in regenerate_component
                except Exception as e:
                    logger.error(f"Error generating component {component.component_id}: {str(e)}")
                    component.component_status = 'error'
                    component.error_message = str(e)
                    component.save()
                    
        except Exception as e:
            logger.error(f"Error generating components for package {package.package_id}: {str(e)}")
    
    def _generate_from_template(self, component: DocumentComponent) -> Tuple[bool, Dict]:
        """Generate document from template"""
        try:
            template = component.template
            policy = component.package.policy
            
            # Prepare template data
            template_data = self._prepare_template_data(policy, template)
            
            # Generate based on template format
            if template.template_format == 'dynamic':
                return self._generate_dynamic_document(template, template_data, policy)
            elif template.template_format == 'static':
                return self._generate_static_document(template, template_data, policy)
            elif template.template_format == 'hybrid':
                return self._generate_hybrid_document(template, template_data, policy)
            else:
                return False, {'error': f'Unknown template format: {template.template_format}'}
                
        except Exception as e:
            logger.error(f"Error generating from template for component {component.component_id}: {str(e)}")
            return False, {'error': str(e)}
    
    def _generate_standard_component(self, component: DocumentComponent) -> Tuple[bool, Dict]:
        """Generate document using standard logic without template"""
        try:
            policy = component.package.policy
            
            # Generate a basic PDF with policy information
            return self._generate_basic_pdf(policy, component.component_name)
            
        except Exception as e:
            logger.error(f"Error generating standard component {component.component_id}: {str(e)}")
            return False, {'error': str(e)}
    
    def _prepare_template_data(self, policy: Policy, template: DocumentTemplate, custom_data: Dict = None) -> Dict:
        """Prepare data for template rendering"""
        try:
            data = {
                'policy': {
                    'policy_number': policy.policy_number,
                    'effective_date': policy.effective_date,
                    'expiration_date': policy.expiration_date,
                    'annual_premium': policy.annual_premium,
                    'policy_status': policy.policy_status,
                },
                'application': {
                    'company_name': policy.quote.application.company.company_name,
                    'product_name': policy.quote.application.product.product_name,
                },
                'quote': {
                    'quote_number': policy.quote.quote_number,
                    'total_premium': policy.quote.total_premium,
                    'effective_date': policy.quote.effective_date,
                    'expiration_date': policy.quote.expiration_date,
                },
                'template': {
                    'name': template.template_name,
                    'code': template.template_code,
                    'type': template.template_type,
                },
                'generated_date': timezone.now(),
                'custom': custom_data or {}
            }
            
            return data
            
        except Exception as e:
            logger.error(f"Error preparing template data: {str(e)}")
            return {}
    
    def _generate_dynamic_document(self, template: DocumentTemplate, data: Dict, policy: Policy) -> Tuple[bool, Dict]:
        """Generate dynamic document using HTML template"""
        # Implement dynamic document generation
        # For now, return a placeholder
        return self._generate_basic_pdf(policy, template.template_name)
    
    def _generate_static_document(self, template: DocumentTemplate, data: Dict, policy: Policy) -> Tuple[bool, Dict]:
        """Generate static document by copying PDF template"""
        try:
            if not hasattr(template, 'storage_path') or not template.storage_path:
                return False, {'error': 'Template has no file'}
            
            # Get source file
            source_path = os.path.join(self.media_root, 'documents', template.storage_path)
            if not os.path.exists(source_path):
                return False, {'error': 'Template file not found'}
            
            # Create destination path
            filename = f"{policy.policy_number}_{template.template_code}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            dest_dir = os.path.join(self.media_root, 'documents', 'generated')
            os.makedirs(dest_dir, exist_ok=True)
            dest_path = os.path.join(dest_dir, filename)
            
            # Copy file (in production, you'd fill form fields here)
            import shutil
            shutil.copy2(source_path, dest_path)
            
            # Get file info
            file_size = os.path.getsize(dest_path)
            
            return True, {
                'file_path': f'generated/{filename}',
                'file_size': file_size,
                'page_count': 1  # You'd calculate this from the PDF
            }
            
        except Exception as e:
            logger.error(f"Error generating static document: {str(e)}")
            return False, {'error': str(e)}
    
    def _generate_hybrid_document(self, template: DocumentTemplate, data: Dict, policy: Policy) -> Tuple[bool, Dict]:
        """Generate hybrid document (fillable PDF)"""
        # Implement hybrid document generation
        # For now, fall back to static
        return self._generate_static_document(template, data, policy)
    
    def _generate_basic_pdf(self, policy: Policy, document_name: str) -> Tuple[bool, Dict]:
        """Generate basic PDF with policy information"""
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter
            import io
            
            # Create PDF buffer
            buffer = io.BytesIO()
            p = canvas.Canvas(buffer, pagesize=letter)
            
            # Add content
            p.setFont("Helvetica-Bold", 16)
            p.drawString(72, 750, document_name)
            
            p.setFont("Helvetica", 12)
            y = 700
            
            # Policy details
            details = [
                f"Policy Number: {policy.policy_number}",
                f"Insured: {policy.quote.application.company.company_name}",
                f"Product: {policy.quote.application.product.product_name}",
                f"Effective Date: {policy.effective_date}",
                f"Expiration Date: {policy.expiration_date}",
                f"Annual Premium: ${policy.annual_premium:,.2f}",
                f"Status: {policy.get_policy_status_display()}",
            ]
            
            for detail in details:
                p.drawString(72, y, detail)
                y -= 20
            
            # Finish PDF
            p.showPage()
            p.save()
            
            # Save to file
            pdf_content = buffer.getvalue()
            buffer.close()
            
            filename = f"{policy.policy_number}_{document_name.replace(' ', '_')}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            dest_dir = os.path.join(self.media_root, 'documents', 'generated')
            os.makedirs(dest_dir, exist_ok=True)
            dest_path = os.path.join(dest_dir, filename)
            
            with open(dest_path, 'wb') as f:
                f.write(pdf_content)
            
            return True, {
                'file_path': f'generated/{filename}',
                'file_size': len(pdf_content),
                'page_count': 1
            }
            
        except Exception as e:
            logger.error(f"Error generating basic PDF: {str(e)}")
            return False, {'error': str(e)}
    
    def _generate_document_from_template(self, template: DocumentTemplate, data: Dict, policy: Policy) -> Tuple[bool, Dict]:
        """Generate document from template with data"""
        # This would be implemented based on your template format
        # For now, use basic generation
        return self._generate_basic_pdf(policy, template.template_name)