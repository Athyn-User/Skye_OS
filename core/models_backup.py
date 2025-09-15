# core/models.py

from django.db import models

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