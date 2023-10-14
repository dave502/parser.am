# Generated by Django 4.2.6 on 2023-10-13 15:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        # migrations.CreateModel(
        #     name='Documents',
        #     fields=[
        #         ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
        #         ('status_code', models.IntegerField(blank=True, null=True)),
        #         ('url', models.TextField()),
        #         ('report_intermediate_docs_link', models.TextField(blank=True, null=True)),
        #         ('report_project_date_start', models.DateTimeField(blank=True, null=True)),
        #         ('report_project_date_end', models.DateTimeField(blank=True, null=True)),
        #         ('update_date', models.DateTimeField(blank=True, null=True)),
        #     ],
        #     options={
        #         'db_table': 'documents',
        #     },
        # ),
        # migrations.CreateModel(
        #     name='Payments',
        #     fields=[
        #         ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
        #         ('date', models.DateTimeField()),
        #         ('amount', models.IntegerField()),
        #         ('invoice_payload', models.TextField()),
        #         ('telegram_payment_charge_id', models.CharField(blank=True, max_length=200, null=True)),
        #         ('provider_payment_charge_id', models.CharField(max_length=200)),
        #     ],
        #     options={
        #         'db_table': 'payments',
        #     },
        # ),
        # migrations.CreateModel(
        #     name='ReestrRegion',
        #     fields=[
        #         ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
        #         ('name', models.CharField(max_length=250, unique=True)),
        #         ('active', models.BooleanField()),
        #     ],
        #     options={
        #         'db_table': 'reestr_region',
        #     },
        # ),
        # migrations.CreateModel(
        #     name='ReestrState',
        #     fields=[
        #         ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
        #         ('name', models.CharField(max_length=250, unique=True)),
        #     ],
        #     options={
        #         'db_table': 'reestr_state',
        #     },
        # ),
        # migrations.CreateModel(
        #     name='Regions',
        #     fields=[
        #         ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
        #         ('name', models.CharField(max_length=150, unique=True)),
        #         ('active', models.BooleanField(blank=True, null=True)),
        #     ],
        #     options={
        #         'db_table': 'regions',
        #     },
        # ),
        # migrations.CreateModel(
        #     name='States',
        #     fields=[
        #         ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
        #         ('name', models.CharField(max_length=150, unique=True)),
        #     ],
        #     options={
        #         'db_table': 'states',
        #     },
        # ),
        # migrations.CreateModel(
        #     name='Users',
        #     fields=[
        #         ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
        #         ('registration_time', models.CharField(blank=True, max_length=150, null=True)),
        #         ('accepted_contract', models.BooleanField(default=False)),
        #         ('referrer', models.CharField(blank=True, max_length=100, null=True)),
        #     ],
        #     options={
        #         'db_table': 'users',
        #     },
        # ),
        # migrations.CreateModel(
        #     name='Subscriptons',
        #     fields=[
        #         ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
        #         ('start_time', models.DateTimeField(blank=True, null=True)),
        #         ('end_time', models.DateTimeField(blank=True, null=True)),
        #         ('notice_sent', models.BooleanField(blank=True, null=True)),
        #         ('notice_date', models.DateTimeField(blank=True, null=True)),
        #         ('scheduled', models.IntegerField(blank=True, null=True)),
        #         ('notice_text', models.TextField(blank=True, null=True)),
        #         ('send_from_time', models.TimeField(blank=True, null=True)),
        #         ('send_upto_time', models.TimeField(blank=True, null=True)),
        #         ('payment', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='reestr.payments')),
        #         ('region', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='reestr.regions')),
        #         ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='reestr.users')),
        #     ],
        #     options={
        #         'db_table': 'subscriptons',
        #     },
        # ),
        # migrations.CreateModel(
        #     name='ReestrDocument',
        #     fields=[
        #         ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
        #         ('status_code', models.IntegerField()),
        #         ('url', models.TextField()),
        #         ('report_intermediate_docs_link', models.TextField()),
        #         ('report_project_date_start', models.DateTimeField()),
        #         ('report_project_date_end', models.DateTimeField()),
        #         ('update_date', models.DateTimeField()),
        #         ('region_id', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='reestr.reestrregion')),
        #     ],
        #     options={
        #         'db_table': 'reestr_document',
        #     },
        # ),
        # migrations.AddField(
        #     model_name='payments',
        #     name='user',
        #     field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='reestr.users'),
        # ),
        # migrations.CreateModel(
        #     name='History',
        #     fields=[
        #         ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
        #         ('status_code', models.IntegerField(blank=True, null=True)),
        #         ('update_date', models.DateTimeField(blank=True, null=True)),
        #         ('document', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reestr.documents')),
        #     ],
        #     options={
        #         'db_table': 'history',
        #     },
        # ),
        # migrations.AddField(
        #     model_name='documents',
        #     name='region',
        #     field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reestr.regions'),
        # ),
    ]
