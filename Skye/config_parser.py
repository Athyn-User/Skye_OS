# Create file: Skye/config_parser.py

import json
from collections import defaultdict

class SkyeConfigParser:
    """
    Parses Excel mapping data into Django-usable configuration
    """
    
    # Icon mapping for different section types
    SECTION_ICONS = {
        'venture': 'business',
        'drive': 'storage',
        'employee_location': 'location_on',
        'employee_contact': 'people',
        'products': 'inventory',
        'cover': 'shield',
        'employee_function_detail': 'work',
        'paper': 'description',
        'paper_detail': 'list_alt',
        'applications': 'apps',
        'application_question': 'help',
        'parameter': 'settings',
        'parameter_map': 'map',
        'document': 'folder',
        'task': 'task',
        'workflow': 'workflow',
        'workflow_detail': 'timeline',
        'attachment': 'attach_file',
        'attachment_detail': 'attachment',
        'limits': 'limit',
        'retention': 'schedule',
        'sublimit': 'subdirectory_arrow_right',
        'orders': 'shopping_cart',
        'generation_job': 'play_arrow',
        'data_generation_jobs': 'data_usage',
        # Add more mappings as needed
    }
    
    @classmethod
    def parse_excel_data(cls, excel_data):
        """
        Convert Excel mapping data to page configuration
        Input: List of rows from Excel [page, subpage, table, column, display_name, add_btn, edit_btn]
        Output: Nested dict configuration
        """
        config = defaultdict(lambda: defaultdict(dict))
        
        for row in excel_data:
            if len(row) >= 7:
                page, subpage, table, column, display_name, add_btn, edit_btn = row[:7]
                
                if not config[page][subpage]:
                    config[page][subpage] = {
                        'table': table,
                        'icon': cls.SECTION_ICONS.get(table, 'table_chart'),
                        'columns': [],
                        'add_button': add_btn.lower() == 'yes',
                        'edit_button': edit_btn.lower() == 'yes'
                    }
                
                config[page][subpage]['columns'].append({
                    'db_column': column,
                    'display_name': display_name,
                    'searchable': True  # Default all columns as searchable
                })
        
        return dict(config)
    
    @classmethod
    def get_foreign_key_fields(cls, model_class):
        """
        Extract foreign key fields from Django model for resolution
        """
        fk_fields = []
        for field in model_class._meta.get_fields():
            if field.is_relation and hasattr(field, 'related_model'):
                fk_fields.append({
                    'field_name': field.name,
                    'related_model': field.related_model,
                    'display_field': getattr(field.related_model, '_display_field', 'id')
                })
        return fk_fields
    
    @classmethod
    def generate_catalog_config(cls):
        """
        Generate the complete Catalog page configuration with all 22+ sections
        Using actual Django model names from your database
        """
        return {
            'Catalog': {
                'Venture': {
                    'table': 'venture',
                    'icon': 'business',
                    'columns': [
                        {'db_column': 'venture_id', 'display_name': 'Venture ID'},
                        {'db_column': 'venture_name', 'display_name': 'Venture Name'},
                        {'db_column': 'venture_city', 'display_name': 'City'},
                        {'db_column': 'venture_state', 'display_name': 'State'},
                    ],
                    'add_button': True,
                    'edit_button': True
                },
                'Coverage': {
                    'table': 'coverage',
                    'icon': 'shield',
                    'columns': [
                        {'db_column': 'coverage_id', 'display_name': 'Coverage ID'},
                        {'db_column': 'coverage_name', 'display_name': 'Coverage Name'},
                    ],
                    'add_button': True,
                    'edit_button': True
                },
                'Products': {
                    'table': 'products',
                    'icon': 'inventory',
                    'columns': [
                        {'db_column': 'products_id', 'display_name': 'Product ID'},
                        {'db_column': 'product_name', 'display_name': 'Product Name'},
                        {'db_column': 'product_code', 'display_name': 'Product Code'},
                    ],
                    'add_button': True,
                    'edit_button': True
                },
                'Company': {
                    'table': 'company',
                    'icon': 'business',
                    'columns': [
                        {'db_column': 'company_id', 'display_name': 'Company ID'},
                        {'db_column': 'company_name', 'display_name': 'Company Name'},
                    ],
                    'add_button': True,
                    'edit_button': True
                },
                'Company Contact': {
                    'table': 'companycontact',
                    'icon': 'contact_phone',
                    'columns': [
                        {'db_column': 'company_contact_id', 'display_name': 'Contact ID'},
                        {'db_column': 'company_contact_first', 'display_name': 'First Name'},
                        {'db_column': 'company_contact_last', 'display_name': 'Last Name'},
                        {'db_column': 'company_contact_email', 'display_name': 'Email'},
                    ],
                    'add_button': True,
                    'edit_button': True
                },
                'Company Location': {
                    'table': 'companylocation',
                    'icon': 'location_city',
                    'columns': [
                        {'db_column': 'company_location_id', 'display_name': 'Location ID'},
                        {'db_column': 'company_location_city', 'display_name': 'City'},
                        {'db_column': 'company_location_state', 'display_name': 'State'},
                    ],
                    'add_button': True,
                    'edit_button': True
                },
                'Employee Location': {
                    'table': 'employeelocation',
                    'icon': 'location_on',
                    'columns': [
                        {'db_column': 'employee_location_id', 'display_name': 'Location ID'},
                        {'db_column': 'employee_location_name', 'display_name': 'Location Name'},
                        {'db_column': 'employee_location_city', 'display_name': 'City'},
                    ],
                    'add_button': True,
                    'edit_button': True
                },
                'Employee Contact': {
                    'table': 'employeecontact',
                    'icon': 'people',
                    'columns': [
                        {'db_column': 'employee_id', 'display_name': 'Employee ID'},
                        {'db_column': 'employee_name_first', 'display_name': 'First Name'},
                        {'db_column': 'employee_name_last', 'display_name': 'Last Name'},
                        {'db_column': 'employee_email', 'display_name': 'Email'},
                    ],
                    'add_button': True,
                    'edit_button': True
                },
                'Stage': {
                    'table': 'stage',
                    'icon': 'flag',
                    'columns': [
                        {'db_column': 'stage_id', 'display_name': 'Stage ID'},
                        {'db_column': 'stage_name', 'display_name': 'Stage Name'},
                    ],
                    'add_button': True,
                    'edit_button': True
                },
                'Flow Origin': {
                    'table': 'floworigin',
                    'icon': 'call_split',
                    'columns': [
                        {'db_column': 'flow_origin_id', 'display_name': 'Flow Origin ID'},
                        {'db_column': 'flow_origin_name', 'display_name': 'Flow Origin Name'},
                    ],
                    'add_button': True,
                    'edit_button': True
                },
                'Workflow': {
                    'table': 'workflow',
                    'icon': 'account_tree',
                    'columns': [
                        {'db_column': 'workflow_id', 'display_name': 'Workflow ID'},
                        {'db_column': 'workflow_name', 'display_name': 'Workflow Name'},
                        {'db_column': 'workflow_type', 'display_name': 'Type'},
                    ],
                    'add_button': True,
                    'edit_button': True
                },
                'Task': {
                    'table': 'task',
                    'icon': 'task',
                    'columns': [
                        {'db_column': 'task_id', 'display_name': 'Task ID'},
                        {'db_column': 'task_name', 'display_name': 'Task Name'},
                        {'db_column': 'task_description', 'display_name': 'Description'},
                    ],
                    'add_button': True,
                    'edit_button': True
                },
                'Workflow Detail': {
                    'table': 'workflowdetail',
                    'icon': 'timeline',
                    'columns': [
                        {'db_column': 'workflow_detail_id', 'display_name': 'Detail ID'},
                        {'db_column': 'workflow_sequence', 'display_name': 'Sequence'},
                        {'db_column': 'man_auto', 'display_name': 'Manual/Auto'},
                    ],
                    'add_button': True,
                    'edit_button': True
                },
                'Orders': {
                    'table': 'orders',
                    'icon': 'shopping_cart',
                    'columns': [
                        {'db_column': 'orders_id', 'display_name': 'Order ID'},
                        {'db_column': 'order_created', 'display_name': 'Created'},
                    ],
                    'add_button': True,
                    'edit_button': True
                },
                'Applications': {
                    'table': 'applications',
                    'icon': 'apps',
                    'columns': [
                        {'db_column': 'application_id', 'display_name': 'Application ID'},
                        {'db_column': 'application_name', 'display_name': 'Application Name'},
                    ],
                    'add_button': True,
                    'edit_button': True
                },
                'Parameter Type': {
                    'table': 'parametertype',
                    'icon': 'category',
                    'columns': [
                        {'db_column': 'parameter_type_id', 'display_name': 'Type ID'},
                        {'db_column': 'parameter_type_name', 'display_name': 'Type Name'},
                    ],
                    'add_button': True,
                    'edit_button': True
                },
                'Parameter': {
                    'table': 'parameter',
                    'icon': 'settings',
                    'columns': [
                        {'db_column': 'parameter_id', 'display_name': 'Parameter ID'},
                        {'db_column': 'parameter_name', 'display_name': 'Parameter Name'},
                    ],
                    'add_button': True,
                    'edit_button': True
                },
                'Application Question': {
                    'table': 'applicationquestion',
                    'icon': 'help',
                    'columns': [
                        {'db_column': 'application_question_id', 'display_name': 'Question ID'},
                        {'db_column': 'custom_question', 'display_name': 'Custom Question'},
                    ],
                    'add_button': True,
                    'edit_button': True
                },
                'Application Response': {
                    'table': 'applicationresponse',
                    'icon': 'chat',
                    'columns': [
                        {'db_column': 'application_response_id', 'display_name': 'Response ID'},
                        {'db_column': 'response', 'display_name': 'Response'},
                    ],
                    'add_button': True,
                    'edit_button': True
                },
                'Cover': {
                    'table': 'cover',
                    'icon': 'security',
                    'columns': [
                        {'db_column': 'cover_id', 'display_name': 'Cover ID'},
                        {'db_column': 'cover_name', 'display_name': 'Cover Name'},
                    ],
                    'add_button': True,
                    'edit_button': True
                },
                'Options': {
                    'table': 'options',
                    'icon': 'tune',
                    'columns': [
                        {'db_column': 'options_id', 'display_name': 'Options ID'},
                        {'db_column': 'option_name', 'display_name': 'Option Name'},
                    ],
                    'add_button': True,
                    'edit_button': True
                },
                'Limits': {
                    'table': 'limits',
                    'icon': 'speed',
                    'columns': [
                        {'db_column': 'limits_id', 'display_name': 'Limits ID'},
                        {'db_column': 'limit_text', 'display_name': 'Limit Text'},
                    ],
                    'add_button': True,
                    'edit_button': True
                },
                'Retention': {
                    'table': 'retention',
                    'icon': 'schedule',
                    'columns': [
                        {'db_column': 'retention_id', 'display_name': 'Retention ID'},
                        {'db_column': 'retention_text', 'display_name': 'Retention Text'},
                    ],
                    'add_button': True,
                    'edit_button': True
                },
                'Order Option': {
                    'table': 'orderoption',
                    'icon': 'checklist',
                    'columns': [
                        {'db_column': 'order_option_id', 'display_name': 'Option ID'},
                        {'db_column': 'premium', 'display_name': 'Premium'},
                        {'db_column': 'bound', 'display_name': 'Bound'},
                    ],
                    'add_button': True,
                    'edit_button': True
                },
                'Document': {
                    'table': 'document',
                    'icon': 'description',
                    'columns': [
                        {'db_column': 'document_id', 'display_name': 'Document ID'},
                        {'db_column': 'document_name', 'display_name': 'Document Name'},
                        {'db_column': 'document_number', 'display_name': 'Document Number'},
                    ],
                    'add_button': True,
                    'edit_button': True
                },
                'Broker': {
                    'table': 'broker',
                    'icon': 'person',
                    'columns': [
                        {'db_column': 'broker_id', 'display_name': 'Broker ID'},
                        {'db_column': 'broker_name', 'display_name': 'Broker Name'},
                    ],
                    'add_button': True,
                    'edit_button': True
                },
                'Broker Location': {
                    'table': 'brokerlocation',
                    'icon': 'location_city',
                    'columns': [
                        {'db_column': 'broker_location_id', 'display_name': 'Location ID'},
                        {'db_column': 'broker_city', 'display_name': 'City'},
                        {'db_column': 'broker_zip', 'display_name': 'ZIP'},
                    ],
                    'add_button': True,
                    'edit_button': True
                },
                'Broker Contact': {
                    'table': 'brokercontact',
                    'icon': 'contact_phone',
                    'columns': [
                        {'db_column': 'broker_contact_id', 'display_name': 'Contact ID'},
                        {'db_column': 'broker_first_name', 'display_name': 'First Name'},
                        {'db_column': 'broker_last_name', 'display_name': 'Last Name'},
                        {'db_column': 'broker_email', 'display_name': 'Email'},
                    ],
                    'add_button': True,
                    'edit_button': True
                }
            }
        }