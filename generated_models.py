# Generated Django Models
# This file was auto-generated from your PostgreSQL database structure

from django.db import models


class DjangoprojectItem(models.Model):
    id = models.BigIntegerField
    name = models.CharField(max_length=200)

    class Meta:
        managed = True
        db_table = 'DjangoProject_item'

    def __str__(self):
        return self.name or f"DjangoprojectItem {self.pk}"

class AttachmentType(models.Model):
    attachment_type_id = models.AutoField(primary_key=True)
    attachment_type_name = models.TextField, blank=True, null=True

    class Meta:
        managed = True
        db_table = 'attachment_type'

    def __str__(self):
        return self.attachment_type_name or f"AttachmentType {self.pk}"

class AuthGroup(models.Model):
    id = models.IntegerField
    name = models.CharField(max_length=150)

    class Meta:
        managed = True
        db_table = 'auth_group'

    def __str__(self):
        return self.name or f"AuthGroup {self.pk}"

class AuthUser(models.Model):
    id = models.IntegerField
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField, blank=True, null=True
    is_superuser = models.BooleanField
    username = models.CharField(max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.BooleanField
    is_active = models.BooleanField
    date_joined = models.DateTimeField

    class Meta:
        managed = True
        db_table = 'auth_user'

    def __str__(self):
        return self.username or f"AuthUser {self.pk}"

class Broker(models.Model):
    broker_id = models.AutoField(primary_key=True)
    broker_name = models.TextField, blank=True, null=True

    class Meta:
        managed = True
        db_table = 'broker'

    def __str__(self):
        return self.broker_name or f"Broker {self.pk}"

class Cloud(models.Model):
    cloud_id = models.AutoField(primary_key=True)
    cloud_name = models.TextField, blank=True, null=True

    class Meta:
        managed = True
        db_table = 'cloud'

    def __str__(self):
        return self.cloud_name or f"Cloud {self.pk}"

class Company(models.Model):
    company_id = models.AutoField(primary_key=True)
    company_name = models.TextField, blank=True, null=True

    class Meta:
        managed = True
        db_table = 'company'

    def __str__(self):
        return self.company_name or f"Company {self.pk}"

class Coverage(models.Model):
    coverage_id = models.AutoField(primary_key=True)
    coverage_name = models.TextField, blank=True, null=True

    class Meta:
        managed = True
        db_table = 'coverage'

    def __str__(self):
        return self.coverage_name or f"Coverage {self.pk}"

class DjangoContentType(models.Model):
    id = models.IntegerField
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = True
        db_table = 'django_content_type'

    def __str__(self):
        return f"DjangoContentType {self.pk}"

class DjangoMigrations(models.Model):
    id = models.BigIntegerField
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField

    class Meta:
        managed = True
        db_table = 'django_migrations'

    def __str__(self):
        return self.name or f"DjangoMigrations {self.pk}"

class DjangoSession(models.Model):
    session_key = models.CharField(max_length=40)
    session_data = models.TextField
    expire_date = models.DateTimeField

    class Meta:
        managed = True
        db_table = 'django_session'

    def __str__(self):
        return f"DjangoSession {self.pk}"

class EmailLog(models.Model):
    email_log_id = models.AutoField(primary_key=True)
    order_id = models.IntegerField, blank=True, null=True
    sent_time = models.CharField(max_length=255)  # Unknown type: time with time zone, blank=True, null=True
    subject = models.TextField, blank=True, null=True

    class Meta:
        managed = True
        db_table = 'email_log'

    def __str__(self):
        return f"EmailLog {self.pk}"

class EmployeeFunction(models.Model):
    employee_function_id = models.AutoField(primary_key=True)
    employee_function = models.TextField, blank=True, null=True

    class Meta:
        managed = True
        db_table = 'employee_function'

    def __str__(self):
        return f"EmployeeFunction {self.pk}"

class FlowOrigin(models.Model):
    flow_origin_id = models.AutoField(primary_key=True)
    flow_origin_name = models.TextField, blank=True, null=True

    class Meta:
        managed = True
        db_table = 'flow_origin'

    def __str__(self):
        return self.flow_origin_name or f"FlowOrigin {self.pk}"

class GenerationLog(models.Model):
    output_id = models.AutoField(primary_key=True)
    model_code = models.TextField, blank=True, null=True
    output_file_name = models.TextField, blank=True, null=True
    product = models.TextField, blank=True, null=True
    output_id_2 = models.TextField, blank=True, null=True

    class Meta:
        managed = True
        db_table = 'generation_log'

    def __str__(self):
        return self.output_file_name or f"GenerationLog {self.pk}"

class GenerationModel(models.Model):
    generation_model_id = models.AutoField(primary_key=True)
    generation_model_name = models.TextField, blank=True, null=True
    python_exe_file = models.TextField, blank=True, null=True
    python_file_path = models.TextField, blank=True, null=True
    jupyter_file_path = models.TextField, blank=True, null=True
    model_filename = models.TextField, blank=True, null=True
    model_code = models.TextField, blank=True, null=True
    py_file = models.TextField, blank=True, null=True

    class Meta:
        managed = True
        db_table = 'generation_model'

    def __str__(self):
        return self.generation_model_name or f"GenerationModel {self.pk}"

class InputOutput(models.Model):
    input_output_id = models.AutoField(primary_key=True)
    input_output_name = models.TextField, blank=True, null=True

    class Meta:
        managed = True
        db_table = 'input_output'

    def __str__(self):
        return self.input_output_name or f"InputOutput {self.pk}"

class Options(models.Model):
    options_id = models.AutoField(primary_key=True)
    option_name = models.TextField, blank=True, null=True

    class Meta:
        managed = True
        db_table = 'options'

    def __str__(self):
        return self.option_name or f"Options {self.pk}"

class Paper(models.Model):
    paper_id = models.AutoField(primary_key=True)
    paper_name = models.TextField, blank=True, null=True
    am_best_rating = models.TextField, blank=True, null=True
    am_best_financial_size = models.TextField, blank=True, null=True

    class Meta:
        managed = True
        db_table = 'paper'

    def __str__(self):
        return self.paper_name or f"Paper {self.pk}"

class ParameterDoc(models.Model):
    parameter_doc_id = models.AutoField(primary_key=True)
    parameter_doc_name = models.TextField, blank=True, null=True

    class Meta:
        managed = True
        db_table = 'parameter_doc'

    def __str__(self):
        return self.parameter_doc_name or f"ParameterDoc {self.pk}"

class ParameterType(models.Model):
    parameter_type_id = models.AutoField(primary_key=True)
    parameter_type_name = models.TextField, blank=True, null=True

    class Meta:
        managed = True
        db_table = 'parameter_type'

    def __str__(self):
        return self.parameter_type_name or f"ParameterType {self.pk}"

class Product(models.Model):
    product_id = models.AutoField(primary_key=True)
    product_name = models.TextField, blank=True, null=True
    venture_id = models.IntegerField, blank=True, null=True
    coverage_id = models.IntegerField, blank=True, null=True
    product_code = models.TextField, blank=True, null=True
    product_prefix = models.TextField, blank=True, null=True
    documents_name = models.TextField, blank=True, null=True

    class Meta:
        managed = True
        db_table = 'product'

    def __str__(self):
        return self.product_name or f"Product {self.pk}"

class Stage(models.Model):
    stage_id = models.AutoField(primary_key=True)
    stage_name = models.TextField, blank=True, null=True

    class Meta:
        managed = True
        db_table = 'stage'

    def __str__(self):
        return self.stage_name or f"Stage {self.pk}"

class Task(models.Model):
    task_id = models.AutoField(primary_key=True)
    task_name = models.TextField, blank=True, null=True
    task_description = models.TextField, blank=True, null=True
    task_display = models.TextField, blank=True, null=True
    subroutine_name = models.TextField, blank=True, null=True

    class Meta:
        managed = True
        db_table = 'task'

    def __str__(self):
        return self.task_name or f"Task {self.pk}"

class TrainingModel(models.Model):
    training_model_id = models.AutoField(primary_key=True)
    model_name = models.TextField, blank=True, null=True
    python_exe_file = models.TextField, blank=True, null=True
    python_file_path = models.TextField, blank=True, null=True
    jupyter_file_path = models.TextField, blank=True, null=True
    model_filename = models.TextField, blank=True, null=True
    model_code = models.TextField, blank=True, null=True
    py_file = models.TextField, blank=True, null=True
    pickle_dump = models.TextField, blank=True, null=True
    inference_py_file = models.TextField, blank=True, null=True

    class Meta:
        managed = True
        db_table = 'training_model'

    def __str__(self):
        return self.model_name or f"TrainingModel {self.pk}"

class UlProgram(models.Model):
    ul_program_id = models.AutoField(primary_key=True)
    order_id = models.IntegerField, blank=True, null=True
    paper_id = models.IntegerField, blank=True, null=True
    limit_id = models.IntegerField, blank=True, null=True

    class Meta:
        managed = True
        db_table = 'ul_program'

    def __str__(self):
        return f"UlProgram {self.pk}"

class Workflow(models.Model):
    workflow_id = models.AutoField(primary_key=True)
    workflow_name = models.TextField, blank=True, null=True
    workflow_type = models.TextField, blank=True, null=True

    class Meta:
        managed = True
        db_table = 'workflow'

    def __str__(self):
        return self.workflow_name or f"Workflow {self.pk}"

class WorkflowType(models.Model):
    workflow_type_id = models.AutoField(primary_key=True)
    workflow_type_name = models.TextField, blank=True, null=True

    class Meta:
        managed = True
        db_table = 'workflow_type'

    def __str__(self):
        return self.workflow_type_name or f"WorkflowType {self.pk}"

class AuthPermission(models.Model):
    id = models.IntegerField
    name = models.CharField(max_length=255)
    content_type_id = models.ForeignKey(DjangoContentType, models.DO_NOTHING, db_column='content_type_id')
    codename = models.CharField(max_length=100)

    class Meta:
        managed = True
        db_table = 'auth_permission'

    def __str__(self):
        return self.name or f"AuthPermission {self.pk}"

class BrokerContact(models.Model):
    broker_contact_id = models.AutoField(primary_key=True)
    broker_location_id = models.ForeignKey(BrokerLocation, models.DO_NOTHING, db_column='broker_location_id', blank=True, null=True)
    broker_first_name = models.TextField, blank=True, null=True
    broker_last_name = models.TextField, blank=True, null=True
    broker_email = models.TextField, blank=True, null=True
    broker_name_combined = models.TextField, blank=True, null=True

    class Meta:
        managed = True
        db_table = 'broker_contact'

    def __str__(self):
        return self.broker_first_name or f"BrokerContact {self.pk}"

class BrokerLocation(models.Model):
    broker_location_id = models.AutoField(primary_key=True)
    broker_id = models.ForeignKey(Broker, models.DO_NOTHING, db_column='broker_id', blank=True, null=True)
    broker_address_1 = models.TextField, blank=True, null=True
    broker_address_2 = models.TextField, blank=True, null=True
    broker_city = models.TextField, blank=True, null=True
    broker_state_id = models.IntegerField, blank=True, null=True
    broker_zip = models.TextField, blank=True, null=True

    class Meta:
        managed = True
        db_table = 'broker_location'

    def __str__(self):
        return f"BrokerLocation {self.pk}"

class EmployeeContact(models.Model):
    employee_id = models.AutoField(primary_key=True)
    employee_location_id = models.ForeignKey(EmployeeLocation, models.DO_NOTHING, db_column='employee_location_id', blank=True, null=True)
    employee_name_first = models.TextField, blank=True, null=True
    employee_name_last = models.TextField, blank=True, null=True
    employee_email = models.TextField, blank=True, null=True
    employee_name_combined = models.TextField, blank=True, null=True

    class Meta:
        managed = True
        db_table = 'employee_contact'

    def __str__(self):
        return self.employee_name_first or f"EmployeeContact {self.pk}"

class AuthGroupPermissions(models.Model):
    id = models.BigIntegerField
    group_id = models.ForeignKey(AuthGroup, models.DO_NOTHING, db_column='group_id')
    permission_id = models.ForeignKey(AuthPermission, models.DO_NOTHING, db_column='permission_id')

    class Meta:
        managed = True
        db_table = 'auth_group_permissions'

    def __str__(self):
        return f"AuthGroupPermissions {self.pk}"

class AuthUserGroups(models.Model):
    id = models.BigIntegerField
    user_id = models.ForeignKey(AuthUser, models.DO_NOTHING, db_column='user_id')
    group_id = models.ForeignKey(AuthGroup, models.DO_NOTHING, db_column='group_id')

    class Meta:
        managed = True
        db_table = 'auth_user_groups'

    def __str__(self):
        return f"AuthUserGroups {self.pk}"

class AuthUserUserPermissions(models.Model):
    id = models.BigIntegerField
    user_id = models.ForeignKey(AuthUser, models.DO_NOTHING, db_column='user_id')
    permission_id = models.ForeignKey(AuthPermission, models.DO_NOTHING, db_column='permission_id')

    class Meta:
        managed = True
        db_table = 'auth_user_user_permissions'

    def __str__(self):
        return f"AuthUserUserPermissions {self.pk}"

class DjangoAdminLog(models.Model):
    id = models.IntegerField
    action_time = models.DateTimeField
    object_id = models.TextField, blank=True, null=True
    object_repr = models.CharField(max_length=200)
    action_flag = models.SmallIntegerField
    change_message = models.TextField
    content_type_id = models.ForeignKey(DjangoContentType, models.DO_NOTHING, db_column='content_type_id', blank=True, null=True)
    user_id = models.ForeignKey(AuthUser, models.DO_NOTHING, db_column='user_id')

    class Meta:
        managed = True
        db_table = 'django_admin_log'

    def __str__(self):
        return f"DjangoAdminLog {self.pk}"

class DocumentDetail(models.Model):
    document_detail_id = models.AutoField(primary_key=True)
    order_option_id = models.ForeignKey(OrderOption, models.DO_NOTHING, db_column='order_option_id', blank=True, null=True)
    document_id = models.ForeignKey(Document, models.DO_NOTHING, db_column='document_id', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'document_detail'

    def __str__(self):
        return f"DocumentDetail {self.pk}"

class ApplicationResponse(models.Model):
    application_response_id = models.AutoField(primary_key=True)
    application_id = models.ForeignKey(Applications, models.DO_NOTHING, db_column='application_id', blank=True, null=True)
    application_question_id = models.ForeignKey(ApplicationQuestion, models.DO_NOTHING, db_column='application_question_id', blank=True, null=True)
    order_id = models.ForeignKey(Orders, models.DO_NOTHING, db_column='order_id', blank=True, null=True)
    response = models.TextField, blank=True, null=True

    class Meta:
        managed = True
        db_table = 'application_response'

    def __str__(self):
        return f"ApplicationResponse {self.pk}"

class Attachment(models.Model):
    attachment_id = models.AutoField(primary_key=True)
    attachment_name = models.TextField, blank=True, null=True
    output_description = models.TextField, blank=True, null=True
    attachment_type_id = models.ForeignKey(AttachmentType, models.DO_NOTHING, db_column='attachment_type_id', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'attachment'

    def __str__(self):
        return self.attachment_name or f"Attachment {self.pk}"

class WorkflowStandard(models.Model):
    workflow_standard_id = models.AutoField(primary_key=True)
    workflow_type = models.TextField, blank=True, null=True
    stage_id = models.IntegerField, blank=True, null=True
    next_stage_id = models.IntegerField, blank=True, null=True
    task_id = models.ForeignKey(Task, models.DO_NOTHING, db_column='task_id', blank=True, null=True)
    workflow_sequence = models.TextField, blank=True, null=True
    man_auto = models.IntegerField, blank=True, null=True

    class Meta:
        managed = True
        db_table = 'workflow_standard'

    def __str__(self):
        return f"WorkflowStandard {self.pk}"

class AttachmentLog(models.Model):
    attachment_log_id = models.AutoField(primary_key=True)
    order_id = models.ForeignKey(Orders, models.DO_NOTHING, db_column='order_id', blank=True, null=True)
    attachment_type_id = models.ForeignKey(AttachmentType, models.DO_NOTHING, db_column='attachment_type_id', blank=True, null=True)
    document_name = models.TextField, blank=True, null=True
    document_timestamp = models.CharField(max_length=255)  # Unknown type: time with time zone, blank=True, null=True
    document_path = models.TextField, blank=True, null=True

    class Meta:
        managed = True
        db_table = 'attachment_log'

    def __str__(self):
        return self.document_name or f"AttachmentLog {self.pk}"

class WorkflowDetail(models.Model):
    workflow_detail_id = models.AutoField(primary_key=True)
    workflow_id = models.ForeignKey(Workflow, models.DO_NOTHING, db_column='workflow_id', blank=True, null=True)
    stage_id = models.IntegerField, blank=True, null=True
    task_id = models.ForeignKey(Task, models.DO_NOTHING, db_column='task_id', blank=True, null=True)
    workflow_sequence = models.IntegerField, blank=True, null=True
    man_auto = models.BooleanField, blank=True, null=True

    class Meta:
        managed = True
        db_table = 'workflow_detail'

    def __str__(self):
        return f"WorkflowDetail {self.pk}"

class CompanyAlias(models.Model):
    company_alias_id = models.AutoField(primary_key=True)
    company_id = models.ForeignKey(Company, models.DO_NOTHING, db_column='company_id', blank=True, null=True)
    company_alias_name = models.TextField, blank=True, null=True
    company_alias_retro_start = models.DateField, blank=True, null=True
    company_alias_retro_end = models.DateField, blank=True, null=True
    company_alias_eff_dte = models.DateField, blank=True, null=True
    company_alias_exp_dte = models.DateField, blank=True, null=True

    class Meta:
        managed = True
        db_table = 'company_alias'

    def __str__(self):
        return self.company_alias_name or f"CompanyAlias {self.pk}"

class CompanyContact(models.Model):
    company_contact_id = models.AutoField(primary_key=True)
    company_id = models.ForeignKey(Company, models.DO_NOTHING, db_column='company_id', blank=True, null=True)
    company_contact_first = models.TextField, blank=True, null=True
    company_contact_last = models.TextField, blank=True, null=True
    company_contact_phone = models.TextField, blank=True, null=True
    company_contact_email = models.TextField, blank=True, null=True
    company_contact_title = models.TextField, blank=True, null=True
    company_contact_salutation = models.TextField, blank=True, null=True
    company_web = models.TextField, blank=True, null=True

    class Meta:
        managed = True
        db_table = 'company_contact'

    def __str__(self):
        return self.company_contact_title or f"CompanyContact {self.pk}"

class CompanyLocation(models.Model):
    company_location_id = models.AutoField(primary_key=True)
    company_id = models.ForeignKey(Company, models.DO_NOTHING, db_column='company_id', blank=True, null=True)
    company_location_address_1 = models.TextField, blank=True, null=True
    company_location_address_2 = models.TextField, blank=True, null=True
    company_location_city = models.TextField, blank=True, null=True
    company_location_state = models.TextField, blank=True, null=True
    company_location_zip = models.TextField, blank=True, null=True
    company_mailing = models.BooleanField, blank=True, null=True

    class Meta:
        managed = True
        db_table = 'company_location'

    def __str__(self):
        return f"CompanyLocation {self.pk}"

class Products(models.Model):
    products_id = models.AutoField(primary_key=True)
    product_name = models.TextField, blank=True, null=True
    venture_id = models.ForeignKey(Venture, models.DO_NOTHING, db_column='venture_id', blank=True, null=True)
    coverage_id = models.ForeignKey(Coverage, models.DO_NOTHING, db_column='coverage_id', blank=True, null=True)
    product_code = models.TextField, blank=True, null=True
    product_prefix = models.TextField, blank=True, null=True
    documents_name = models.TextField, blank=True, null=True

    class Meta:
        managed = True
        db_table = 'products'

    def __str__(self):
        return self.product_name or f"Products {self.pk}"

class OrderData(models.Model):
    order_data_id = models.AutoField(primary_key=True)
    orders_id = models.ForeignKey(Orders, models.DO_NOTHING, db_column='orders_id', blank=True, null=True)
    employee_count = models.TextField, blank=True, null=True

    class Meta:
        managed = True
        db_table = 'order_data'

    def __str__(self):
        return f"OrderData {self.pk}"

class PaperDetail(models.Model):
    paper_detail_id = models.AutoField(primary_key=True)
    products_id = models.ForeignKey(Products, models.DO_NOTHING, db_column='products_id', blank=True, null=True)
    paper_id = models.ForeignKey(Paper, models.DO_NOTHING, db_column='paper_id', blank=True, null=True)
    paper_percentage = models.DecimalField(max_digits=10, decimal_places=2), blank=True, null=True

    class Meta:
        managed = True
        db_table = 'paper_detail'

    def __str__(self):
        return f"PaperDetail {self.pk}"

class SublimitDetail(models.Model):
    sublimit_detail_id = models.AutoField(primary_key=True)
    orders_id = models.ForeignKey(Orders, models.DO_NOTHING, db_column='orders_id', blank=True, null=True)
    sublimit_id = models.ForeignKey(Sublimit, models.DO_NOTHING, db_column='sublimit_id', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'sublimit_detail'

    def __str__(self):
        return f"SublimitDetail {self.pk}"

class TrainingJob(models.Model):
    training_job_id = models.AutoField(primary_key=True)
    training_model_id = models.ForeignKey(TrainingModel, models.DO_NOTHING, db_column='training_model_id', blank=True, null=True)
    products_id = models.ForeignKey(Products, models.DO_NOTHING, db_column='products_id', blank=True, null=True)
    data_set_id = models.TextField, blank=True, null=True
    pickle_file_name = models.TextField, blank=True, null=True

    class Meta:
        managed = True
        db_table = 'training_job'

    def __str__(self):
        return self.pickle_file_name or f"TrainingJob {self.pk}"

class ModelParameter(models.Model):
    model_parameter_id = models.AutoField(primary_key=True)
    training_job_id = models.ForeignKey(TrainingJob, models.DO_NOTHING, db_column='training_job_id', blank=True, null=True)
    parameter_id = models.ForeignKey(Parameter, models.DO_NOTHING, db_column='parameter_id', blank=True, null=True)
    input_output_id = models.ForeignKey(InputOutput, models.DO_NOTHING, db_column='input_output_id', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'model_parameter'

    def __str__(self):
        return f"ModelParameter {self.pk}"

class ApplicationQuestion(models.Model):
    application_question_id = models.AutoField(primary_key=True)
    application_id = models.ForeignKey(Applications, models.DO_NOTHING, db_column='application_id', blank=True, null=True)
    custom_question = models.TextField, blank=True, null=True
    parameter_id = models.ForeignKey(Parameter, models.DO_NOTHING, db_column='parameter_id', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'application_question'

    def __str__(self):
        return f"ApplicationQuestion {self.pk}"

class ParametersStandard(models.Model):
    parameters_standard_id = models.AutoField(primary_key=True)
    coverage_id = models.ForeignKey(Coverage, models.DO_NOTHING, db_column='coverage_id', blank=True, null=True)
    parameter_id = models.ForeignKey(Parameter, models.DO_NOTHING, db_column='parameter_id', blank=True, null=True)
    parameter_map_seq = models.IntegerField, blank=True, null=True

    class Meta:
        managed = True
        db_table = 'parameters_standard'

    def __str__(self):
        return f"ParametersStandard {self.pk}"

class OrderOption(models.Model):
    order_option_id = models.AutoField(primary_key=True)
    orders_id = models.ForeignKey(Orders, models.DO_NOTHING, db_column='orders_id', blank=True, null=True)
    options_id = models.ForeignKey(Options, models.DO_NOTHING, db_column='options_id', blank=True, null=True)
    cover_id = models.ForeignKey(Cover, models.DO_NOTHING, db_column='cover_id', blank=True, null=True)
    order_option_include = models.BooleanField, blank=True, null=True
    retention_id = models.ForeignKey(Retention, models.DO_NOTHING, db_column='retention_id', blank=True, null=True)
    limits_id = models.ForeignKey(Limits, models.DO_NOTHING, db_column='limits_id', blank=True, null=True)
    premium = models.DecimalField(max_digits=10, decimal_places=2), blank=True, null=True
    bound = models.BooleanField, blank=True, null=True

    class Meta:
        managed = True
        db_table = 'order_option'

    def __str__(self):
        return f"OrderOption {self.pk}"

class ParameterMap(models.Model):
    parameter_map_id = models.AutoField(primary_key=True)
    products_id = models.ForeignKey(Products, models.DO_NOTHING, db_column='products_id', blank=True, null=True)
    parameter_id = models.ForeignKey(Parameter, models.DO_NOTHING, db_column='parameter_id', blank=True, null=True)
    console_element = models.BooleanField, blank=True, null=True
    quote_item = models.BooleanField, blank=True, null=True
    binder_item = models.BooleanField, blank=True, null=True
    policy_item = models.BooleanField, blank=True, null=True

    class Meta:
        managed = True
        db_table = 'parameter_map'

    def __str__(self):
        return f"ParameterMap {self.pk}"

class Sublimit(models.Model):
    sublimit_id = models.AutoField(primary_key=True)
    orders_id = models.ForeignKey(Orders, models.DO_NOTHING, db_column='orders_id', blank=True, null=True)
    products_id = models.ForeignKey(Products, models.DO_NOTHING, db_column='products_id', blank=True, null=True)
    sublimit_name = models.TextField, blank=True, null=True
    sublimit_amount = models.DecimalField(max_digits=10, decimal_places=2), blank=True, null=True

    class Meta:
        managed = True
        db_table = 'sublimit'

    def __str__(self):
        return self.sublimit_name or f"Sublimit {self.pk}"

class OrderDataVert(models.Model):
    order_date_vert_id = models.AutoField(primary_key=True)
    order_id = models.ForeignKey(Orders, models.DO_NOTHING, db_column='order_id', blank=True, null=True)
    parameter_id = models.ForeignKey(Parameter, models.DO_NOTHING, db_column='parameter_id', blank=True, null=True)
    vert_value = models.TextField, blank=True, null=True
    parameter_map_id = models.ForeignKey(ParameterMap, models.DO_NOTHING, db_column='parameter_map_id', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'order_data_vert'

    def __str__(self):
        return f"OrderDataVert {self.pk}"

class Orders(models.Model):
    orders_id = models.AutoField(primary_key=True)
    stage_id = models.ForeignKey(Stage, models.DO_NOTHING, db_column='stage_id', blank=True, null=True)
    employee_id = models.ForeignKey(EmployeeContact, models.DO_NOTHING, db_column='employee_id', blank=True, null=True)
    flow_origin_id = models.ForeignKey(FlowOrigin, models.DO_NOTHING, db_column='flow_origin_id', blank=True, null=True)
    company_id = models.ForeignKey(Company, models.DO_NOTHING, db_column='company_id', blank=True, null=True)
    products_id = models.ForeignKey(Products, models.DO_NOTHING, db_column='products_id', blank=True, null=True)
    venture_id = models.ForeignKey(Venture, models.DO_NOTHING, db_column='venture_id', blank=True, null=True)
    order_created = models.CharField(max_length=255)  # Unknown type: time with time zone, blank=True, null=True
    workflow_id = models.ForeignKey(Workflow, models.DO_NOTHING, db_column='workflow_id', blank=True, null=True)
    workflow_detail_id = models.ForeignKey(WorkflowDetail, models.DO_NOTHING, db_column='workflow_detail_id', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'orders'

    def __str__(self):
        return f"Orders {self.pk}"

class Cover(models.Model):
    cover_id = models.AutoField(primary_key=True)
    cover_name = models.TextField, blank=True, null=True
    product_id = models.ForeignKey(Products, models.DO_NOTHING, db_column='product_id', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'cover'

    def __str__(self):
        return self.cover_name or f"Cover {self.pk}"

class DataSeed(models.Model):
    data_seed_id = models.AutoField(primary_key=True)
    data_seed_filename = models.TextField, blank=True, null=True
    show_seed = models.BooleanField, blank=True, null=True
    product_id = models.ForeignKey(Products, models.DO_NOTHING, db_column='product_id', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'data_seed'

    def __str__(self):
        return self.data_seed_filename or f"DataSeed {self.pk}"

class Document(models.Model):
    document_id = models.AutoField(primary_key=True)
    document_name = models.TextField, blank=True, null=True
    product_id = models.ForeignKey(Products, models.DO_NOTHING, db_column='product_id', blank=True, null=True)
    document_number = models.TextField, blank=True, null=True
    default_document = models.BooleanField, blank=True, null=True
    document_added = models.CharField(max_length=255)  # Unknown type: time with time zone, blank=True, null=True
    document_expiration = models.CharField(max_length=255)  # Unknown type: time with time zone, blank=True, null=True
    document_prior_version = models.IntegerField, blank=True, null=True
    document_code = models.TextField, blank=True, null=True

    class Meta:
        managed = True
        db_table = 'document'

    def __str__(self):
        return self.document_name or f"Document {self.pk}"

class Retention(models.Model):
    retention_id = models.AutoField(primary_key=True)
    products_id = models.ForeignKey(Products, models.DO_NOTHING, db_column='products_id', blank=True, null=True)
    cover_id = models.IntegerField, blank=True, null=True
    retention_text = models.TextField, blank=True, null=True
    retention_pc_number = models.DecimalField(max_digits=10, decimal_places=2), blank=True, null=True
    retention_ag_number = models.DecimalField(max_digits=10, decimal_places=2), blank=True, null=True

    class Meta:
        managed = True
        db_table = 'retention'

    def __str__(self):
        return f"Retention {self.pk}"

class Applications(models.Model):
    application_id = models.AutoField(primary_key=True)
    application_name = models.TextField, blank=True, null=True
    product_id = models.ForeignKey(Product, models.DO_NOTHING, db_column='product_id', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'applications'

    def __str__(self):
        return self.application_name or f"Applications {self.pk}"

class Limits(models.Model):
    limits_id = models.AutoField(primary_key=True)
    product_id = models.ForeignKey(Products, models.DO_NOTHING, db_column='product_id', blank=True, null=True)
    cover_id = models.ForeignKey(Cover, models.DO_NOTHING, db_column='cover_id', blank=True, null=True)
    limit_text = models.TextField, blank=True, null=True
    limit_pc_number = models.DecimalField(max_digits=10, decimal_places=2), blank=True, null=True
    limit_ag_number = models.DecimalField(max_digits=10, decimal_places=2), blank=True, null=True

    class Meta:
        managed = True
        db_table = 'limits'

    def __str__(self):
        return f"Limits {self.pk}"

class EmployeeFunctionDetail(models.Model):
    employee_function_detail_id = models.AutoField(primary_key=True)
    employee_id = models.ForeignKey(EmployeeContact, models.DO_NOTHING, db_column='employee_id', blank=True, null=True)
    employee_function_id = models.ForeignKey(EmployeeFunction, models.DO_NOTHING, db_column='employee_function_id', blank=True, null=True)
    product_id = models.ForeignKey(Products, models.DO_NOTHING, db_column='product_id', blank=True, null=True)
    cloud_name = models.TextField, blank=True, null=True
    iam = models.TextField, blank=True, null=True

    class Meta:
        managed = True
        db_table = 'employee_function_detail'

    def __str__(self):
        return self.cloud_name or f"EmployeeFunctionDetail {self.pk}"

class AttachmentDetail(models.Model):
    attachment_detail_id = models.AutoField(primary_key=True)
    attachment_id = models.ForeignKey(Attachment, models.DO_NOTHING, db_column='attachment_id', blank=True, null=True)
    product_id = models.ForeignKey(Products, models.DO_NOTHING, db_column='product_id', blank=True, null=True)
    task_id = models.ForeignKey(Task, models.DO_NOTHING, db_column='task_id', blank=True, null=True)
    attachment_type_id = models.ForeignKey(AttachmentType, models.DO_NOTHING, db_column='attachment_type_id', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'attachment_detail'

    def __str__(self):
        return f"AttachmentDetail {self.pk}"
