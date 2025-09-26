# File: applications/document_service.py
# Enhanced service building on your existing models - Complete file with PDF overlay support

from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Max
from django.utils import timezone
from django.conf import settings
from django.template import Template, Context
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
    
    # Standard header template for ALL endorsements
    STANDARD_ENDORSEMENT_HEADER = """
    <div class="endorsement-header" style="page-break-inside: avoid; margin-bottom: 20px;">
        <table style="width: 100%; border-collapse: collapse; font-family: Arial, sans-serif; font-size: 11px;">
            <tr>
                <td style="width: 60%; padding: 12px; border: 2px solid black; vertical-align: top;">
                    <strong style="font-size: 12px;">NAMED INSURED:</strong><br>
                    {{ named_insured.company_name }}<br>
                    {{ named_insured.address }}<br>
                    {{ named_insured.city }}, {{ named_insured.state }} {{ named_insured.zip_code }}
                </td>
                <td style="width: 40%; padding: 12px; border: 2px solid black; vertical-align: top;">
                    <div style="margin-bottom: 8px;">
                        <strong>POLICY NUMBER:</strong><br>
                        {{ policy_number }}
                    </div>
                    <div style="margin-bottom: 8px;">
                        <strong>ENDORSEMENT NUMBER:</strong><br>
                        {{ endorsement_number }}
                    </div>
                    <div>
                        <strong>ENDORSEMENT EFFECTIVE DATE:</strong><br>
                        {{ endorsement_effective_date }}
                    </div>
                </td>
            </tr>
        </table>
    </div>
    """
    
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
    
    def _generate_endorsement_number(self, policy: Policy, template: DocumentTemplate) -> str:
        """Generate unique endorsement number for this policy"""
        try:
            # Count existing endorsement components for this policy
            package = PolicyDocumentPackage.objects.filter(
                policy=policy,
                is_current=True
            ).first()
            
            if package:
                endorsement_count = package.components.filter(
                    template__template_type='endorsement'
                ).count()
            else:
                endorsement_count = 0
            
            # Generate endorsement number: END-COM-000003-01, END-COM-000003-02, etc.
            base_number = policy.policy_number.replace('POL-', 'END-')
            return f"{base_number}-{endorsement_count + 1:02d}"
            
        except Exception as e:
            logger.error(f"Error generating endorsement number: {str(e)}")
            return f"END-{timezone.now().strftime('%Y%m%d')}-001"
    
    def _prepare_template_data(self, policy: Policy, template: DocumentTemplate, custom_data: Dict = None) -> Dict:
        """Prepare data for template rendering - UPDATED for endorsement headers and location schedules"""
        try:
            # Get company information
            company = policy.quote.application.company
            
            # Base template data
            data = {
                'policy': {
                    'policy_number': policy.policy_number,
                    'effective_date': policy.effective_date,
                    'expiration_date': policy.expiration_date,
                    'annual_premium': policy.annual_premium,
                    'policy_status': policy.policy_status,
                },
                'application': {
                    'company_name': company.company_name,
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
            
            # ADD endorsement-specific data if this is an endorsement
            if template.template_type == 'endorsement':
                # Generate endorsement number
                endorsement_number = self._generate_endorsement_number(policy, template)
                
                data.update({
                    # Standard endorsement header variables
                    'named_insured': {
                        'company_name': company.company_name,
                        'address': getattr(company, 'address', 'Address on file'),
                        'city': getattr(company, 'city', 'City on file'),
                        'state': getattr(company, 'state', 'State on file'),
                        'zip_code': getattr(company, 'zip_code', 'ZIP on file')
                    },
                    'policy_number': policy.policy_number,
                    'endorsement_number': endorsement_number,
                    'endorsement_effective_date': timezone.now().strftime('%B %d, %Y'),
                    
                    # Additional endorsement context
                    'endorsement_title': template.template_name,
                    'endorsement_description': custom_data.get('description', '') if custom_data else '',
                    
                    # LOCATION SCHEDULE DATA - NEW
                    'location_schedule': self._prepare_location_schedule_data(policy, template, custom_data),
                })
            
            return data
            
        except Exception as e:
            logger.error(f"Error preparing template data: {str(e)}")
            return {}
    
    def _prepare_location_schedule_data(self, policy: Policy, template: DocumentTemplate, custom_data: Dict = None) -> Dict:
        """Prepare location schedule data for endorsements"""
        try:
            from .location_models import LocationSchedule, LocationScheduleItem
            
            location_data = {
                'has_schedule': False,
                'schedule_id': None,
                'schedule_name': '',
                'locations': [],
                'totals': {
                    'total_locations': 0,
                    'total_building_limit': 0,
                    'total_contents_limit': 0,
                    'total_combined_limit': 0,
                }
            }
            
            # Check if this is a location schedule endorsement
            is_location_endorsement = (
                'LOCATION' in template.template_code.upper() or 
                'SCHEDULE' in template.template_code.upper() or
                (custom_data and custom_data.get('schedule_id'))
            )
            
            if not is_location_endorsement:
                return location_data
            
            # Get specific schedule if provided
            if custom_data and custom_data.get('schedule_id'):
                try:
                    schedule = LocationSchedule.objects.get(
                        schedule_id=custom_data['schedule_id'],
                        policy=policy
                    )
                except LocationSchedule.DoesNotExist:
                    logger.warning(f"Schedule {custom_data.get('schedule_id')} not found for policy {policy.policy_id}")
                    return location_data
            else:
                # Get or create a default "All Locations" schedule
                schedule, created = LocationSchedule.objects.get_or_create(
                    policy=policy,
                    schedule_name='All Locations Schedule',
                    defaults={
                        'schedule_type': 'all_locations',
                        'show_building_limits': True,
                        'show_contents_limits': True,
                    }
                )
                
                if created:
                    schedule.add_locations_by_criteria()
            
            # Get schedule items with location details
            schedule_items = schedule.items.select_related('location').filter(
                location__is_active=True
            ).order_by('sequence_order')
            
            locations = []
            total_building = 0
            total_contents = 0
            
            for item in schedule_items:
                location = item.location
                building_limit = location.building_limit or 0
                contents_limit = location.contents_limit or 0
                
                location_info = {
                    'location_number': location.location_number,
                    'location_name': location.location_name or '',
                    'full_address': location.full_address,
                    'street_address': location.street_address,
                    'city': location.city,
                    'state': location.state,
                    'zip_code': location.zip_code,
                    'building_limit': building_limit,
                    'contents_limit': contents_limit,
                    'total_limit': building_limit + contents_limit,
                    'building_limit_formatted': f"${building_limit:,.0f}" if building_limit > 0 else "None",
                    'contents_limit_formatted': f"${contents_limit:,.0f}" if contents_limit > 0 else "None",
                    'total_limit_formatted': f"${building_limit + contents_limit:,.0f}",
                    'effective_date': location.effective_date,
                    'construction_type': location.get_construction_type_display() if location.construction_type else '',
                    'occupancy': location.get_primary_occupancy_display() if location.primary_occupancy else '',
                }
                
                locations.append(location_info)
                total_building += building_limit
                total_contents += contents_limit
            
            location_data.update({
                'has_schedule': True,
                'schedule_id': schedule.schedule_id,
                'schedule_name': schedule.schedule_name,
                'schedule_type': schedule.get_schedule_type_display(),
                'locations': locations,
                'totals': {
                    'total_locations': len(locations),
                    'total_building_limit': total_building,
                    'total_contents_limit': total_contents,
                    'total_combined_limit': total_building + total_contents,
                    'total_building_formatted': f"${total_building:,.0f}",
                    'total_contents_formatted': f"${total_contents:,.0f}",
                    'total_combined_formatted': f"${total_building + total_contents:,.0f}",
                },
                'display_options': {
                    'show_building_limits': schedule.show_building_limits,
                    'show_contents_limits': schedule.show_contents_limits,
                    'show_deductibles': schedule.show_deductibles,
                    'show_construction_details': schedule.show_construction_details,
                }
            })
            
            logger.info(f"Prepared location schedule data: {len(locations)} locations, ${total_building + total_contents:,.0f} total limits")
            
            return location_data
            
        except Exception as e:
            logger.error(f"Error preparing location schedule data: {str(e)}")
            return location_data
    
    def _generate_from_template(self, component: DocumentComponent) -> Tuple[bool, Dict]:
        """Generate document from template - UPDATED for endorsement headers"""
        try:
            template = component.template
            policy = component.package.policy
            
            # Prepare template data (now includes endorsement headers if applicable)
            template_data = self._prepare_template_data(policy, template)
            
            # Log which generation method will be used
            logger.info(f"Generating {template.template_type} component '{component.component_name}' using {template.template_format} format")
            
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
            
            # Create minimal template data for endorsement detection
            template_data = None
            if component.component_type == 'endorsement':
                # Create a fake template for endorsement number generation
                fake_template = type('obj', (object,), {
                    'template_name': component.component_name,
                    'template_code': f"END-{component.component_type.upper()}",
                    'template_type': 'endorsement'
                })
                template_data = self._prepare_template_data(policy, fake_template)
            
            # Generate PDF with potential endorsement headers
            return self._generate_basic_pdf(policy, component.component_name, template_data)
            
        except Exception as e:
            logger.error(f"Error generating standard component {component.component_id}: {str(e)}")
            return False, {'error': str(e)}
    
    def _generate_dynamic_document(self, template: DocumentTemplate, data: Dict, policy: Policy) -> Tuple[bool, Dict]:
        """Generate dynamic document using HTML template"""
        # For now, use basic PDF generation with data
        return self._generate_basic_pdf(policy, template.template_name, data)
    
    def _generate_static_document(self, template: DocumentTemplate, data: Dict, policy: Policy) -> Tuple[bool, Dict]:
        """Generate static document by copying PDF template"""
        try:
            if not hasattr(template, 'storage_path') or not template.storage_path:
                return False, {'error': 'Template has no file'}
            
            # Get source file
            source_path = os.path.join(self.media_root, 'documents', template.storage_path)
            if not os.path.exists(source_path):
                return False, {'error': 'Template file not found'}
            
            # For endorsements with static format, overlay header
            if template.template_type == 'endorsement' and 'endorsement_number' in data:
                return self._add_header_to_pdf(source_path, data, policy, template)
            else:
                # For non-endorsements, just copy the file
                return self._copy_static_pdf(source_path, policy, template)
            
        except Exception as e:
            logger.error(f"Error generating static document: {str(e)}")
            return False, {'error': str(e)}
    
    def _generate_hybrid_document(self, template: DocumentTemplate, data: Dict, policy: Policy) -> Tuple[bool, Dict]:
        """Generate hybrid document (fillable PDF) - UPDATED with header overlay"""
        try:
            logger.info(f"Processing hybrid template: {template.template_code} (Type: {template.template_type})")
            
            # Check if template has a PDF file
            if not hasattr(template, 'storage_path') or not template.storage_path:
                logger.info(f"No PDF file for template {template.template_code}, generating basic PDF")
                return self._generate_basic_pdf(policy, template.template_name, data)
            
            template_file = os.path.join(self.media_root, 'documents', template.storage_path)
            if not os.path.exists(template_file):
                logger.warning(f"Template PDF file not found: {template_file}")
                return self._generate_basic_pdf(policy, template.template_name, data)
            
            # FOR ENDORSEMENTS: Add header overlay to existing PDF
            if template.template_type == 'endorsement' and 'endorsement_number' in data:
                logger.info(f"Adding endorsement header to existing PDF: {template.template_code}")
                return self._add_header_to_pdf(template_file, data, policy, template)
            else:
                # For non-endorsements, just copy the file
                logger.info(f"Copying static PDF without modifications: {template.template_code}")
                return self._copy_static_pdf(template_file, policy, template)
                
        except Exception as e:
            logger.error(f"Error generating hybrid document: {str(e)}")
            return False, {'error': str(e)}
    
    def _add_header_to_pdf(self, template_file_path: str, data: Dict, policy: Policy, template: DocumentTemplate) -> Tuple[bool, Dict]:
        """Add endorsement header to existing PDF file"""
        try:
            # Try to use PyPDF2 to overlay header on existing PDF
            try:
                return self._overlay_header_with_pypdf(template_file_path, data, policy, template)
            except ImportError:
                logger.warning("PyPDF2 not available, generating new PDF with header instead")
                return self._generate_basic_pdf(policy, template.template_name, data)
                
        except Exception as e:
            logger.error(f"Error adding header to PDF: {str(e)}")
            return False, {'error': str(e)}
    
    def _overlay_header_with_pypdf(self, template_file_path: str, data: Dict, policy: Policy, template: DocumentTemplate) -> Tuple[bool, Dict]:
        """Overlay header using PyPDF2"""
        try:
            from PyPDF2 import PdfReader, PdfWriter
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter
            from reportlab.lib.units import inch
            from reportlab.lib import colors
            import io
            
            logger.info(f"Overlaying header on PDF: {template_file_path}")
            
            # Create header overlay PDF
            header_buffer = io.BytesIO()
            header_canvas = canvas.Canvas(header_buffer, pagesize=letter)
            
            # Draw header box at top of page
            header_canvas.setStrokeColor(colors.black)
            header_canvas.setFillColor(colors.white)
            header_canvas.setLineWidth(2)
            
            # Header box coordinates (top of page)
            x_start = 50
            y_start = 720  # Near top of 8.5x11 page
            box_width = 500
            box_height = 100
            
            # Draw header table background
            header_canvas.rect(x_start, y_start, box_width, box_height, fill=1, stroke=1)
            
            # Add vertical divider
            header_canvas.line(x_start + 300, y_start, x_start + 300, y_start + box_height)
            
            # Add text content
            header_canvas.setFillColor(colors.black)
            header_canvas.setFont("Helvetica-Bold", 10)
            
            # Left side - Named Insured
            header_canvas.drawString(x_start + 10, y_start + 75, "NAMED INSURED:")
            header_canvas.setFont("Helvetica", 9)
            header_canvas.drawString(x_start + 10, y_start + 60, data['named_insured']['company_name'])
            header_canvas.drawString(x_start + 10, y_start + 45, data['named_insured']['address'])
            header_canvas.drawString(x_start + 10, y_start + 30, f"{data['named_insured']['city']}, {data['named_insured']['state']} {data['named_insured']['zip_code']}")
            
            # Right side - Policy Info
            header_canvas.setFont("Helvetica-Bold", 9)
            header_canvas.drawString(x_start + 320, y_start + 75, "POLICY NUMBER:")
            header_canvas.setFont("Helvetica", 9)
            header_canvas.drawString(x_start + 320, y_start + 60, data['policy_number'])
            
            header_canvas.setFont("Helvetica-Bold", 9)
            header_canvas.drawString(x_start + 320, y_start + 45, "ENDORSEMENT NUMBER:")
            header_canvas.setFont("Helvetica", 9)
            header_canvas.drawString(x_start + 320, y_start + 30, data['endorsement_number'])
            
            header_canvas.setFont("Helvetica-Bold", 9)
            header_canvas.drawString(x_start + 320, y_start + 15, "EFFECTIVE DATE:")
            header_canvas.setFont("Helvetica", 9)
            header_canvas.drawString(x_start + 320, y_start + 0, data['endorsement_effective_date'])
            
            header_canvas.save()
            header_buffer.seek(0)
            
            # Read original template PDF
            with open(template_file_path, 'rb') as template_file:
                template_reader = PdfReader(template_file)
                header_reader = PdfReader(header_buffer)
                writer = PdfWriter()
                
                # Get first page and overlay header
                first_page = template_reader.pages[0]
                header_page = header_reader.pages[0]
                first_page.merge_page(header_page)
                writer.add_page(first_page)
                
                # Add remaining pages without header
                for i in range(1, len(template_reader.pages)):
                    writer.add_page(template_reader.pages[i])
                
                # Save combined PDF
                filename = f"{policy.policy_number}_{template.template_code}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                dest_dir = os.path.join(self.media_root, 'documents', 'generated')
                os.makedirs(dest_dir, exist_ok=True)
                dest_path = os.path.join(dest_dir, filename)
                
                with open(dest_path, 'wb') as output_file:
                    writer.write(output_file)
                
                file_size = os.path.getsize(dest_path)
                
                logger.info(f"Successfully created endorsement with header overlay: {filename}")
                
                return True, {
                    'file_path': f'generated/{filename}',
                    'file_size': file_size,
                    'page_count': len(template_reader.pages)
                }
                
        except Exception as e:
            logger.error(f"Error overlaying header with PyPDF2: {str(e)}")
            # Fall back to generating basic PDF with header
            return self._generate_basic_pdf(policy, template.template_name, data)
    
    def _copy_static_pdf(self, template_file_path: str, policy: Policy, template: DocumentTemplate) -> Tuple[bool, Dict]:
        """Copy static PDF without modifications"""
        try:
            # Create destination path
            filename = f"{policy.policy_number}_{template.template_code}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            dest_dir = os.path.join(self.media_root, 'documents', 'generated')
            os.makedirs(dest_dir, exist_ok=True)
            dest_path = os.path.join(dest_dir, filename)
            
            # Copy file
            import shutil
            shutil.copy2(template_file_path, dest_path)
            
            # Get file info
            file_size = os.path.getsize(dest_path)
            
            logger.info(f"Copied static PDF: {filename}")
            
            return True, {
                'file_path': f'generated/{filename}',
                'file_size': file_size,
                'page_count': 1  # You'd calculate this from the PDF
            }
            
        except Exception as e:
            logger.error(f"Error copying static PDF: {str(e)}")
            return False, {'error': str(e)}
    
    def _generate_basic_pdf(self, policy: Policy, document_name: str, template_data: dict = None) -> Tuple[bool, Dict]:
        """Generate basic PDF with policy information - UPDATED for endorsement headers and location schedules"""
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
            from reportlab.lib.units import inch
            from reportlab.lib import colors
            import io
            
            # Create PDF buffer
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=1*inch)
            
            # Build document elements
            elements = []
            styles = getSampleStyleSheet()
            
            # Check if this is an endorsement (has endorsement data)
            is_endorsement = template_data and 'endorsement_number' in template_data
            has_locations = template_data and template_data.get('location_schedule', {}).get('has_schedule', False)
            
            logger.info(f"Generating {'endorsement' if is_endorsement else 'standard'} PDF: {document_name} (locations: {has_locations})")
            
            if is_endorsement:
                # CREATE ENDORSEMENT WITH HEADER
                
                # Standard Header Table for Endorsements
                header_data = [
                    ['NAMED INSURED:', 'POLICY NUMBER:'],
                    [template_data['named_insured']['company_name'], template_data['policy_number']],
                    [f"{template_data['named_insured']['address']}", 'ENDORSEMENT NUMBER:'],
                    [f"{template_data['named_insured']['city']}, {template_data['named_insured']['state']} {template_data['named_insured']['zip_code']}", 
                    template_data['endorsement_number']],
                    ['', 'ENDORSEMENT EFFECTIVE DATE:'],
                    ['', template_data['endorsement_effective_date']]
                ]
                
                header_table = Table(header_data, colWidths=[4*inch, 2.5*inch])
                header_table.setStyle(TableStyle([
                    ('BOX', (0, 0), (-1, -1), 2, colors.black),
                    ('INNERGRID', (0, 0), (-1, -1), 1, colors.black),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('LEFTPADDING', (0, 0), (-1, -1), 12),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 12),
                    ('TOPPADDING', (0, 0), (-1, -1), 8),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ]))
                
                elements.append(header_table)
                elements.append(Spacer(1, 0.3*inch))
                
                # Endorsement Title
                title_style = styles['Heading1']
                title_style.alignment = 1  # Center
                title = Paragraph(template_data.get('endorsement_title', document_name).upper(), title_style)
                elements.append(title)
                elements.append(Spacer(1, 0.2*inch))
                
                # LOCATION SCHEDULE CONTENT - NEW
                if has_locations:
                    schedule_data = template_data['location_schedule']
                    
                    # Schedule description
                    content_style = styles['Normal']
                    intro_text = f"""
                    This endorsement modifies insurance provided under the following:
                    
                    <b>POLICY NUMBER:</b> {template_data['policy_number']}<br/>
                    <b>NAMED INSURED:</b> {template_data['named_insured']['company_name']}<br/>
                    <b>EFFECTIVE DATE:</b> {template_data['endorsement_effective_date']}<br/>
                    
                    <b>SCHEDULE OF LOCATIONS</b><br/>
                    The following locations are covered under this policy:
                    """
                    
                    intro = Paragraph(intro_text, content_style)
                    elements.append(intro)
                    elements.append(Spacer(1, 0.2*inch))
                    
                    # Location table
                    if schedule_data['locations']:
                        # Table headers
                        table_data = [['Location', 'Address', 'Building Limit', 'Contents Limit', 'Total Limit']]
                        
                        # Add location rows
                        for location in schedule_data['locations']:
                            row = [
                                location['location_number'],
                                f"{location['street_address']}\n{location['city']}, {location['state']} {location['zip_code']}",
                                location['building_limit_formatted'],
                                location['contents_limit_formatted'], 
                                location['total_limit_formatted']
                            ]
                            table_data.append(row)
                        
                        # Add totals row
                        totals = schedule_data['totals']
                        table_data.append([
                            'TOTALS:',
                            f"{totals['total_locations']} Locations",
                            totals['total_building_formatted'],
                            totals['total_contents_formatted'],
                            totals['total_combined_formatted']
                        ])
                        
                        # Create and style table
                        location_table = Table(table_data, colWidths=[0.8*inch, 2.5*inch, 1.2*inch, 1.2*inch, 1.2*inch])
                        location_table.setStyle(TableStyle([
                            # Header row
                            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                            ('FONTSIZE', (0, 0), (-1, 0), 9),
                            
                            # Data rows
                            ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
                            ('FONTSIZE', (0, 1), (-1, -2), 8),
                            ('GRID', (0, 0), (-1, -1), 1, colors.black),
                            
                            # Totals row
                            ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
                            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                            ('FONTSIZE', (0, -1), (-1, -1), 9),
                            
                            # Alignment
                            ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
                            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                            ('LEFTPADDING', (0, 0), (-1, -1), 6),
                            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                            ('TOPPADDING', (0, 0), (-1, -1), 6),
                            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                        ]))
                        
                        elements.append(location_table)
                        elements.append(Spacer(1, 0.2*inch))
                    
                    # Schedule notes
                    notes_text = f"""
                    <b>SCHEDULE NOTES:</b><br/>
                    • Total Locations: {schedule_data['totals']['total_locations']}<br/>
                    • Combined Limits: {schedule_data['totals']['total_combined_formatted']}<br/>
                    • This schedule supersedes any previously issued location schedules.<br/>
                    • All other terms and conditions of the policy remain unchanged.
                    """
                    
                    notes = Paragraph(notes_text, content_style)
                    elements.append(notes)
                    
                else:
                    # Standard endorsement content for non-location endorsements
                    content_style = styles['Normal']
                    endorsement_code = template_data.get('template', {}).get('code', '').upper()
                    
                    if 'ADD-INSURED' in endorsement_code or 'ADDITIONAL' in endorsement_code:
                        content_text = f"""
                        This endorsement modifies insurance provided under the following:
                        
                        <b>POLICY NUMBER:</b> {template_data['policy_number']}<br/>
                        <b>NAMED INSURED:</b> {template_data['named_insured']['company_name']}<br/>
                        <b>EFFECTIVE DATE:</b> {template_data['endorsement_effective_date']}<br/>
                        
                        <b>ADDITIONAL INSURED INFORMATION:</b><br/>
                        Name: [TO BE COMPLETED]<br/>
                        Address: [TO BE COMPLETED]
                        
                        <br/><br/>
                        This endorsement adds the above named person or organization as an additional insured 
                        under the General Liability Coverage of this policy, but only with respect to liability 
                        arising out of operations performed by or on behalf of the named insured.
                        """
                    elif 'WAIVER' in endorsement_code or 'SUB' in endorsement_code:
                        content_text = f"""
                        This endorsement modifies insurance provided under the following:
                        
                        <b>POLICY NUMBER:</b> {template_data['policy_number']}<br/>
                        <b>NAMED INSURED:</b> {template_data['named_insured']['company_name']}<br/>
                        <b>EFFECTIVE DATE:</b> {template_data['endorsement_effective_date']}<br/>
                        
                        <b>WAIVER OF SUBROGATION:</b><br/>
                        The insurer waives all rights of subrogation against: [TO BE COMPLETED]
                        
                        <br/><br/>
                        This waiver applies only to the extent that such waiver is permitted by law.
                        """
                    else:
                        # Generic endorsement
                        content_text = f"""
                        This endorsement modifies insurance provided under the following:
                        
                        <b>POLICY NUMBER:</b> {template_data['policy_number']}<br/>
                        <b>NAMED INSURED:</b> {template_data['named_insured']['company_name']}<br/>
                        <b>EFFECTIVE DATE:</b> {template_data['endorsement_effective_date']}<br/>
                        
                        <br/>
                        {template_data.get('endorsement_description', 'Endorsement details to be specified.')}
                        """
                    
                    content = Paragraph(content_text, content_style)
                    elements.append(content)
                
                # Add footer
                elements.append(Spacer(1, 0.5*inch))
                footer_style = styles['Normal']
                footer_style.fontSize = 8
                footer_style.alignment = 1  # Center
                footer = Paragraph(f"Generated on {timezone.now().strftime('%B %d, %Y at %I:%M %p')} by Skye Insurance Group", footer_style)
                elements.append(footer)
                
                # Build PDF
                doc.build(elements)
                
            else:
                # STANDARD DOCUMENT (non-endorsement) - use canvas directly for backwards compatibility
                
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
            
            logger.info(f"Generated PDF saved: {filename}")
            
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
        return self._generate_basic_pdf(policy, template.template_name, data)