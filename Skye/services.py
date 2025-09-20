# Skye/services.py - Complete Final Version

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
    
    # Enhanced model display fields mapping - includes all your models
    MODEL_DISPLAY_FIELDS = {
        # Original mappings
        'venture': 'venture_name',
        'company': 'company_name',
        'products': 'product_name',
        'employee_contact': 'employee_name_combined',
        'employeecontact': 'employee_name_combined',  # Alternative naming
        'employee_location': 'employee_location_name',
        'employeelocation': 'employee_location_name',  # Alternative naming
        'coverage': 'coverage_name',
        'stage': 'stage_name',
        'parameter': 'parameter_name',
        'workflow': 'workflow_name',
        'task': 'task_name',
        'options': 'option_name',
        'paper': 'paper_name',
        'broker': 'broker_name',
        
        # Additional Catalog models
        'drive': 'drive_name',
        'cover': 'cover_name',
        'employee_function_detail': 'employee_function_detail_id',  # May need custom handling
        'paper_detail': 'paper_detail_id',
        'applications': 'application_name',
        'applicationquestion': 'custom_question',
        'applicationresponse': 'response',
        'parametertype': 'parameter_type_name',
        'parameter_map': 'parameter_map_id',
        'document': 'document_name',
        'workflowdetail': 'workflow_detail_id',
        'floworigin': 'flow_origin_name',
        'attachment': 'attachment_name',
        'attachment_detail': 'attachment_detail_id',
        'limits': 'limit_text',
        'retention': 'retention_text',
        'sublimit': 'sublimit_name',
        'orders': 'orders_id',  # May want to create a custom display method
        'orderoption': 'order_option_id',
        'companycontact': 'company_contact_first',  # May want to combine first+last
        'companylocation': 'company_location_city',
        'brokerlocation': 'broker_city',
        'brokercontact': 'broker_first_name',  # May want to combine first+last
        
        # Machine Learning models - Updated to use __str__ methods
        'generation_job': None,
        'generationjob': None,
        'generation_log': None,
        'generationlog': None,
        'model_parameter': None,
        'modelparameter': None,
        'training_job': None,    # This will now use "Training Job 1" from __str__
        'trainingjob': None,
        'generation_model': 'model_name',
        'generationmodel': 'model_name',
        'data_seed': None,
        'dataseed': None,
        'training_model': 'model_name',
        'trainingmodel': 'model_name',
        'input_output': None,    # This will now use input_output_name from __str__
        'inputoutput': None,
    }
    
    # Custom display methods for complex models
    CUSTOM_DISPLAY_METHODS = {
        'employeecontact': lambda obj: f"{getattr(obj, 'employee_name_first', '')} {getattr(obj, 'employee_name_last', '')}".strip(),
        'employee_contact': lambda obj: f"{getattr(obj, 'employee_name_first', '')} {getattr(obj, 'employee_name_last', '')}".strip(),
        'companycontact': lambda obj: f"{getattr(obj, 'company_contact_first', '')} {getattr(obj, 'company_contact_last', '')}".strip(),
        'brokercontact': lambda obj: f"{getattr(obj, 'broker_first_name', '')} {getattr(obj, 'broker_last_name', '')}".strip(),
        'orders': lambda obj: f"Order #{getattr(obj, 'orders_id', 'N/A')} - {getattr(obj, 'company', 'No Company')}",
    }
    
    @classmethod
    def resolve_foreign_keys(cls, queryset, model_name):
        """
        Resolve foreign keys in a queryset to readable names
        Enhanced to handle all model types consistently
        """
        if not queryset:
            return []
        
        # Handle both QuerySet and list inputs
        if hasattr(queryset, 'model'):
            model_class = queryset.model
            objects = list(queryset)
        else:
            # If it's a list, get model from first object
            objects = list(queryset)
            if not objects:
                return []
            model_class = objects[0].__class__
        
        resolved_data = []
        
        for obj in objects:
            obj_data = {}
            
            # Get all field values
            for field in model_class._meta.get_fields():
                if not field.is_relation:
                    # Regular field
                    value = getattr(obj, field.name, None)
                    obj_data[field.name] = value
                elif hasattr(field, 'related_model') and field.related_model:
                    # Foreign key field - but skip reverse relations
                    if hasattr(field, 'remote_field') and field.remote_field:
                        # This is a forward foreign key
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
                    # Skip reverse foreign key relations (like 'products' pointing back to GenerationLog)
            
            # Add primary key
            obj_data['pk'] = obj.pk
            resolved_data.append(obj_data)
        
        # Debug output
        if resolved_data:
            logger.info(f"ForeignKeyResolver: Processed {len(resolved_data)} records for {model_name}")
            logger.debug(f"Sample resolved data: {resolved_data[0]}")
        
        return resolved_data
    
    @classmethod
    def _resolve_single_fk(cls, related_obj, model_name):
        """
        Resolve a single foreign key object to its display name
        Enhanced with custom display methods and better fallbacks
        """
        if not related_obj:
            return None
            
        cache_key = f'{cls.CACHE_PREFIX}:{model_name}:{related_obj.pk}'
        cached_result = cache.get(cache_key)
        
        if cached_result is not None:
            return cached_result
        
        try:
            # Check for custom display method first
            if model_name in cls.CUSTOM_DISPLAY_METHODS:
                display_value = cls.CUSTOM_DISPLAY_METHODS[model_name](related_obj)
            else:
                # Get display field for this model
                display_field = cls.MODEL_DISPLAY_FIELDS.get(model_name, None)
                
                if display_field and hasattr(related_obj, display_field):
                    display_value = getattr(related_obj, display_field)
                else:
                    # Use __str__ method by default
                    display_value = str(related_obj)
            
            # Ensure we have a string value
            if display_value is None:
                display_value = f"ID: {related_obj.pk}"
            else:
                display_value = str(display_value)
            
            # Cache the result
            cache.set(cache_key, display_value, cls.CACHE_TIMEOUT)
            
            # Debug output
            logger.debug(f"FK Resolution: {model_name}:{related_obj.pk} -> '{display_value}'")
            
            return display_value
            
        except Exception as e:
            logger.warning(f"Error resolving FK for {model_name}:{related_obj.pk}: {e}")
            fallback_value = f"ID: {related_obj.pk}"
            cache.set(cache_key, fallback_value, cls.CACHE_TIMEOUT)
            return fallback_value
    
    @classmethod
    def bulk_resolve_fks(cls, fk_ids, model_name):
        """
        Bulk resolve multiple foreign key IDs
        Enhanced with better error handling and fallbacks
        """
        if not fk_ids:
            return {}
        
        try:
            model_class = apps.get_model('Skye', model_name)
        except LookupError:
            logger.error(f"Model {model_name} not found")
            return {fk_id: f"ID: {fk_id}" for fk_id in fk_ids}
        
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
                # Check for custom display method
                if model_name in cls.CUSTOM_DISPLAY_METHODS:
                    objects = model_class.objects.filter(pk__in=uncached_ids)
                    cache_data = {}
                    
                    for obj in objects:
                        cache_key = f'{cls.CACHE_PREFIX}:{model_name}:{obj.pk}'
                        display_value = cls.CUSTOM_DISPLAY_METHODS[model_name](obj)
                        cache_data[cache_key] = display_value
                        cached_results[cache_key] = display_value
                else:
                    # Use regular display field or __str__
                    display_field = cls.MODEL_DISPLAY_FIELDS.get(model_name, None)
                    if display_field:
                        objects = model_class.objects.filter(pk__in=uncached_ids).values('pk', display_field)
                        cache_data = {}
                        
                        for obj in objects:
                            cache_key = f'{cls.CACHE_PREFIX}:{model_name}:{obj["pk"]}'
                            display_value = obj.get(display_field, f"ID: {obj['pk']}")
                            cache_data[cache_key] = str(display_value) if display_value is not None else f"ID: {obj['pk']}"
                            cached_results[cache_key] = cache_data[cache_key]
                    else:
                        # Use __str__ method
                        objects = model_class.objects.filter(pk__in=uncached_ids)
                        cache_data = {}
                        
                        for obj in objects:
                            cache_key = f'{cls.CACHE_PREFIX}:{model_name}:{obj.pk}'
                            display_value = str(obj)
                            cache_data[cache_key] = display_value
                            cached_results[cache_key] = display_value
                
                # Cache the new results
                cache.set_many(cache_data, cls.CACHE_TIMEOUT)
                
            except Exception as e:
                logger.error(f"Error bulk resolving FKs for {model_name}: {e}")
                # Fallback for errored items
                for fk_id in uncached_ids:
                    cache_key = f'{cls.CACHE_PREFIX}:{model_name}:{fk_id}'
                    if cache_key not in cached_results:
                        cached_results[cache_key] = f"ID: {fk_id}"
        
        # Build final results mapping
        results = {}
        for fk_id in fk_ids:
            cache_key = f'{cls.CACHE_PREFIX}:{model_name}:{fk_id}'
            results[fk_id] = cached_results.get(cache_key, f"ID: {fk_id}")
        
        return results

