# Skye/utilities/field_generator.py
# Dynamic form field generator for modal Add/Edit functionality

from django.apps import apps
from django.db import models
import logging

logger = logging.getLogger(__name__)

class FieldGenerator:
    """
    Generates form field metadata from Django models for dynamic form creation
    """
    
    # Fields to exclude from forms (auto-generated or system fields)
    EXCLUDED_FIELDS = {
        'id', 'pk', 'created_at', 'updated_at', 'date_created', 'date_modified',
        'timestamp', 'last_modified', 'created', 'modified'
    }
    
    # Field type mapping for form generation
    FIELD_TYPE_MAPPING = {
        models.CharField: 'text',
        models.TextField: 'textarea',
        models.EmailField: 'email',
        models.URLField: 'url',
        models.IntegerField: 'number',
        models.DecimalField: 'number',
        models.FloatField: 'number',
        models.BooleanField: 'checkbox',
        models.DateField: 'date',
        models.DateTimeField: 'datetime-local',
        models.TimeField: 'time',
        models.ForeignKey: 'select',
        models.OneToOneField: 'select',
        models.ManyToManyField: 'multiselect',
        models.AutoField: 'hidden',  # Usually excluded anyway
    }
    
    @classmethod
    def get_model_fields(cls, section_name, table_name):
        """
        Get field metadata for a model to generate dynamic forms
        """
        try:
            # Try to get model class
            model_class = cls._get_model_class(table_name)
            
            if not model_class:
                return {
                    'error': f'Model for table {table_name} not found',
                    'fields': []
                }
            
            fields = []
            
            for field in model_class._meta.get_fields():
                # Skip excluded fields and reverse foreign keys
                if (field.name.lower() in cls.EXCLUDED_FIELDS or
                    field.name.lower().endswith('_id') or
                    hasattr(field, 'related_model') and field.many_to_one is False):
                    continue
                
                field_info = cls._process_field(field, model_class)
                if field_info:
                    fields.append(field_info)
            
            return {
                'success': True,
                'model_name': model_class.__name__,
                'fields': fields
            }
            
        except Exception as e:
            logger.error(f"Error generating fields for {section_name}: {e}")
            return {
                'error': str(e),
                'fields': []
            }
    
    @classmethod
    def _get_model_class(cls, table_name):
        """
        Get Django model class from table name
        """
        possible_names = [
            table_name,
            table_name.title(),
            ''.join(word.title() for word in table_name.split('_')),
        ]
        
        for model_name in possible_names:
            try:
                return apps.get_model('Skye', model_name)
            except LookupError:
                continue
        
        return None
    
    @classmethod
    def _process_field(cls, field, model_class):
        """
        Process a single Django model field into form field metadata
        """
        try:
            field_type = type(field)
            
            # Get basic field info
            field_info = {
                'name': field.name,
                'label': cls._get_field_label(field),
                'type': cls.FIELD_TYPE_MAPPING.get(field_type, 'text'),
                'required': cls._is_field_required(field),
                'help_text': getattr(field, 'help_text', ''),
                'max_length': getattr(field, 'max_length', None),
            }
            
            # Handle foreign key fields
            if isinstance(field, (models.ForeignKey, models.OneToOneField)):
                field_info.update(cls._process_foreign_key(field))
            
            # Handle choice fields
            if hasattr(field, 'choices') and field.choices:
                field_info['type'] = 'select'
                field_info['choices'] = list(field.choices)
            
            # Handle boolean fields
            if isinstance(field, models.BooleanField):
                field_info['default'] = getattr(field, 'default', False)
            
            # Handle decimal/float fields
            if isinstance(field, models.DecimalField):
                field_info['step'] = f"0.{'0' * (field.decimal_places - 1)}1"
                field_info['max_digits'] = field.max_digits
                field_info['decimal_places'] = field.decimal_places
            
            return field_info
            
        except Exception as e:
            logger.warning(f"Error processing field {field.name}: {e}")
            return None
    
    @classmethod
    def _get_field_label(cls, field):
        """
        Generate a user-friendly label for the field
        """
        if hasattr(field, 'verbose_name') and field.verbose_name:
            return field.verbose_name.title()
        
        # Convert field name to title case
        return field.name.replace('_', ' ').title()
    
    @classmethod
    def _is_field_required(cls, field):
        """
        Determine if a field is required
        """
        # Check if field allows null or blank
        if getattr(field, 'null', False) or getattr(field, 'blank', False):
            return False
        
        # Check if field has a default value
        if hasattr(field, 'default') and field.default != models.NOT_PROVIDED:
            return False
        
        # AutoFields are not required (handled by database)
        if isinstance(field, models.AutoField):
            return False
        
        return True
    
    @classmethod
    def _process_foreign_key(cls, field):
        """
        Process foreign key field to get related model options
        """
        try:
            related_model = field.related_model
            
            # Get display field for related model
            display_field = cls._get_display_field(related_model)
            
            # Get available options (limit to reasonable number)
            options = []
            queryset = related_model.objects.all()[:100]  # Limit for performance
            
            for obj in queryset:
                # Handle different display field cases
                if display_field == '__str__':
                    # Call the __str__ method
                    label = str(obj)
                else:
                    # Get the actual field value
                    label = getattr(obj, display_field, str(obj))
                
                options.append({
                    'value': obj.pk,
                    'label': label
                })
            
            return {
                'related_model': related_model.__name__,
                'display_field': display_field,
                'options': options,
                'empty_label': f'Select {cls._get_field_label(field)}'
            }
            
        except Exception as e:
            logger.warning(f"Error processing foreign key {field.name}: {e}")
            return {
                'options': [],
                'empty_label': f'Select {cls._get_field_label(field)}'
            }
    
    @classmethod
    def _get_display_field(cls, model):
        """
        Determine the best field to display for a model
        """
        # Check if model has a custom __str__ method (not the default one)
        if hasattr(model, '__str__') and model.__str__ != object.__str__:
            # First try common name fields
            name_fields = ['name', 'title', 'label', 'display_name']
            
            for field_name in name_fields:
                if hasattr(model, field_name):
                    return field_name
            
            # Try model-specific naming patterns
            model_name = model.__name__.lower()
            
            # For EmployeeContact, try employee name fields
            if model_name == 'employeecontact':
                if hasattr(model, 'employee_name_combined'):
                    return 'employee_name_combined'
                elif hasattr(model, 'employee_name_first'):
                    return 'employee_name_first'
            
            # Try other specific patterns
            specific_field = f'{model_name}_name'
            if hasattr(model, specific_field):
                return specific_field
            
            # If model has a meaningful __str__, use it
            return '__str__'
        
        # Fall back to first text field we can find
        for field in model._meta.get_fields():
            if (hasattr(field, 'max_length') and 
                field.name not in ['id', 'pk'] and 
                not field.name.endswith('_id')):
                return field.name
        
        # Last resort
        return '__str__'
    
    @classmethod
    def create_record(cls, table_name, form_data):
        """
        Create a new record using the form data
        """
        try:
            model_class = cls._get_model_class(table_name)
            
            if not model_class:
                return {
                    'success': False,
                    'error': f'Model for table {table_name} not found'
                }
            
            # Process form data for model creation
            processed_data = cls._process_form_data(model_class, form_data)
            
            # Create new instance
            instance = model_class(**processed_data)
            instance.full_clean()  # Validate the instance
            instance.save()
            
            return {
                'success': True,
                'message': f'{model_class.__name__} created successfully',
                'id': instance.pk,
                'display_value': str(instance)
            }
            
        except Exception as e:
            logger.error(f"Error creating record for {table_name}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    @classmethod
    def _process_form_data(cls, model_class, form_data):
        """
        Process form data for model creation, handling foreign keys
        """
        processed_data = {}
        
        for field in model_class._meta.get_fields():
            if field.name in form_data:
                value = form_data[field.name]
                
                # Skip empty values for optional fields
                if value in ['', None]:
                    if not cls._is_field_required(field):
                        continue
                    else:
                        # Required field is empty
                        continue
                
                # Handle foreign key fields
                if isinstance(field, (models.ForeignKey, models.OneToOneField)):
                    try:
                        # Convert to integer for foreign key lookup
                        if value:
                            related_instance = field.related_model.objects.get(pk=int(value))
                            processed_data[field.name] = related_instance
                    except (ValueError, field.related_model.DoesNotExist):
                        # Skip invalid foreign key values
                        continue
                
                # Handle boolean fields
                elif isinstance(field, models.BooleanField):
                    processed_data[field.name] = value in ['true', 'True', '1', 1, True]
                
                # Handle numeric fields
                elif isinstance(field, (models.IntegerField, models.DecimalField, models.FloatField)):
                    try:
                        if isinstance(field, models.IntegerField):
                            processed_data[field.name] = int(value)
                        elif isinstance(field, models.DecimalField):
                            from decimal import Decimal
                            processed_data[field.name] = Decimal(str(value))
                        else:
                            processed_data[field.name] = float(value)
                    except (ValueError, TypeError):
                        # Skip invalid numeric values
                        continue
                
                # Handle text fields
                else:
                    processed_data[field.name] = str(value)
        
        return processed_data