import os
import hashlib
from datetime import datetime
from django.conf import settings
from django.utils import timezone
from .portal_models import PortalDocument

class DualStorageService:
    """Handle dual storage for portal documents"""
    
    @staticmethod
    def generate_paths(company_id, filename):
        """Generate storage paths for dual storage"""
        date_part = datetime.now().strftime('%Y\\%m')
        
        # Add timestamp to filename to ensure uniqueness
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        name, ext = os.path.splitext(filename)
        unique_filename = f"{name}_{timestamp}{ext}"
        
        paths = {
            'active': f"portal-uploads\\company-{company_id}\\active\\{date_part}\\{unique_filename}",
            'archive': f"company-archive\\company-{company_id}\\{date_part}\\{unique_filename}",
            'removed': f"portal-uploads\\company-{company_id}\\removed\\{date_part}\\{unique_filename}",
        }
        
        return paths
    
    @staticmethod
    def save_with_dual_storage(uploaded_file, company_id, document_data):
        """Save uploaded file to both active and archive locations"""
        
        paths = DualStorageService.generate_paths(company_id, uploaded_file.name)
        
        # Save to active location
        active_path = os.path.join(settings.MEDIA_ROOT, paths['active'])
        os.makedirs(os.path.dirname(active_path), exist_ok=True)
        
        with open(active_path, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)
        
        # Create archive copy
        archive_path = os.path.join(settings.MEDIA_ROOT, paths['archive'])
        os.makedirs(os.path.dirname(archive_path), exist_ok=True)
        
        import shutil
        shutil.copy2(active_path, archive_path)
        
        # Create database record
        document = PortalDocument(
            company_id=company_id,
            document_name=document_data.get('document_name', uploaded_file.name),
            document_type=document_data.get('document_type', 'general'),
            file=paths['active'],
            original_file_path=paths['active'],
            archive_path=paths['archive'],
            archive_created_date=timezone.now(),
            file_size=uploaded_file.size,
            file_type=uploaded_file.content_type,
            description=document_data.get('description', ''),
            status='uploaded',
            uploaded_at=timezone.now(),
            uploaded_by_id=document_data.get('uploaded_by_id'),
            client_visible=True,
            permanent_record=True,
        )
        
        # Add optional relationships
        if 'application_id' in document_data:
            document.application_id = document_data['application_id']
        if 'quote_id' in document_data:
            document.quote_id = document_data['quote_id']
        if 'policy_id' in document_data:
            document.policy_id = document_data['policy_id']
        if 'claim_id' in document_data:
            document.claim_id = document_data['claim_id']
        
        document.save()
        return document

