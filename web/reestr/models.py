# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Documents(models.Model):
    region = models.ForeignKey('Regions', models.CASCADE, blank=False, null=False)
    status_code = models.IntegerField(blank=True, null=True)
    url = models.TextField(blank=False, null=False)
    report_intermediate_docs_link = models.TextField(blank=True, null=True)
    report_project_date_start = models.DateTimeField(blank=True, null=True)
    report_project_date_end = models.DateTimeField(blank=True, null=True)
    update_date = models.DateTimeField(blank=True, null=True)

    # @property
    # def url_short(self) -> str:
    #     if len(self.url) < 50:
    #         return self.url
    #     return self.url[:50] + "..."

    class Meta:
        #managed = False
        verbose_name_plural = "Documents"
        db_table = 'documents'

    def __str__(self) -> str:
        return f"{self.region.name} #{self.region.id}"



class History(models.Model):
    document = models.ForeignKey(Documents, models.CASCADE, blank=False, null=False)
    status_code = models.IntegerField(blank=True, null=True)
    update_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        #managed = False
        verbose_name_plural = "History"
        db_table = 'history'


class Payments(models.Model):
    user = models.ForeignKey('Users', models.DO_NOTHING, blank=True, null=True)
    date = models.DateTimeField(blank=False, null=False)
    amount = models.IntegerField(blank=False, null=False)
    invoice_payload = models.TextField(blank=False, null=False)
    telegram_payment_charge_id = models.CharField(blank=True, null=True, max_length=200)
    provider_payment_charge_id = models.CharField(blank=False, null=False, max_length=200)

    class Meta:
        #managed = False
        verbose_name_plural = "Payments"
        db_table = 'payments'


class ReestrDocument(models.Model):
    status_code = models.IntegerField()
    url = models.TextField()
    report_intermediate_docs_link = models.TextField()
    report_project_date_start = models.DateTimeField()
    report_project_date_end = models.DateTimeField()
    update_date = models.DateTimeField()
    region_id = models.ForeignKey('ReestrRegion', models.DO_NOTHING)

    class Meta:
        #managed = False
        db_table = 'reestr_document'


class ReestrRegion(models.Model):
    name = models.CharField(unique=True, max_length=250)
    active = models.BooleanField()

    class Meta:
        #managed = False
        db_table = 'reestr_region'


class ReestrState(models.Model):
    name = models.CharField(unique=True, max_length=250)

    class Meta:
        #managed = False
        db_table = 'reestr_state'


class Regions(models.Model):
    name = models.CharField(unique=True, max_length=150)
    active = models.BooleanField(blank=True, null=True)

    class Meta:
        #managed = False
        verbose_name_plural = "Regions"
        db_table = 'regions'


class States(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        #managed = False
        verbose_name_plural = "States"
        db_table = 'states'


class Subscriptons(models.Model):
    user = models.ForeignKey('Users', models.CASCADE, blank=True, null=True)
    region = models.ForeignKey(Regions, models.DO_NOTHING, blank=True, null=True)
    payment = models.ForeignKey(Payments, models.DO_NOTHING, blank=True, null=True)
    start_time = models.DateTimeField(blank=True, null=True)
    end_time = models.DateTimeField(blank=True, null=True)
    notice_sent = models.BooleanField(blank=True, null=True)
    notice_date = models.DateTimeField(blank=True, null=True)
    scheduled = models.IntegerField(blank=True, null=True)
    notice_text = models.TextField(blank=True, null=True)
    send_from_time = models.TimeField(blank=True, null=True)
    send_upto_time = models.TimeField(blank=True, null=True)

    class Meta:
        #managed = False
        verbose_name_plural = "Subscriptons"
        db_table = 'subscriptons'


class Users(models.Model):
    registration_time = models.CharField(blank=True, null=True, max_length=150)
    accepted_contract = models.BooleanField(default=False)
    referrer = models.CharField(blank=True, null=True, max_length=100)

    class Meta:
        #managed = False
        verbose_name_plural = "Users"
        db_table = 'users'
