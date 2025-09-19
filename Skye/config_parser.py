# Updated Skye/config_parser.py with all 28 sections

import json
from collections import defaultdict

class SkyeConfigParser:
    """
    Parses Excel mapping data into Django-usable configuration
    Enhanced with all 28+ sections for complete Catalog functionality
    """
    
    # Enhanced icon mapping for all section types
    SECTION_ICONS = {
        'venture': 'business',
        'drive': 'storage',
        'employee_location': 'location_on',
        'employee_contact': 'people',
        'products': 'inventory',
        'cover': 'shield',
        'coverage': 'security',
        'employee_function_detail': 'work',
        'paper': 'description',
        'paper_detail': 'list_alt',
        'applications': 'apps',
        'application_question': 'help',
        'application_response': 'chat',
        'parameter': 'settings',
        'parameter_type': 'category',
        'parameter_map': 'map',
        'document': 'folder',
        'task': 'task',
        'workflow': 'account_tree',
        'workflow_detail': 'timeline',
        'stage': 'flag',
        'flow_origin': 'call_split',
        'attachment': 'attach_file',
        'attachment_detail': 'attachment',
        'limits': 'speed',
        'retention': 'schedule',
        'sublimit': 'subdirectory_arrow_right',
        'orders': 'shopping_cart',
        'order_option': 'checklist',
        'options': 'tune',
        'generation_job': 'play_arrow',
        'data_generation_jobs': 'data_usage',
        'company': 'business',
        'company_contact': 'contact_phone',
        'company_location': 'location_city',
        'broker': 'person',
        'broker_location': 'location_city',
        'broker_contact': 'contact_phone',
        'workflow_standard': 'rule',
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
        Generate the complete Catalog page configuration with all 28+ sections
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
                        {'db_column': 'venture_zip', 'display_name': 'ZIP Code'},
                    ],
                    'add_button': True,
                    'edit_button': True
                },
                'Drive': {
                    'table': 'drive',
                    'icon': 'storage',
                    'columns': [
                        {'db_column': 'drive_id', 'display_name': 'Drive ID'},
                        {'db_column': 'drive_name', 'display_name': 'Drive Name'},
                        {'db_column': 'venture_id', 'display_name': 'Venture'},
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
                        {'db_column': 'employee_location_state', 'display_name': 'State'},
                        {'db_column': 'venture', 'display_name': 'Venture'},
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
                        {'db_column': 'employee_location', 'display_name': 'Location'},
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
                        {'db_column': 'venture', 'display_name': 'Venture'},
                        {'db_column': 'coverage', 'display_name': 'Coverage'},
                    ],
                    'add_button': True,
                    'edit_button': True
                },
                'Coverage': {
                    'table': 'coverage',
                    'icon': 'security',
                    'columns': [
                        {'db_column': 'coverage_id', 'display_name': 'Coverage ID'},
                        {'db_column': 'coverage_name', 'display_name': 'Coverage Name'},
                    ],
                    'add_button': True,
                    'edit_button': True
                },
                'Cover': {
                    'table': 'cover',
                    'icon': 'shield',
                    'columns': [
                        {'db_column': 'cover_id', 'display_name': 'Cover ID'},
                        {'db_column': 'cover_name', 'display_name': 'Cover Name'},
                        {'db_column': 'product', 'display_name': 'Product'},
                    ],
                    'add_button': True,
                    'edit_button': True
                },
                'Employee Function': {
                    'table': 'employee_function_detail',
                    'icon': 'work',
                    'columns': [
                        {'db_column': 'employee_function_detail_id', 'display_name': 'Function ID'},
                        {'db_column': 'employee_id', 'display_name': 'Employee'},
                        {'db_column': 'employee_function_id', 'display_name': 'Function'},
                        {'db_column': 'product_id', 'display_name': 'Product'},
                        {'db_column': 'cloud_name', 'display_name': 'Cloud Name'},
                    ],
                    'add_button': True,
                    'edit_button': True
                },
                'Paper': {
                    'table': 'paper',
                    'icon': 'description',
                    'columns': [
                        {'db_column': 'paper_id', 'display_name': 'Paper ID'},
                        {'db_column': 'paper_name', 'display_name': 'Paper Name'},
                        {'db_column': 'am_best_rating', 'display_name': 'AM Best Rating'},
                        {'db_column': 'am_best_financial_size', 'display_name': 'Financial Size'},
                    ],
                    'add_button': True,
                    'edit_button': True
                },
                'Paper Detail': {
                    'table': 'paper_detail',
                    'icon': 'list_alt',
                    'columns': [
                        {'db_column': 'paper_detail_id', 'display_name': 'Detail ID'},
                        {'db_column': 'products_id', 'display_name': 'Product'},
                        {'db_column': 'paper_id', 'display_name': 'Paper'},
                        {'db_column': 'paper_percentage', 'display_name': 'Percentage'},
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
                        {'db_column': 'product', 'display_name': 'Product'},
                    ],
                    'add_button': True,
                    'edit_button': True
                },
                'Application Question': {
                    'table': 'applicationquestion',
                    'icon': 'help',
                    'columns': [
                        {'db_column': 'application_question_id', 'display_name': 'Question ID'},
                        {'db_column': 'application', 'display_name': 'Application'},
                        {'db_column': 'custom_question', 'display_name': 'Question Text'},
                        {'db_column': 'parameter', 'display_name': 'Parameter'},
                    ],
                    'add_button': True,
                    'edit_button': True
                },
                'Application Response': {
                    'table': 'applicationresponse',
                    'icon': 'chat',
                    'columns': [
                        {'db_column': 'application_response_id', 'display_name': 'Response ID'},
                        {'db_column': 'application', 'display_name': 'Application'},
                        {'db_column': 'application_question', 'display_name': 'Question'},
                        {'db_column': 'response', 'display_name': 'Response'},
                        {'db_column': 'order', 'display_name': 'Order'},
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
                        {'db_column': 'parameter_type', 'display_name': 'Type'},
                        {'db_column': 'parameter_quote', 'display_name': 'Quote'},
                        {'db_column': 'parameter_binder', 'display_name': 'Binder'},
                        {'db_column': 'parameter_policy', 'display_name': 'Policy'},
                    ],
                    'add_button': True,
                    'edit_button': True
                },
                'Parameter Map': {
                    'table': 'parameter_map',
                    'icon': 'map',
                    'columns': [
                        {'db_column': 'parameter_map_id', 'display_name': 'Map ID'},
                        {'db_column': 'products_id', 'display_name': 'Product'},
                        {'db_column': 'parameter_id', 'display_name': 'Parameter'},
                        {'db_column': 'console_element', 'display_name': 'Console Element'},
                        {'db_column': 'quote_item', 'display_name': 'Quote Item'},
                        {'db_column': 'binder_item', 'display_name': 'Binder Item'},
                        {'db_column': 'policy_item', 'display_name': 'Policy Item'},
                    ],
                    'add_button': True,
                    'edit_button': True
                },
                'Document': {
                    'table': 'document',
                    'icon': 'folder',
                    'columns': [
                        {'db_column': 'document_id', 'display_name': 'Document ID'},
                        {'db_column': 'document_name', 'display_name': 'Document Name'},
                        {'db_column': 'product', 'display_name': 'Product'},
                        {'db_column': 'document_number', 'display_name': 'Document Number'},
                        {'db_column': 'default_document', 'display_name': 'Default'},
                        {'db_column': 'document_code', 'display_name': 'Document Code'},
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
                        {'db_column': 'task_display', 'display_name': 'Display'},
                        {'db_column': 'subroutine_name', 'display_name': 'Subroutine'},
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
                'Workflow Detail': {
                    'table': 'workflowdetail',
                    'icon': 'timeline',
                    'columns': [
                        {'db_column': 'workflow_detail_id', 'display_name': 'Detail ID'},
                        {'db_column': 'workflow', 'display_name': 'Workflow'},
                        {'db_column': 'stage', 'display_name': 'Stage'},
                        {'db_column': 'task', 'display_name': 'Task'},
                        {'db_column': 'workflow_sequence', 'display_name': 'Sequence'},
                        {'db_column': 'man_auto', 'display_name': 'Manual/Auto'},
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
                'Attachment': {
                    'table': 'attachment',
                    'icon': 'attach_file',
                    'columns': [
                        {'db_column': 'attachment_id', 'display_name': 'Attachment ID'},
                        {'db_column': 'attachment_name', 'display_name': 'Attachment Name'},
                    ],
                    'add_button': True,
                    'edit_button': True
                },
                'Attachment Detail': {
                    'table': 'attachment_detail',
                    'icon': 'attachment',
                    'columns': [
                        {'db_column': 'attachment_detail_id', 'display_name': 'Detail ID'},
                        {'db_column': 'attachment_id', 'display_name': 'Attachment'},
                        {'db_column': 'product_id', 'display_name': 'Product'},
                        {'db_column': 'task_id', 'display_name': 'Task'},
                        {'db_column': 'attachment_type_id', 'display_name': 'Type'},
                    ],
                    'add_button': True,
                    'edit_button': True
                },
                'Limits': {
                    'table': 'limits',
                    'icon': 'speed',
                    'columns': [
                        {'db_column': 'limits_id', 'display_name': 'Limits ID'},
                        {'db_column': 'product', 'display_name': 'Product'},
                        {'db_column': 'cover', 'display_name': 'Cover'},
                        {'db_column': 'limit_text', 'display_name': 'Limit Text'},
                        {'db_column': 'limit_pc_number', 'display_name': 'PC Number'},
                        {'db_column': 'limit_ag_number', 'display_name': 'AG Number'},
                    ],
                    'add_button': True,
                    'edit_button': True
                },
                'Retention': {
                    'table': 'retention',
                    'icon': 'schedule',
                    'columns': [
                        {'db_column': 'retention_id', 'display_name': 'Retention ID'},
                        {'db_column': 'products', 'display_name': 'Product'},
                        {'db_column': 'cover', 'display_name': 'Cover'},
                        {'db_column': 'retention_text', 'display_name': 'Retention Text'},
                        {'db_column': 'retention_pc_number', 'display_name': 'PC Number'},
                        {'db_column': 'retention_ag_number', 'display_name': 'AG Number'},
                    ],
                    'add_button': True,
                    'edit_button': True
                },
                'Sublimit': {
                    'table': 'sublimit',
                    'icon': 'subdirectory_arrow_right',
                    'columns': [
                        {'db_column': 'sublimit_id', 'display_name': 'Sublimit ID'},
                        {'db_column': 'orders_id', 'display_name': 'Order'},
                        {'db_column': 'products_id', 'display_name': 'Product'},
                        {'db_column': 'sublimit_name', 'display_name': 'Sublimit Name'},
                        {'db_column': 'sublimit_amount', 'display_name': 'Amount'},
                    ],
                    'add_button': True,
                    'edit_button': True
                },
                'Orders': {
                    'table': 'orders',
                    'icon': 'shopping_cart',
                    'columns': [
                        {'db_column': 'orders_id', 'display_name': 'Order ID'},
                        {'db_column': 'company', 'display_name': 'Company'},
                        {'db_column': 'products', 'display_name': 'Product'},
                        {'db_column': 'stage', 'display_name': 'Stage'},
                        {'db_column': 'employee', 'display_name': 'Employee'},
                        {'db_column': 'order_created', 'display_name': 'Created'},
                    ],
                    'add_button': True,
                    'edit_button': True
                },
                'Order Option': {
                    'table': 'orderoption',
                    'icon': 'checklist',
                    'columns': [
                        {'db_column': 'order_option_id', 'display_name': 'Option ID'},
                        {'db_column': 'orders', 'display_name': 'Order'},
                        {'db_column': 'options', 'display_name': 'Option'},
                        {'db_column': 'cover', 'display_name': 'Cover'},
                        {'db_column': 'order_option_include', 'display_name': 'Include'},
                        {'db_column': 'premium', 'display_name': 'Premium'},
                        {'db_column': 'bound', 'display_name': 'Bound'},
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
                        {'db_column': 'company', 'display_name': 'Company'},
                        {'db_column': 'company_contact_first', 'display_name': 'First Name'},
                        {'db_column': 'company_contact_last', 'display_name': 'Last Name'},
                        {'db_column': 'company_contact_email', 'display_name': 'Email'},
                        {'db_column': 'company_contact_phone', 'display_name': 'Phone'},
                    ],
                    'add_button': True,
                    'edit_button': True
                },
                'Company Location': {
                    'table': 'companylocation',
                    'icon': 'location_city',
                    'columns': [
                        {'db_column': 'company_location_id', 'display_name': 'Location ID'},
                        {'db_column': 'company', 'display_name': 'Company'},
                        {'db_column': 'company_location_city', 'display_name': 'City'},
                        {'db_column': 'company_location_state', 'display_name': 'State'},
                        {'db_column': 'company_location_zip', 'display_name': 'ZIP'},
                        {'db_column': 'company_mailing', 'display_name': 'Mailing'},
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
                        {'db_column': 'broker', 'display_name': 'Broker'},
                        {'db_column': 'broker_city', 'display_name': 'City'},
                        {'db_column': 'broker_state_id', 'display_name': 'State ID'},
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
                        {'db_column': 'broker_location', 'display_name': 'Location'},
                        {'db_column': 'broker_first_name', 'display_name': 'First Name'},
                        {'db_column': 'broker_last_name', 'display_name': 'Last Name'},
                        {'db_column': 'broker_email', 'display_name': 'Email'},
                    ],
                    'add_button': True,
                    'edit_button': True
                }
            }
        }