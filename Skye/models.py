# Skye/models.py

from django.db import models
from django.contrib.auth.models import User


class Venture(models.Model):
    venture_id = models.AutoField(primary_key=True)
    venture_name = models.TextField(blank=True, null=True)
    venture_address_1 = models.TextField(blank=True, null=True)
    venture_address_2 = models.TextField(blank=True, null=True)
    venture_city = models.TextField(blank=True, null=True)
    venture_state = models.TextField(blank=True, null=True)
    venture_zip = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'venture'

    def __str__(self):
        return self.venture_name or f"Venture {self.venture_id}"


class Coverage(models.Model):
    coverage_id = models.AutoField(primary_key=True)
    coverage_name = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'coverage'

    def __str__(self):
        return self.coverage_name or f"Coverage {self.coverage_id}"


class Products(models.Model):
    products_id = models.AutoField(primary_key=True)
    product_name = models.TextField(blank=True, null=True)
    venture = models.ForeignKey(Venture, on_delete=models.CASCADE, null=True, blank=True)
    coverage = models.ForeignKey(Coverage, on_delete=models.CASCADE, null=True, blank=True)
    product_code = models.TextField(blank=True, null=True)
    product_prefix = models.TextField(blank=True, null=True)
    documents_name = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'products'

    def __str__(self):
        return self.product_name or f"Product {self.products_id}"


class Company(models.Model):
    company_id = models.AutoField(primary_key=True)
    company_name = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'company'

    def __str__(self):
        return self.company_name or f"Company {self.company_id}"


class CompanyContact(models.Model):
    company_contact_id = models.AutoField(primary_key=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True, blank=True)
    company_contact_first = models.TextField(blank=True, null=True)
    company_contact_last = models.TextField(blank=True, null=True)
    company_contact_phone = models.TextField(blank=True, null=True)
    company_contact_email = models.TextField(blank=True, null=True)
    company_contact_title = models.TextField(blank=True, null=True)
    company_contact_salutation = models.TextField(blank=True, null=True)
    company_web = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'company_contact'

    def __str__(self):
        return f"{self.company_contact_first} {self.company_contact_last}"


class CompanyLocation(models.Model):
    company_location_id = models.AutoField(primary_key=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True, blank=True)
    company_location_address_1 = models.TextField(blank=True, null=True)
    company_location_address_2 = models.TextField(blank=True, null=True)
    company_location_city = models.TextField(blank=True, null=True)
    company_location_state = models.TextField(blank=True, null=True)
    company_location_zip = models.TextField(blank=True, null=True)
    company_mailing = models.BooleanField(default=False)

    class Meta:
        db_table = 'company_location'

    def __str__(self):
        return f"{self.company.company_name} - {self.company_location_city}"


class EmployeeLocation(models.Model):
    employee_location_id = models.AutoField(primary_key=True)
    venture = models.ForeignKey(Venture, on_delete=models.CASCADE, null=True, blank=True)
    employee_location_name = models.TextField(blank=True, null=True)
    employee_location_address_1 = models.TextField(blank=True, null=True)
    employee_location_address_2 = models.TextField(blank=True, null=True)
    employee_location_city = models.TextField(blank=True, null=True)
    employee_location_state = models.TextField(blank=True, null=True)
    employee_location_zip = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'employee_location'

    def __str__(self):
        return self.employee_location_name or f"Location {self.employee_location_id}"


class EmployeeContact(models.Model):
    employee_id = models.AutoField(primary_key=True)
    employee_location = models.ForeignKey(EmployeeLocation, on_delete=models.CASCADE, null=True, blank=True)
    employee_name_first = models.TextField(blank=True, null=True)
    employee_name_last = models.TextField(blank=True, null=True)
    employee_email = models.TextField(blank=True, null=True)
    employee_name_combined = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'employee_contact'

    def __str__(self):
        return f"{self.employee_name_first} {self.employee_name_last}"


