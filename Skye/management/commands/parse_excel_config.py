# Create file: Skye/management/commands/parse_excel_config.py
# This will help you convert your Excel mapping to Django configuration

from django.core.management.base import BaseCommand
import openpyxl
import json
from pathlib import Path

class Command(BaseCommand):
    help = 'Parse Excel configuration file and generate page configs'

    def add_arguments(self, parser):
        parser.add_argument('excel_file', type=str, help='Path to Excel file')
        parser.add_argument('--output', type=str, default='config.json', help='Output JSON file')

    def handle(self, *args, **options):
        excel_file = options['excel_file']
        output_file = options['output']
        
        try:
            workbook = openpyxl.load_workbook(excel_file)
            sheet = workbook.active
            
            config = {}
            
            # Skip header row
            for row in sheet.iter_rows(min_row=2, values_only=True):
                if len(row) >= 7 and row[0]:  # Ensure we have all columns and page name
                    page, subpage, table, column, display_name, add_btn, edit_btn = row[:7]
                    
                    if page not in config:
                        config[page] = {}
                    
                    if subpage not in config[page]:
                        config[page][subpage] = {
                            'table': table,
                            'icon': self.get_icon_for_table(table),
                            'columns': [],
                            'add_button': add_btn.lower() == 'yes' if add_btn else False,
                            'edit_button': edit_btn.lower() == 'yes' if edit_btn else False
                        }
                    
                    config[page][subpage]['columns'].append({
                        'db_column': column,
                        'display_name': display_name,
                        'searchable': True
                    })
            
            # Write to JSON file
            with open(output_file, 'w') as f:
                json.dump(config, f, indent=2)
            
            self.stdout.write(
                self.style.SUCCESS(f'Successfully parsed Excel file. Config saved to {output_file}')
            )
            
            # Print summary
            for page, sections in config.items():
                self.stdout.write(f"\n{page}: {len(sections)} sections")
                for section in sections.keys():
                    self.stdout.write(f"  - {section}")
        
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error parsing Excel file: {str(e)}')
            )
    
    def get_icon_for_table(self, table_name):
        """Map table names to Material Icons"""
        icon_mapping = {
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
            'company': 'business',
            'broker': 'person',
            'workflow_standard': 'rule',
            'stage': 'flag',
        }
        return icon_mapping.get(table_name, 'table_chart')