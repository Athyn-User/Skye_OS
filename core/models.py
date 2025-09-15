# core/models.py
# Complete Django Models for all database tables

from django.db import models

# Base models (no foreign keys)
class AttachmentType(models.Model):
    attachment_type_id = models.AutoField(primary_key=True)
    attachment_type_name = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'attachment_type'

    def __str__(self):
        return self.attachment_type_name or f"AttachmentType {self.attachment_type_id}"

class Broker(models.Model):
    broker_id = models.AutoField(primary_key=True)
    broker_name = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'broker'

    def __str__(self):
        return self.broker_name or f"Broker {self.broker_id}"

class Cloud(models.Model):
    cloud_id = models.AutoField(primary_key=True)
    cloud_name = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'cloud'

    def __str__(self):
        return self.cloud_name or f"Cloud {self.cloud_id}"

class Company(models.Model):
    company_id = models.AutoField(primary_key=True)
    company_name = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'company'

    def __str__(self):
        return self.company_name or f"Company {self.company_id}"

class Coverage(models.Model):
    coverage_id = models.AutoField(primary_key=True)
    coverage_name = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'coverage'

    def __str__(self):
        return self.coverage_name or f"Coverage {self.coverage_id}"

class EmployeeFunction(models.Model):
    employee_function_id = models.AutoField(primary_key=True)
    employee_function = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'employee_function'

    def __str__(self):
        return self.employee_function or f"EmployeeFunction {self.employee_function_id}"

class FlowOrigin(models.Model):
    flow_origin_id = models.AutoField(primary_key=True)
    flow_origin_name = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'flow_origin'

    def __str__(self):
        return self.flow_origin_name or f"FlowOrigin {self.flow_origin_id}"

class GenerationModel(models.Model):
    generation_model_id = models.AutoField(primary_key=True)
    generation_model_name = models.TextField(blank=True, null=True)
    python_exe_file = models.TextField(blank=True, null=True)
    python_file_path = models.TextField(blank=True, null=True)
    jupyter_file_path = models.TextField(blank=True, null=True)
    model_filename = models.TextField(blank=True, null=True)
    model_code = models.TextField(blank=True, null=True)
    py_file = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'generation_model'

    def __str__(self):
        return self.generation_model_name or f"GenerationModel {self.generation_model_id}"

class InputOutput(models.Model):
    input_output_id = models.AutoField(primary_key=True)
    input_output_name = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'input_output'

    def __str__(self):
        return self.input_output_name or f"InputOutput {self.input_output_id}"

class Options(models.Model):
    options_id = models.AutoField(primary_key=True)
    option_name = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'options'

    def __str__(self):
        return self.option_name or f"Options {self.options_id}"

class Paper(models.Model):
    paper_id = models.AutoField(primary_key=True)
    paper_name = models.TextField(blank=True, null=True)
    am_best_rating = models.TextField(blank=True, null=True)
    am_best_financial_size = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'paper'

    def __str__(self):
        return self.paper_name or f"Paper {self.paper_id}"

class ParameterDoc(models.Model):
    parameter_doc_id = models.AutoField(primary_key=True)
    parameter_doc_name = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'parameter_doc'

    def __str__(self):
        return self.parameter_doc_name or f"ParameterDoc {self.parameter_doc_id}"

class ParameterType(models.Model):
    parameter_type_id = models.AutoField(primary_key=True)
    parameter_type_name = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'parameter_type'

    def __str__(self):
        return self.parameter_type_name or f"ParameterType {self.parameter_type_id}"

class Stage(models.Model):
    stage_id = models.AutoField(primary_key=True)
    stage_name = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'stage'

    def __str__(self):
        return self.stage_name or f"Stage {self.stage_id}"

class Task(models.Model):
    task_id = models.AutoField(primary_key=True)
    task_name = models.TextField(blank=True, null=True)
    task_description = models.TextField(blank=True, null=True)
    task_display = models.TextField(blank=True, null=True)
    subroutine_name = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'task'

    def __str__(self):
        return self.task_name or f"Task {self.task_id}"