class Stage(models.Model):
    stage_id = models.AutoField(primary_key=True)
    stage_name = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'stage'

    def __str__(self):
        return self.stage_name or f"Stage {self.stage_id}"


class FlowOrigin(models.Model):
    flow_origin_id = models.AutoField(primary_key=True)
    flow_origin_name = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'flow_origin'

    def __str__(self):
        return self.flow_origin_name or f"Flow Origin {self.flow_origin_id}"


class Workflow(models.Model):
    workflow_id = models.AutoField(primary_key=True)
    workflow_name = models.TextField(blank=True, null=True)
    workflow_type = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'workflow'

    def __str__(self):
        return self.workflow_name or f"Workflow {self.workflow_id}"


class Task(models.Model):
    task_id = models.AutoField(primary_key=True)
    task_name = models.TextField(blank=True, null=True)
    task_description = models.TextField(blank=True, null=True)
    task_display = models.TextField(blank=True, null=True)
    subroutine_name = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'task'

    def __str__(self):
        return self.task_name or f"Task {self.task_id}"


class WorkflowDetail(models.Model):
    workflow_detail_id = models.AutoField(primary_key=True)
    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE, null=True, blank=True)
    stage = models.ForeignKey(Stage, on_delete=models.CASCADE, null=True, blank=True)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, blank=True)
    workflow_sequence = models.IntegerField(null=True, blank=True)
    man_auto = models.BooleanField(default=False)

    class Meta:
        db_table = 'workflow_detail'

    def __str__(self):
        return f"Workflow Detail {self.workflow_detail_id}"


