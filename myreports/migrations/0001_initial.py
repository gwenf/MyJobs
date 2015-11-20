# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Column',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('table_name', models.CharField(max_length=50)),
                ('column_name', models.CharField(max_length=50)),
                ('is_active', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='ColumnFormat',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('format_code', models.CharField(max_length=2000)),
                ('is_active', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Configuration',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('is_active', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='ConfigurationColumn',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('alias', models.CharField(max_length=100)),
                ('multi_value_expansion', models.PositiveSmallIntegerField()),
                ('filter_only', models.BooleanField(default=False)),
                ('default_value', models.CharField(default=b'', max_length=500, blank=True)),
                ('is_active', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='ConfigurationColumnFormats',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_active', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='DataType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('data_type', models.CharField(max_length=100)),
                ('description', models.CharField(max_length=500)),
                ('is_active', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='DynamicReport',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('results', models.FileField(upload_to=b'reports')),
            ],
        ),
        migrations.CreateModel(
            name='InterfaceElementType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('interface_element_type', models.CharField(max_length=50)),
                ('description', models.CharField(max_length=500)),
                ('element_code', models.CharField(max_length=2000)),
                ('is_active', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='PresentationType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('presentation_type', models.CharField(max_length=100)),
                ('description', models.CharField(max_length=500)),
                ('is_active', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('order_by', models.CharField(default=b'', max_length=50, blank=True)),
                ('app', models.CharField(default=b'mypartners', max_length=50)),
                ('model', models.CharField(default=b'contactrecord', max_length=50)),
                ('values', models.CharField(default=b'[]', max_length=500)),
                ('filters', models.TextField(default=b'{}')),
                ('results', models.FileField(upload_to=b'reports')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ReportingType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('reporting_type', models.CharField(max_length=50)),
                ('description', models.CharField(max_length=500)),
                ('is_active', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='ReportingTypeReportTypes',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_active', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='ReportPresentation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('display_name', models.CharField(max_length=50)),
                ('is_active', models.BooleanField(default=False)),
                ('configuration', models.ForeignKey(to='myreports.Configuration')),
                ('presentation_type', models.ForeignKey(to='myreports.PresentationType')),
            ],
        ),
        migrations.CreateModel(
            name='ReportType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('report_type', models.CharField(max_length=50)),
                ('description', models.CharField(max_length=500)),
                ('is_active', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='ReportTypeDataTypes',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_active', models.BooleanField(default=False)),
                ('data_type', models.ForeignKey(to='myreports.DataType')),
                ('report_type', models.ForeignKey(to='myreports.ReportType')),
            ],
        ),
        migrations.CreateModel(
            name='UserReportingTypes',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_active', models.BooleanField(default=False)),
                ('reporting_type', models.ForeignKey(to='myreports.ReportingType')),
            ],
        ),
        migrations.CreateModel(
            name='UserType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('user_type', models.CharField(max_length=10)),
                ('is_active', models.BooleanField(default=False)),
                ('reporting_types', models.ManyToManyField(to='myreports.ReportingType', through='myreports.UserReportingTypes')),
            ],
        ),
        migrations.AddField(
            model_name='userreportingtypes',
            name='user_type',
            field=models.ForeignKey(to='myreports.UserType'),
        ),
        migrations.AddField(
            model_name='reporttype',
            name='data_types',
            field=models.ManyToManyField(to='myreports.DataType', through='myreports.ReportTypeDataTypes'),
        ),
        migrations.AddField(
            model_name='reportpresentation',
            name='report_data',
            field=models.ForeignKey(to='myreports.ReportTypeDataTypes'),
        ),
        migrations.AddField(
            model_name='reportingtypereporttypes',
            name='report_type',
            field=models.ForeignKey(to='myreports.ReportType'),
        ),
        migrations.AddField(
            model_name='reportingtypereporttypes',
            name='reporting_type',
            field=models.ForeignKey(to='myreports.ReportingType'),
        ),
        migrations.AddField(
            model_name='reportingtype',
            name='report_types',
            field=models.ManyToManyField(to='myreports.ReportType', through='myreports.ReportingTypeReportTypes'),
        ),
    ]