class TrainingModel(models.Model):
    training_model_id = models.AutoField(primary_key=True)
    model_name = models.TextField(blank=True, null=True)
    python_exe_file = models.TextField(blank=True, null=True)
    python_file_path = models.TextField(blank=True, null=True)
    jupyter_file_path = models.TextField(blank=True, null=True)
    model_filename = models.TextField(blank=True, null=True)
    model_code = models.TextField(blank=True, null=True)
    py_file = models.TextField(blank=True, null=True)
    pickle_dump = models.TextField(blank=True, null=True)
    inference_py_file = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'training_model'

    def __str__(self):
        return self.model_name or f"TrainingModel {self.training_model_id}"

class Venture(models.Model):
    venture_id = models.AutoField(primary_key=True)
    venture_name = models.TextField(blank=True, null=True)
    venture_address_1 = models.TextField(blank=True, null=True)
    venture_address_2 = models.TextField(blank=True, null=True)
    venture_city = models.TextField(blank=True, null=True)
    venture_state = models.TextField(blank=True, null=True)
    venture_zip = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'venture'

    def __str__(self):
        return self.venture_name or f"Venture {self.venture_id}"

class WorkflowType(models.Model):
    workflow_type_id = models.AutoField(primary_key=True)
    workflow_type_name = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'workflow_type'

    def __str__(self):
        return self.workflow_type_name or f"WorkflowType {self.workflow_type_id}"

class Parameter(models.Model):
    parameter_id = models.AutoField(primary_key=True)
    parameter_name = models.TextField(blank=True, null=True)
    parameter_type_id = models.IntegerField(blank=True, null=True)
    parameter_docs = models.TextField(blank=True, null=True)
    parameter_quote = models.BooleanField(blank=True, null=True)
    parameter_binder = models.BooleanField(blank=True, null=True)
    parameter_policy = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'parameter'

    def __str__(self):
        return self.parameter_name or f"Parameter {self.parameter_id}"

# Models with 1 level foreign keys
class BrokerLocation(models.Model):
    broker_location_id = models.AutoField(primary_key=True)
    broker = models.ForeignKey(Broker, models.DO_NOTHING, blank=True, null=True)
    broker_address_1 = models.TextField(blank=True, null=True)
    broker_address_2 = models.TextField(blank=True, null=True)
    broker_city = models.TextField(blank=True, null=True)
    broker_state_id = models.IntegerField(blank=True, null=True)
    broker_zip = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'broker_location'

    def __str__(self):
        return f"BrokerLocation {self.broker_location_id}"

class CompanyAlias(models.Model):
    company_alias_id = models.AutoField(primary_key=True)
    company = models.ForeignKey(Company, models.DO_NOTHING, blank=True, null=True)
    company_alias_name = models.TextField(blank=True, null=True)
    company_alias_retro_start = models.DateField(blank=True, null=True)
    company_alias_retro_end = models.DateField(blank=True, null=True)
    company_alias_eff_dte = models.DateField(blank=True, null=True)
    company_alias_exp_dte = models.DateField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'company_alias'

    def __str__(self):
        return self.company_alias_name or f"CompanyAlias {self.company_alias_id}"

class CompanyContact(models.Model):
    company_contact_id = models.AutoField(primary_key=True)
    company = models.ForeignKey(Company, models.DO_NOTHING, blank=True, null=True)
    company_contact_first = models.TextField(blank=True, null=True)
    company_contact_last = models.TextField(blank=True, null=True)
    company_contact_phone = models.TextField(blank=True, null=True)
    company_contact_email = models.TextField(blank=True, null=True)
    company_contact_title = models.TextField(blank=True, null=True)
    company_contact_salutation = models.TextField(blank=True, null=True)
    company_web = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'company_contact'

    def __str__(self):
        return self.company_contact_title or f"CompanyContact {self.company_contact_id}"

class CompanyLocation(models.Model):
    company_location_id = models.AutoField(primary_key=True)
    company = models.ForeignKey(Company, models.DO_NOTHING, blank=True, null=True)
    company_location_address_1 = models.TextField(blank=True, null=True)
    company_location_address_2 = models.TextField(blank=True, null=True)
    company_location_city = models.TextField(blank=True, null=True)
    company_location_state = models.TextField(blank=True, null=True)
    company_location_zip = models.TextField(blank=True, null=True)
    company_mailing = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'company_location'

    def __str__(self):
        return f"CompanyLocation {self.company_location_id}"