class Orders(models.Model):
    orders_id = models.AutoField(primary_key=True)
    stage = models.ForeignKey(Stage, on_delete=models.CASCADE, null=True, blank=True)
    employee = models.ForeignKey(EmployeeContact, on_delete=models.CASCADE, null=True, blank=True)
    flow_origin = models.ForeignKey(FlowOrigin, on_delete=models.CASCADE, null=True, blank=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True, blank=True)
    products = models.ForeignKey(Products, on_delete=models.CASCADE, null=True, blank=True)
    venture = models.ForeignKey(Venture, on_delete=models.CASCADE, null=True, blank=True)
    order_created = models.TimeField(null=True, blank=True)
    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE, null=True, blank=True)
    workflow_detail = models.ForeignKey(WorkflowDetail, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        db_table = 'orders'

    def __str__(self):
        return f"Order {self.orders_id}"


class Applications(models.Model):
    application_id = models.AutoField(primary_key=True)
    application_name = models.TextField(blank=True, null=True)
    product = models.ForeignKey(Products, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        db_table = 'applications'

    def __str__(self):
        return self.application_name or f"Application {self.application_id}"


class ParameterType(models.Model):
    parameter_type_id = models.AutoField(primary_key=True)
    parameter_type_name = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'parameter_type'

    def __str__(self):
        return self.parameter_type_name or f"Parameter Type {self.parameter_type_id}"


class Parameter(models.Model):
    parameter_id = models.AutoField(primary_key=True)
    parameter_name = models.TextField(blank=True, null=True)
    parameter_type = models.ForeignKey(ParameterType, on_delete=models.CASCADE, null=True, blank=True)
    parameter_docs = models.TextField(blank=True, null=True)
    parameter_quote = models.BooleanField(default=False)
    parameter_binder = models.BooleanField(default=False)
    parameter_policy = models.BooleanField(default=False)

    class Meta:
        db_table = 'parameter'

    def __str__(self):
        return self.parameter_name or f"Parameter {self.parameter_id}"


class ApplicationQuestion(models.Model):
    application_question_id = models.AutoField(primary_key=True)
    application = models.ForeignKey(Applications, on_delete=models.CASCADE, null=True, blank=True)
    custom_question = models.TextField(blank=True, null=True)
    parameter = models.ForeignKey(Parameter, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        db_table = 'application_question'

    def __str__(self):
        return f"Question {self.application_question_id}"


class ApplicationResponse(models.Model):
    application_response_id = models.AutoField(primary_key=True)
    application = models.ForeignKey(Applications, on_delete=models.CASCADE, null=True, blank=True)
    application_question = models.ForeignKey(ApplicationQuestion, on_delete=models.CASCADE, null=True, blank=True)
    order = models.ForeignKey(Orders, on_delete=models.CASCADE, null=True, blank=True)
    response = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'application_response'

    def __str__(self):
        return f"Response {self.application_response_id}"


class Cover(models.Model):
    cover_id = models.AutoField(primary_key=True)
    cover_name = models.TextField(blank=True, null=True)
    product = models.ForeignKey(Products, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        db_table = 'cover'

    def __str__(self):
        return self.cover_name or f"Cover {self.cover_id}"


class Options(models.Model):
    options_id = models.AutoField(primary_key=True)
    option_name = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'options'

    def __str__(self):
        return self.option_name or f"Option {self.options_id}"


class Limits(models.Model):
    limits_id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Products, on_delete=models.CASCADE, null=True, blank=True)
    cover = models.ForeignKey(Cover, on_delete=models.CASCADE, null=True, blank=True)
    limit_text = models.TextField(blank=True, null=True)
    limit_pc_number = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    limit_ag_number = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)

    class Meta:
        db_table = 'limits'

    def __str__(self):
        return f"Limit {self.limits_id}"


class Retention(models.Model):
    retention_id = models.AutoField(primary_key=True)
    products = models.ForeignKey(Products, on_delete=models.CASCADE, null=True, blank=True)
    cover = models.ForeignKey(Cover, on_delete=models.CASCADE, null=True, blank=True)
    retention_text = models.TextField(blank=True, null=True)
    retention_pc_number = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    retention_ag_number = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)

    class Meta:
        db_table = 'retention'

    def __str__(self):
        return f"Retention {self.retention_id}"


class OrderOption(models.Model):
    order_option_id = models.AutoField(primary_key=True)
    orders = models.ForeignKey(Orders, on_delete=models.CASCADE, null=True, blank=True)
    options = models.ForeignKey(Options, on_delete=models.CASCADE, null=True, blank=True)
    cover = models.ForeignKey(Cover, on_delete=models.CASCADE, null=True, blank=True)
    order_option_include = models.BooleanField(default=False)
    retention = models.ForeignKey(Retention, on_delete=models.CASCADE, null=True, blank=True)
    limits = models.ForeignKey(Limits, on_delete=models.CASCADE, null=True, blank=True)
    premium = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    bound = models.BooleanField(default=False)

    class Meta:
        db_table = 'order_option'

    def __str__(self):
        return f"Order Option {self.order_option_id}"


# Additional models for completeness - you can add more based on your needs
class Document(models.Model):
    document_id = models.AutoField(primary_key=True)
    document_name = models.TextField(blank=True, null=True)
    product = models.ForeignKey(Products, on_delete=models.CASCADE, null=True, blank=True)
    document_number = models.TextField(blank=True, null=True)
    default_document = models.BooleanField(default=False)
    document_added = models.TimeField(null=True, blank=True)
    document_expiration = models.TimeField(null=True, blank=True)
    document_prior_version = models.IntegerField(null=True, blank=True)
    document_code = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'document'

    def __str__(self):
        return self.document_name or f"Document {self.document_id}"


class Broker(models.Model):
    broker_id = models.AutoField(primary_key=True)
    broker_name = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'broker'

    def __str__(self):
        return self.broker_name or f"Broker {self.broker_id}"


class BrokerLocation(models.Model):
    broker_location_id = models.AutoField(primary_key=True)
    broker = models.ForeignKey(Broker, on_delete=models.CASCADE, null=True, blank=True)
    broker_address_1 = models.TextField(blank=True, null=True)
    broker_address_2 = models.TextField(blank=True, null=True)
    broker_city = models.TextField(blank=True, null=True)
    broker_state_id = models.IntegerField(null=True, blank=True)
    broker_zip = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'broker_location'

    def __str__(self):
        return f"{self.broker.broker_name} - {self.broker_city}"


class BrokerContact(models.Model):
    broker_contact_id = models.AutoField(primary_key=True)
    broker_location = models.ForeignKey(BrokerLocation, on_delete=models.CASCADE, null=True, blank=True)
    broker_first_name = models.TextField(blank=True, null=True)
    broker_last_name = models.TextField(blank=True, null=True)
    broker_email = models.TextField(blank=True, null=True)
    broker_name_combined = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'broker_contact'

    def __str__(self):
        return f"{self.broker_first_name} {self.broker_last_name}"

class Drive(models.Model):
    drive_id = models.AutoField(primary_key=True)
    drive_name = models.TextField(blank=True, null=True)
    venture = models.ForeignKey(Venture, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        db_table = 'drive'

    def __str__(self):
        return self.drive_name or f"Drive {self.drive_id}"


class EmployeeFunction(models.Model):
    employee_function_id = models.AutoField(primary_key=True)
    employee_function = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'employee_function'

    def __str__(self):
        return self.employee_function or f"Function {self.employee_function_id}"


class EmployeeFunctionDetail(models.Model):
    employee_function_detail_id = models.AutoField(primary_key=True)
    employee = models.ForeignKey(EmployeeContact, on_delete=models.CASCADE, null=True, blank=True)
    employee_function = models.ForeignKey(EmployeeFunction, on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey(Products, on_delete=models.CASCADE, null=True, blank=True)
    cloud_name = models.TextField(blank=True, null=True)
    iam = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'employee_function_detail'

    def __str__(self):
        return f"Function Detail {self.employee_function_detail_id}"


class Paper(models.Model):
    paper_id = models.AutoField(primary_key=True)
    paper_name = models.TextField(blank=True, null=True)
    am_best_rating = models.TextField(blank=True, null=True)
    am_best_financial_size = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'paper'

    def __str__(self):
        return self.paper_name or f"Paper {self.paper_id}"


class PaperDetail(models.Model):
    paper_detail_id = models.AutoField(primary_key=True)
    products = models.ForeignKey(Products, on_delete=models.CASCADE, null=True, blank=True)
    paper = models.ForeignKey(Paper, on_delete=models.CASCADE, null=True, blank=True)
    paper_percentage = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)

    class Meta:
        db_table = 'paper_detail'

    def __str__(self):
        return f"Paper Detail {self.paper_detail_id}"


class ParameterMap(models.Model):
    parameter_map_id = models.AutoField(primary_key=True)
    products = models.ForeignKey(Products, on_delete=models.CASCADE, null=True, blank=True)
    parameter = models.ForeignKey(Parameter, on_delete=models.CASCADE, null=True, blank=True)
    console_element = models.BooleanField(default=False)
    quote_item = models.BooleanField(default=False)
    binder_item = models.BooleanField(default=False)
    policy_item = models.BooleanField(default=False)

    class Meta:
        db_table = 'parameter_map'

    def __str__(self):
        return f"Parameter Map {self.parameter_map_id}"


class AttachmentType(models.Model):
    attachment_type_id = models.AutoField(primary_key=True)
    attachment_type_name = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'attachment_type'

    def __str__(self):
        return self.attachment_type_name or f"Attachment Type {self.attachment_type_id}"


class Attachment(models.Model):
    attachment_id = models.AutoField(primary_key=True)
    attachment_name = models.TextField(blank=True, null=True)
    output_description = models.TextField(blank=True, null=True)
    attachment_type = models.ForeignKey(AttachmentType, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        db_table = 'attachment'

    def __str__(self):
        return self.attachment_name or f"Attachment {self.attachment_id}"


class AttachmentDetail(models.Model):
    attachment_detail_id = models.AutoField(primary_key=True)
    attachment = models.ForeignKey(Attachment, on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey(Products, on_delete=models.CASCADE, null=True, blank=True)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, blank=True)
    attachment_type = models.ForeignKey(AttachmentType, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        db_table = 'attachment_detail'

    def __str__(self):
        return f"Attachment Detail {self.attachment_detail_id}"


class Sublimit(models.Model):
    sublimit_id = models.AutoField(primary_key=True)
    orders = models.ForeignKey(Orders, on_delete=models.CASCADE, null=True, blank=True)
    products = models.ForeignKey(Products, on_delete=models.CASCADE, null=True, blank=True)
    sublimit_name = models.TextField(blank=True, null=True)
    sublimit_amount = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)

    class Meta:
        db_table = 'sublimit'

    def __str__(self):
        return self.sublimit_name or f"Sublimit {self.sublimit_id}"


class WorkflowStandard(models.Model):
    workflow_standard_id = models.AutoField(primary_key=True)
    workflow_type = models.TextField(blank=True, null=True)
    stage = models.ForeignKey(Stage, on_delete=models.CASCADE, null=True, blank=True)
    next_stage_id = models.IntegerField(null=True, blank=True)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, blank=True)
    workflow_sequence = models.TextField(blank=True, null=True)
    man_auto = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'workflow_standard'

    def __str__(self):
        return f"Workflow Standard {self.workflow_standard_id}"

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
        db_table = 'generation_model'

    def __str__(self):
        return self.generation_model_name or f"Generation Model {self.generation_model_id}"


class DataSeed(models.Model):
    data_seed_id = models.AutoField(primary_key=True)
    data_seed_filename = models.TextField(blank=True, null=True)
    show_seed = models.BooleanField(default=False)
    product = models.ForeignKey(Products, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        db_table = 'data_seed'

    def __str__(self):
        return self.data_seed_filename or f"Data Seed {self.data_seed_id}"


class GenerationJob(models.Model):
    generation_job_id = models.AutoField(primary_key=True)
    generator_model = models.ForeignKey(GenerationModel, on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey(Products, on_delete=models.CASCADE, null=True, blank=True)
    data_seed = models.ForeignKey(DataSeed, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        db_table = 'generation_job'

    def __str__(self):
        return f"Generation Job {self.generation_job_id}"


class GenerationLog(models.Model):
    output_id = models.AutoField(primary_key=True)
    model_code = models.TextField(blank=True, null=True)
    output_file_name = models.TextField(blank=True, null=True)
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    output_id_2 = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'generation_log'

    def __str__(self):
        return f"Generation Log {self.output_id}"


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
        db_table = 'training_model'

    def __str__(self):
        return self.model_name or f"Training Model {self.training_model_id}"


class TrainingJob(models.Model):
    training_job_id = models.AutoField(primary_key=True)
    training_model = models.ForeignKey(TrainingModel, on_delete=models.CASCADE, null=True, blank=True)
    products = models.ForeignKey(Products, on_delete=models.CASCADE, null=True, blank=True)
    data_set_id = models.TextField(blank=True, null=True)
    pickle_file_name = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'training_job'

    def __str__(self):
        return f"Training Job {self.training_job_id}"


class InputOutput(models.Model):
    input_output_id = models.AutoField(primary_key=True)
    input_output_name = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'input_output'

    def __str__(self):
        return self.input_output_name or f"Input/Output {self.input_output_id}"


class ModelParameter(models.Model):
    model_parameter_id = models.AutoField(primary_key=True)
    training_job = models.ForeignKey(TrainingJob, on_delete=models.CASCADE, null=True, blank=True)
    parameter = models.ForeignKey(Parameter, on_delete=models.CASCADE, null=True, blank=True)
    input_output = models.ForeignKey(InputOutput, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        db_table = 'model_parameter'

    def __str__(self):
        return f"Model Parameter {self.model_parameter_id}"