# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('myreports', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('seo', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='report',
            name='owner',
            field=models.ForeignKey(to='seo.Company'),
        ),
        migrations.AddField(
            model_name='dynamicreport',
            name='created_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='dynamicreport',
            name='owner',
            field=models.ForeignKey(to='seo.Company'),
        ),
        migrations.AddField(
            model_name='dynamicreport',
            name='report_presentation',
            field=models.ForeignKey(to='myreports.ReportPresentation'),
        ),
        migrations.AddField(
            model_name='configurationcolumnformats',
            name='column_format',
            field=models.ForeignKey(to='myreports.ColumnFormat'),
        ),
        migrations.AddField(
            model_name='configurationcolumnformats',
            name='configuration_column',
            field=models.ForeignKey(to='myreports.ConfigurationColumn'),
        ),
        migrations.AddField(
            model_name='configurationcolumn',
            name='column',
            field=models.ForeignKey(to='myreports.Column', null=True),
        ),
        migrations.AddField(
            model_name='configurationcolumn',
            name='column_formats',
            field=models.ManyToManyField(to='myreports.ColumnFormat', through='myreports.ConfigurationColumnFormats'),
        ),
        migrations.AddField(
            model_name='configurationcolumn',
            name='configuration',
            field=models.ForeignKey(to='myreports.Configuration'),
        ),
        migrations.AddField(
            model_name='configurationcolumn',
            name='interface_element_type',
            field=models.ForeignKey(to='myreports.InterfaceElementType'),
        ),
    ]
