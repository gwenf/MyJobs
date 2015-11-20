# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmailSection',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('section_type', models.PositiveIntegerField(choices=[(1, b'Header'), (3, b'Footer')])),
                ('content', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='EmailTask',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('object_id', models.PositiveIntegerField()),
                ('event_id', models.PositiveIntegerField()),
                ('completed_on', models.DateTimeField(null=True, blank=True)),
                ('scheduled_for', models.DateTimeField(default=datetime.datetime.now)),
                ('scheduled_at', models.DateTimeField(auto_now_add=True)),
                ('task_id', models.CharField(default=b'', help_text=b'guid with dashes', max_length=36, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='EmailTemplate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('body', models.TextField()),
                ('is_active', models.BooleanField(default=False, verbose_name=b'IsActive')),
            ],
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_active', models.BooleanField(default=True)),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('model', models.ForeignKey(to='contenttypes.ContentType')),
            ],
        ),
    ]