class Drive(models.Model):
    drive_id = models.AutoField(primary_key=True)
    drive_name = models.TextField(blank=True, null=True)
    venture = models.ForeignKey(Venture, on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'drive'

    def __str__(self):
        return self.drive_name or f"Drive {self.drive_id}"

class EmployeeLocation(models.Model):
    employee_location_id = models.AutoField(primary_key=True)
    venture = models.ForeignKey(Venture, on_delete=models.CASCADE, blank=True, null=True)
    employee_location_name = models.TextField(blank=True, null=True)
    employee_location_address_1 = models.TextField(blank=True, null=True)
    employee_location_address_2 = models.TextField(blank=True, null=True)
    employee_location_city = models.TextField(blank=True, null=True)
    employee_location_state = models.TextField(blank=True, null=True)
    employee_location_zip = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'employee_location'

    def __str__(self):
        return self.employee_location_name or f"Location {self.employee_location_id}"

class GenerationJob(models.Model):
    generation_job_id = models.AutoField(primary_key=True)
    generator_model_id = models.IntegerField(blank=True, null=True)
    product_id = models.IntegerField(blank=True, null=True)
    data_seed_id = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'generation_job'

    def __str__(self):
        return f"Generation Job {self.generation_job_id}"

class Products(models.Model):
    products_id = models.AutoField(primary_key=True)
    product_name = models.TextField(blank=True, null=True)
    venture = models.ForeignKey(Venture, models.DO_NOTHING, blank=True, null=True)
    coverage = models.ForeignKey(Coverage, models.DO_NOTHING, blank=True, null=True)
    product_code = models.TextField(blank=True, null=True)
    product_prefix = models.TextField(blank=True, null=True)
    documents_name = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'products'

    def __str__(self):
        return self.product_name or f"Product {self.products_id}"

class Workflow(models.Model):
    workflow_id = models.AutoField(primary_key=True)
    workflow_name = models.TextField(blank=True, null=True)
    workflow_type = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'workflow'

    def __str__(self):
        return self.workflow_name or f"Workflow {self.workflow_id}"

# Models with 2 level foreign keys
class Attachment(models.Model):
    attachment_id = models.AutoField(primary_key=True)
    attachment_name = models.TextField(blank=True, null=True)
    output_description = models.TextField(blank=True, null=True)
    attachment_type = models.ForeignKey(AttachmentType, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'attachment'

    def __str__(self):
        return self.attachment_name or f"Attachment {self.attachment_id}"

class BrokerContact(models.Model):
    broker_contact_id = models.AutoField(primary_key=True)
    broker_location = models.ForeignKey(BrokerLocation, models.DO_NOTHING, blank=True, null=True)
    broker_first_name = models.TextField(blank=True, null=True)
    broker_last_name = models.TextField(blank=True, null=True)
    broker_email = models.TextField(blank=True, null=True)
    broker_name_combined = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'broker_contact'

    def __str__(self):
        return self.broker_first_name or f"BrokerContact {self.broker_contact_id}"

class Cover(models.Model):
    cover_id = models.AutoField(primary_key=True)
    cover_name = models.TextField(blank=True, null=True)
    product = models.ForeignKey(Products, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'cover'

    def __str__(self):
        return self.cover_name or f"Cover {self.cover_id}"

class DataSeed(models.Model):
    data_seed_id = models.AutoField(primary_key=True)
    data_seed_filename = models.TextField(blank=True, null=True)
    show_seed = models.BooleanField(blank=True, null=True)
    product = models.ForeignKey(Products, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'data_seed'

    def __str__(self):
        return self.data_seed_filename or f"DataSeed {self.data_seed_id}"

class Document(models.Model):
    document_id = models.AutoField(primary_key=True)
    document_name = models.TextField(blank=True, null=True)
    product = models.ForeignKey(Products, models.DO_NOTHING, blank=True, null=True)
    document_number = models.TextField(blank=True, null=True)
    default_document = models.BooleanField(blank=True, null=True)
    document_added = models.DateTimeField(blank=True, null=True)
    document_expiration = models.DateTimeField(blank=True, null=True)
    document_prior_version = models.IntegerField(blank=True, null=True)
    document_code = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'document'

    def __str__(self):
        return self.document_name or f"Document {self.document_id}"

class EmployeeContact(models.Model):
    employee_id = models.AutoField(primary_key=True)
    employee_location = models.ForeignKey(EmployeeLocation, models.DO_NOTHING, blank=True, null=True)
    employee_name_first = models.TextField(blank=True, null=True)
    employee_name_last = models.TextField(blank=True, null=True)
    employee_email = models.TextField(blank=True, null=True)
    employee_name_combined = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'employee_contact'

    def __str__(self):
        return self.employee_name_first or f"EmployeeContact {self.employee_id}"

class Limits(models.Model):
    limits_id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Products, models.DO_NOTHING, blank=True, null=True)
    cover = models.ForeignKey(Cover, models.DO_NOTHING, blank=True, null=True)
    limit_text = models.TextField(blank=True, null=True)
    limit_pc_number = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    limit_ag_number = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'limits'

    def __str__(self):
        return self.limit_text or f"Limits {self.limits_id}"

class PaperDetail(models.Model):
    paper_detail_id = models.AutoField(primary_key=True)
    products = models.ForeignKey(Products, models.DO_NOTHING, blank=True, null=True)
    paper = models.ForeignKey(Paper, models.DO_NOTHING, blank=True, null=True)
    paper_percentage = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'paper_detail'

    def __str__(self):
        return f"PaperDetail {self.paper_detail_id}"

class Retention(models.Model):
    retention_id = models.AutoField(primary_key=True)
    products = models.ForeignKey(Products, models.DO_NOTHING, blank=True, null=True)
    cover_id = models.IntegerField(blank=True, null=True)
    retention_text = models.TextField(blank=True, null=True)
    retention_pc_number = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    retention_ag_number = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'retention'

    def __str__(self):
        return self.retention_text or f"Retention {self.retention_id}"

class TrainingJob(models.Model):
    training_job_id = models.AutoField(primary_key=True)
    training_model = models.ForeignKey(TrainingModel, models.DO_NOTHING, blank=True, null=True)
    products = models.ForeignKey(Products, models.DO_NOTHING, blank=True, null=True)
    data_set_id = models.TextField(blank=True, null=True)
    pickle_file_name = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'training_job'

    def __str__(self):
        return self.pickle_file_name or f"TrainingJob {self.training_job_id}"

class WorkflowDetail(models.Model):
    workflow_detail_id = models.AutoField(primary_key=True)
    workflow = models.ForeignKey(Workflow, models.DO_NOTHING, blank=True, null=True)
    stage_id = models.IntegerField(blank=True, null=True)
    task = models.ForeignKey(Task, models.DO_NOTHING, blank=True, null=True)
    workflow_sequence = models.IntegerField(blank=True, null=True)
    man_auto = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'workflow_detail'

    def __str__(self):
        return f"WorkflowDetail {self.workflow_detail_id}"

class WorkflowStandard(models.Model):
    workflow_standard_id = models.AutoField(primary_key=True)
    workflow_type = models.TextField(blank=True, null=True)
    stage_id = models.IntegerField(blank=True, null=True)
    next_stage_id = models.IntegerField(blank=True, null=True)
    task = models.ForeignKey(Task, models.DO_NOTHING, blank=True, null=True)
    workflow_sequence = models.TextField(blank=True, null=True)
    man_auto = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'workflow_standard'

    def __str__(self):
        return f"WorkflowStandard {self.workflow_standard_id}"

# More complex models with multiple foreign keys
class Orders(models.Model):
    orders_id = models.AutoField(primary_key=True)
    stage = models.ForeignKey(Stage, models.DO_NOTHING, blank=True, null=True)
    employee = models.ForeignKey(EmployeeContact, models.DO_NOTHING, blank=True, null=True)
    flow_origin = models.ForeignKey(FlowOrigin, models.DO_NOTHING, blank=True, null=True)
    company = models.ForeignKey(Company, models.DO_NOTHING, blank=True, null=True)
    products = models.ForeignKey(Products, models.DO_NOTHING, blank=True, null=True)
    venture = models.ForeignKey(Venture, models.DO_NOTHING, blank=True, null=True)
    order_created = models.DateTimeField(blank=True, null=True)
    workflow = models.ForeignKey(Workflow, models.DO_NOTHING, blank=True, null=True)
    workflow_detail = models.ForeignKey(WorkflowDetail, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'orders'

    def __str__(self):
        return f"Order {self.orders_id}"

# Models that depend on Orders
class AttachmentLog(models.Model):
    attachment_log_id = models.AutoField(primary_key=True)
    order = models.ForeignKey(Orders, models.DO_NOTHING, blank=True, null=True)
    attachment_type = models.ForeignKey(AttachmentType, models.DO_NOTHING, blank=True, null=True)
    document_name = models.TextField(blank=True, null=True)
    document_timestamp = models.DateTimeField(blank=True, null=True)
    document_path = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'attachment_log'

    def __str__(self):
        return self.document_name or f"AttachmentLog {self.attachment_log_id}"

class EmailLog(models.Model):
    email_log_id = models.AutoField(primary_key=True)
    order_id = models.IntegerField(blank=True, null=True)
    sent_time = models.TimeField(blank=True, null=True)
    subject = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'email_log'

    def __str__(self):
        return self.subject or f"EmailLog {self.email_log_id}"

class OrderData(models.Model):
    order_data_id = models.AutoField(primary_key=True)
    orders = models.ForeignKey(Orders, models.DO_NOTHING, blank=True, null=True)
    employee_count = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'order_data'

    def __str__(self):
        return f"OrderData {self.order_data_id}"

class OrderOption(models.Model):
    order_option_id = models.AutoField(primary_key=True)
    orders = models.ForeignKey(Orders, models.DO_NOTHING, blank=True, null=True)
    options = models.ForeignKey(Options, models.DO_NOTHING, blank=True, null=True)
    cover = models.ForeignKey(Cover, models.DO_NOTHING, blank=True, null=True)
    order_option_include = models.BooleanField(blank=True, null=True)
    retention = models.ForeignKey(Retention, models.DO_NOTHING, blank=True, null=True)
    limits = models.ForeignKey(Limits, models.DO_NOTHING, blank=True, null=True)
    premium = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    bound = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'order_option'

    def __str__(self):
        return f"OrderOption {self.order_option_id}"

class Sublimit(models.Model):
    sublimit_id = models.AutoField(primary_key=True)
    orders = models.ForeignKey(Orders, models.DO_NOTHING, blank=True, null=True)
    products = models.ForeignKey(Products, models.DO_NOTHING, blank=True, null=True)
    sublimit_name = models.TextField(blank=True, null=True)
    sublimit_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'sublimit'

    def __str__(self):
        return self.sublimit_name or f"Sublimit {self.sublimit_id}"

# Additional complex models
class AttachmentDetail(models.Model):
    attachment_detail_id = models.AutoField(primary_key=True)
    attachment = models.ForeignKey(Attachment, models.DO_NOTHING, blank=True, null=True)
    product = models.ForeignKey(Products, models.DO_NOTHING, blank=True, null=True)
    task = models.ForeignKey(Task, models.DO_NOTHING, blank=True, null=True)
    attachment_type = models.ForeignKey(AttachmentType, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'attachment_detail'

    def __str__(self):
        return f"AttachmentDetail {self.attachment_detail_id}"

class DocumentDetail(models.Model):
    document_detail_id = models.AutoField(primary_key=True)
    order_option = models.ForeignKey(OrderOption, models.DO_NOTHING, blank=True, null=True)
    document = models.ForeignKey(Document, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'document_detail'

    def __str__(self):
        return f"DocumentDetail {self.document_detail_id}"

class EmployeeFunctionDetail(models.Model):
    employee_function_detail_id = models.AutoField(primary_key=True)
    employee = models.ForeignKey(EmployeeContact, models.DO_NOTHING, blank=True, null=True)
    employee_function = models.ForeignKey(EmployeeFunction, models.DO_NOTHING, blank=True, null=True)
    product = models.ForeignKey(Products, models.DO_NOTHING, blank=True, null=True)
    cloud_name = models.TextField(blank=True, null=True)
    iam = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'employee_function_detail'

    def __str__(self):
        return self.cloud_name or f"EmployeeFunctionDetail {self.employee_function_detail_id}"

class GenerationLog(models.Model):
    output_id = models.AutoField(primary_key=True)
    model_code = models.TextField(blank=True, null=True)
    output_file_name = models.TextField(blank=True, null=True)
    product = models.TextField(blank=True, null=True)
    output_id_2 = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'generation_log'

    def __str__(self):
        return self.output_file_name or f"GenerationLog {self.output_id}"

class ModelParameter(models.Model):
    model_parameter_id = models.AutoField(primary_key=True)
    training_job = models.ForeignKey(TrainingJob, models.DO_NOTHING, blank=True, null=True)
    parameter = models.ForeignKey(Parameter, models.DO_NOTHING, blank=True, null=True)
    input_output = models.ForeignKey(InputOutput, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'model_parameter'

    def __str__(self):
        return f"ModelParameter {self.model_parameter_id}"

class OrderDataVert(models.Model):
    order_date_vert_id = models.AutoField(primary_key=True)
    order = models.ForeignKey(Orders, models.DO_NOTHING, blank=True, null=True)
    parameter = models.ForeignKey(Parameter, models.DO_NOTHING, blank=True, null=True)
    vert_value = models.TextField(blank=True, null=True)
    parameter_map = models.ForeignKey('ParameterMap', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'order_data_vert'

    def __str__(self):
        return f"OrderDataVert {self.order_date_vert_id}"

class ParameterMap(models.Model):
    parameter_map_id = models.AutoField(primary_key=True)
    products = models.ForeignKey(Products, models.DO_NOTHING, blank=True, null=True)
    parameter = models.ForeignKey(Parameter, models.DO_NOTHING, blank=True, null=True)
    console_element = models.BooleanField(blank=True, null=True)
    quote_item = models.BooleanField(blank=True, null=True)
    binder_item = models.BooleanField(blank=True, null=True)
    policy_item = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'parameter_map'

    def __str__(self):
        return f"ParameterMap {self.parameter_map_id}"

class ParametersStandard(models.Model):
    parameters_standard_id = models.AutoField(primary_key=True)
    coverage = models.ForeignKey(Coverage, models.DO_NOTHING, blank=True, null=True)
    parameter = models.ForeignKey(Parameter, models.DO_NOTHING, blank=True, null=True)
    parameter_map_seq = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'parameters_standard'

    def __str__(self):
        return f"ParametersStandard {self.parameters_standard_id}"

class SublimitDetail(models.Model):
    sublimit_detail_id = models.AutoField(primary_key=True)
    orders = models.ForeignKey(Orders, models.DO_NOTHING, blank=True, null=True)
    sublimit = models.ForeignKey(Sublimit, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'sublimit_detail'

    def __str__(self):
        return f"SublimitDetail {self.sublimit_detail_id}"

class UlProgram(models.Model):
    ul_program_id = models.AutoField(primary_key=True)
    order_id = models.IntegerField(blank=True, null=True)
    paper_id = models.IntegerField(blank=True, null=True)
    limit_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'ul_program'

    def __str__(self):
        return f"UlProgram {self.ul_program_id}"

# Application related models
class Applications(models.Model):
    application_id = models.AutoField(primary_key=True)
    application_name = models.TextField(blank=True, null=True)
    product = models.ForeignKey('Product', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'applications'

    def __str__(self):
        return self.application_name or f"Applications {self.application_id}"

class ApplicationQuestion(models.Model):
    application_question_id = models.AutoField(primary_key=True)
    application = models.ForeignKey(Applications, models.DO_NOTHING, blank=True, null=True)
    custom_question = models.TextField(blank=True, null=True)
    parameter = models.ForeignKey(Parameter, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'application_question'

    def __str__(self):
        return f"ApplicationQuestion {self.application_question_id}"

class ApplicationResponse(models.Model):
    application_response_id = models.AutoField(primary_key=True)
    application = models.ForeignKey(Applications, models.DO_NOTHING, blank=True, null=True)
    application_question = models.ForeignKey(ApplicationQuestion, models.DO_NOTHING, blank=True, null=True)
    order = models.ForeignKey(Orders, models.DO_NOTHING, blank=True, null=True)
    response = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'application_response'

    def __str__(self):
        return f"ApplicationResponse {self.application_response_id}"

# Legacy Product model (separate from Products)
class Product(models.Model):
    product_id = models.AutoField(primary_key=True)
    product_name = models.TextField(blank=True, null=True)
    venture_id = models.IntegerField(blank=True, null=True)
    coverage_id = models.IntegerField(blank=True, null=True)
    product_code = models.TextField(blank=True, null=True)
    product_prefix = models.TextField(blank=True, null=True)
    documents_name = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'product'

    def __str__(self):
        return self.product_name or f"Product {self.product_id}"

# Special case model
class DjangoprojectItem(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=200)

    class Meta:
        managed = True
        db_table = 'DjangoProject_item'

    def __str__(self):
        return self.name

# Note: Django built-in models (auth_*, django_*, etc.) are managed automatically by Django
# and should not be included in custom models to avoid conflicts.