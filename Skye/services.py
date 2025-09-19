# Create file: Skye/services.py

from django.core.cache import cache
from django.apps import apps
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class ForeignKeyResolver:
    """
    Service for resolving foreign key IDs to readable names
    with caching for performance
    """
    
    CACHE_PREFIX = 'fk_resolve'
    CACHE_TIMEOUT = getattr(settings, 'FK_RESOLUTION_CACHE_TIMEOUT', 300)
    
    # Define how to get display names for each model
    MODEL_DISPLAY_FIELDS = {
        'venture': 'venture_name',
        'company': 'company_name',
        'products': 'product_name',
        'employee_contact': 'employee_name_combined',
        'employee_location': 'employee_location_name',
        'coverage': 'coverage_name',
        'stage': 'stage_name',
        'parameter': 'parameter_name',
        'workflow': 'workflow_name',
        'task': 'task_name',
        'options': 'option_name',
        'paper': 'paper_name',
        'broker': 'broker_name',
        # Add more as needed
    }
    
    @classmethod
    def resolve_foreign_keys(cls, queryset, model_name):
        """
        Resolve foreign keys in a queryset to readable names
        """
        if not queryset.exists():
            return []
        
        model_class = queryset.model
        resolved_data = []
        
        for obj in queryset:
            obj_data = {}
            
            # Get all field values
            for field in model_class._meta.get_fields():
                if not field.is_relation:
                    # Regular field
                    obj_data[field.name] = getattr(obj, field.name, None)
                elif hasattr(field, 'related_model') and field.related_model:
                    # Foreign key field
                    fk_value = getattr(obj, field.name, None)
                    if fk_value:
                        resolved_name = cls._resolve_single_fk(
                            fk_value, 
                            field.related_model._meta.model_name
                        )
                        obj_data[field.name] = resolved_name
                        obj_data[f'{field.name}_id'] = fk_value.pk
                    else:
                        obj_data[field.name] = None
                        obj_data[f'{field.name}_id'] = None
            
            # Add primary key
            obj_data['pk'] = obj.pk
            resolved_data.append(obj_data)
        
        return resolved_data
    
    @classmethod
    def _resolve_single_fk(cls, related_obj, model_name):
        """
        Resolve a single foreign key object to its display name
        """
        if not related_obj:
            return None
            
        cache_key = f'{cls.CACHE_PREFIX}:{model_name}:{related_obj.pk}'
        cached_result = cache.get(cache_key)
        
        if cached_result is not None:
            return cached_result
        
        # Get display field for this model
        display_field = cls.MODEL_DISPLAY_FIELDS.get(model_name, 'id')
        
        try:
            display_value = getattr(related_obj, display_field, str(related_obj.pk))
            # Cache the result
            cache.set(cache_key, display_value, cls.CACHE_TIMEOUT)
            return display_value
        except AttributeError:
            logger.warning(f"Display field '{display_field}' not found for {model_name}")
            return str(related_obj.pk)
    
    @classmethod
    def bulk_resolve_fks(cls, fk_ids, model_name):
        """
        Bulk resolve multiple foreign key IDs
        """
        if not fk_ids:
            return {}
        
        model_class = apps.get_model('Skye', model_name)
        display_field = cls.MODEL_DISPLAY_FIELDS.get(model_name, 'id')
        
        # Check cache first
        cache_keys = [f'{cls.CACHE_PREFIX}:{model_name}:{fk_id}' for fk_id in fk_ids]
        cached_results = cache.get_many(cache_keys)
        
        # Find uncached IDs
        uncached_ids = []
        for fk_id in fk_ids:
            cache_key = f'{cls.CACHE_PREFIX}:{model_name}:{fk_id}'
            if cache_key not in cached_results:
                uncached_ids.append(fk_id)
        
        # Fetch uncached data
        if uncached_ids:
            try:
                objects = model_class.objects.filter(pk__in=uncached_ids).values('pk', display_field)
                cache_data = {}
                
                for obj in objects:
                    cache_key = f'{cls.CACHE_PREFIX}:{model_name}:{obj["pk"]}'
                    display_value = obj.get(display_field, str(obj['pk']))
                    cache_data[cache_key] = display_value
                    cached_results[cache_key] = display_value
                
                # Cache the new results
                cache.set_many(cache_data, cls.CACHE_TIMEOUT)
                
            except Exception as e:
                logger.error(f"Error bulk resolving FKs for {model_name}: {e}")
        
        # Build final results mapping
        results = {}
        for fk_id in fk_ids:
            cache_key = f'{cls.CACHE_PREFIX}:{model_name}:{fk_id}'
            results[fk_id] = cached_results.get(cache_key, str(fk_id))
        
        return results

class ProgressiveDataLoader:
    """
    Service for progressive loading of page sections
    """
    
    @classmethod
    def load_sections_batch(cls, page_config, section_names, start_index=0, batch_size=2):
        """
        Load a batch of sections for progressive loading
        """
        from django.apps import apps
        
        sections_data = {}
        section_list = list(section_names)
        
        end_index = min(start_index + batch_size, len(section_list))
        batch_sections = section_list[start_index:end_index]
        
        for section_name in batch_sections:
            if section_name in page_config:
                section_config = page_config[section_name]
                table_name = section_config['table']
                
                try:
                    # Get model class
                    model_class = apps.get_model('Skye', table_name)
                    
                    # Get limited queryset
                    queryset = model_class.objects.all()[:settings.PROGRESSIVE_LOADING['RECORDS_PER_SECTION']]
                    
                    # Resolve foreign keys
                    resolved_data = ForeignKeyResolver.resolve_foreign_keys(queryset, table_name)
                    
                    sections_data[section_name] = {
                        'config': section_config,
                        'data': resolved_data,
                        'total_count': model_class.objects.count()
                    }
                    
                except Exception as e:
                    logger.error(f"Error loading section {section_name}: {e}")
                    sections_data[section_name] = {
                        'config': section_config,
                        'data': [],
                        'total_count': 0,
                        'error': str(e)
                    }
        
        return {
            'sections': sections_data,
            'has_more': end_index < len(section_list),
            'next_index': end_index
        }