class ProgressiveDataLoader:
    """
    Service for progressive loading of page sections
    Enhanced to use ForeignKeyResolver consistently
    """
    
    @classmethod
    def load_sections_batch(cls, page_config, section_names, start_index=0, batch_size=2):
        """
        Load a batch of sections for progressive loading
        Enhanced to use ForeignKeyResolver for consistent FK resolution
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
                    # Get model class with multiple naming attempts
                    model_class = cls._get_model_class(table_name)
                    
                    if not model_class:
                        logger.warning(f"Model not found for table: {table_name}")
                        sections_data[section_name] = {
                            'config': section_config,
                            'data': [],
                            'total_count': 0,
                            'error': f'Model {table_name} not implemented yet'
                        }
                        continue
                    
                    # Get limited queryset
                    limit = getattr(settings, 'PROGRESSIVE_LOADING', {}).get('RECORDS_PER_SECTION', 20)
                    queryset = model_class.objects.all()[:limit]
                    total_count = model_class.objects.count()
                    
                    # Resolve foreign keys using ForeignKeyResolver
                    resolved_data = ForeignKeyResolver.resolve_foreign_keys(queryset, table_name)
                    
                    sections_data[section_name] = {
                        'config': section_config,
                        'data': resolved_data,
                        'total_count': total_count
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
    
    @classmethod
    def _get_model_class(cls, table_name):
        """
        Try to get model class with multiple naming variations
        """
        possible_names = [
            table_name,  # e.g., 'venture'
            table_name.title(),  # e.g., 'Venture'
            ''.join(word.title() for word in table_name.split('_')),  # e.g., 'EmployeeContact'
        ]
        
        for model_name in possible_names:
            try:
                return apps.get_model('Skye', model_name)
            except LookupError:
                continue
        
        return None


class DataExportService:
    """
    Service for exporting data to various formats
    """
    
    @classmethod
    def export_to_csv(cls, queryset, filename):
        """
        Export queryset to CSV format
        """
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        writer = csv.writer(response)
        
        if queryset.exists():
            # Write header
            field_names = [field.name for field in queryset.model._meta.fields]
            writer.writerow(field_names)
            
            # Write data
            for obj in queryset:
                row = [getattr(obj, field) for field in field_names]
                writer.writerow(row)
        
        return response
    
    @classmethod
    def export_to_excel(cls, queryset, filename):
        """
        Export queryset to Excel format
        """
        import xlsxwriter
        from django.http import HttpResponse
        from io import BytesIO
        
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet()
        
        if queryset.exists():
            # Write header
            field_names = [field.name for field in queryset.model._meta.fields]
            for col, field_name in enumerate(field_names):
                worksheet.write(0, col, field_name)
            
            # Write data
            for row, obj in enumerate(queryset, start=1):
                for col, field in enumerate(field_names):
                    value = getattr(obj, field)
                    worksheet.write(row, col, str(value) if value is not None else '')
        
        workbook.close()
        output.seek(0)
        
        response = HttpResponse(
            output.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response


class CacheService:
    """
    Service for managing application cache
    """
    
    @classmethod
    def clear_fk_cache(cls):
        """
        Clear all foreign key resolution cache
        """
        cache_keys = cache.keys(f'{ForeignKeyResolver.CACHE_PREFIX}:*')
        if cache_keys:
            cache.delete_many(cache_keys)
            logger.info(f"Cleared {len(cache_keys)} FK cache entries")
    
    @classmethod
    def clear_all_cache(cls):
        """
        Clear all application cache
        """
        cache.clear()
        logger.info("Cleared all cache")
    
    @classmethod
    def get_cache_stats(cls):
        """
        Get cache statistics
        """
        try:
            # This works with Redis backend
            import redis
            from django.core.cache.backends.redis import RedisCache
            
            if isinstance(cache, RedisCache):
                redis_client = cache._cache.get_client()
                info = redis_client.info('memory')
                return {
                    'memory_used': info.get('used_memory_human', 'N/A'),
                    'keys': redis_client.dbsize(),
                    'hits': info.get('keyspace_hits', 0),
                    'misses': info.get('keyspace_misses', 0),
                }
        except ImportError:
            pass
        
        return {'message': 'Cache stats not available for this backend'}


class ValidationService:
    """
    Service for data validation
    """
    
    @classmethod
    def validate_model_instance(cls, instance):
        """
        Validate a model instance
        """
        try:
            instance.full_clean()
            return {'valid': True, 'errors': {}}
        except Exception as e:
            return {'valid': False, 'errors': e.message_dict if hasattr(e, 'message_dict') else str(e)}
    
    @classmethod
    def validate_foreign_keys(cls, model_class):
        """
        Validate that all foreign key relationships are properly configured
        """
        issues = []
        
        for field in model_class._meta.get_fields():
            if hasattr(field, 'related_model') and field.related_model:
                try:
                    # Check if related model exists
                    field.related_model.objects.first()
                except Exception as e:
                    issues.append({
                        'field': field.name,
                        'related_model': field.related_model._meta.label,
                        'error': str(e)
                    })
        
        return issues