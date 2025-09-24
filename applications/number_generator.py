# File: applications/number_generator.py
# Create this new file in the applications directory

from django.db import transaction, models
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

class NumberGenerator:
    """Service for generating structured document numbers with 6-digit base"""
    
    @classmethod
    def generate_application_number(cls, product, base_number=None, sequence_number=0, version_number=None):
        """
        Generate an application number in format: APP-[PRODUCT]-[NUMBER]-[SEQUENCE][-VERSION]
        """
        product_code = product.document_code or 'GEN'
        
        if not base_number:
            # Reserve new number from sequence tracker
            from .models import SequenceTracker
            tracker, created = SequenceTracker.objects.get_or_create(
                product_code=product_code,
                defaults={
                    'product_name': product.product_name,
                    'last_used_number': 0,
                    'last_reserved_number': 0
                }
            )
            base_number = cls._reserve_number(tracker)
        
        # Format the number
        number = f"APP-{product_code}-{base_number}-{sequence_number:02d}"
        
        # Add version suffix if needed
        if version_number:
            number += f"-{version_number:02d}"
        
        return number, base_number
    
    @classmethod
    def generate_quote_number(cls, application=None, product=None, base_number=None, sequence_number=0, version_number=None):
        """
        Generate a quote number, inheriting base from application if provided
        Format: QTE-[PRODUCT]-[NUMBER]-[SEQUENCE][-VERSION]
        """
        # If we have an application, inherit its base number
        if application and application.base_number:
            product_code = application.product.document_code or 'GEN'
            base_number = application.base_number
        elif product:
            product_code = product.document_code or 'GEN'
            
            if not base_number:
                # Reserve new number from sequence tracker
                from .models import SequenceTracker
                tracker, created = SequenceTracker.objects.get_or_create(
                    product_code=product_code,
                    defaults={
                        'product_name': product.product_name,
                        'last_used_number': 0,
                        'last_reserved_number': 0
                    }
                )
                base_number = cls._reserve_number(tracker)
        else:
            raise ValueError("Either application or product must be provided")
        
        # Format the number
        number = f"QTE-{product_code}-{base_number}-{sequence_number:02d}"
        
        # Add version suffix if needed
        if version_number:
            number += f"-{version_number:02d}"
        
        return number, base_number
    
    @classmethod
    def generate_policy_number(cls, quote):
        """
        Generate a policy number from a quote
        Format: POL-[PRODUCT]-[NUMBER]-[SEQUENCE][-VERSION]
        """
        product_code = quote.application.product.document_code or 'GEN'
        base_number = quote.base_number
        sequence_number = quote.sequence_number
        version_number = quote.version_number
        
        # Format the number
        number = f"POL-{product_code}-{base_number}-{sequence_number:02d}"
        
        # Add version suffix if needed
        if version_number:
            number += f"-{version_number:02d}"
        
        return number
    
    @classmethod
    def generate_renewal_policy_number(cls, original_policy):
        """
        Generate a renewal policy number with incremented sequence
        """
        product_code = original_policy.quote.application.product.document_code or 'GEN'
        base_number = original_policy.base_number
        new_sequence = original_policy.sequence_number + 1
        
        # Format the number
        number = f"POL-{product_code}-{base_number}-{new_sequence:02d}"
        
        return number, new_sequence
    
    @classmethod
    def _reserve_number(cls, tracker):
        """Reserve the next number in sequence (6-digit format)"""
        with transaction.atomic():
            tracker = tracker.__class__.objects.select_for_update().get(
                sequence_id=tracker.sequence_id
            )
            tracker.last_reserved_number += 1
            if tracker.last_reserved_number > 999999:
                raise ValueError(f"Sequence exhausted for product {tracker.product_code}")
            tracker.save()
            return f"{tracker.last_reserved_number:06d}"
    
    @classmethod
    def confirm_number(cls, product_code, number):
        """Confirm a reserved number as used"""
        from .models import SequenceTracker
        try:
            number_int = int(number)
            with transaction.atomic():
                tracker = SequenceTracker.objects.select_for_update().get(
                    product_code=product_code
                )
                if number_int > tracker.last_used_number:
                    tracker.last_used_number = number_int
                    tracker.save()
                return True
        except Exception as e:
            logger.error(f"Error confirming number {number} for {product_code}: {e}")
            return False
    
    @classmethod
    def cleanup_abandoned_reservations(cls):
        """
        Clean up abandoned reservations (where reserved > used)
        This should be run periodically via a management command or celery task
        """
        from .models import SequenceTracker
        
        trackers = SequenceTracker.objects.filter(
            last_reserved_number__gt=models.F('last_used_number')
        )
        
        for tracker in trackers:
            # Reset reserved to used if gap exists for more than 1 hour
            # This assumes quotes are created within an hour
            tracker.last_reserved_number = tracker.last_used_number
            tracker.save()
            logger.info(f"Reset reservations for {tracker.product_code}")
    
    @classmethod
    def create_quote_version(cls, original_quote):
        """
        Create a new version of a quote
        Returns the new version number to use
        """
        from .models import Quote
        
        # Find highest version number for this quote
        max_version = Quote.objects.filter(
            base_number=original_quote.base_number,
            application=original_quote.application
        ).exclude(
            quote_id=original_quote.quote_id
        ).aggregate(
            max_version=models.Max('version_number')
        )['max_version']
        
        # If no versions exist yet, this will be version 1
        # (original has version_number=None)
        if max_version is None:
            if original_quote.version_number is None:
                return 1
            else:
                return original_quote.version_number + 1
        else:
            return max_version + 1