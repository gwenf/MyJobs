# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
import re
import mypartners.models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CommonEmailDomain',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('domain', models.CharField(unique=True, max_length=200)),
            ],
            options={
                'ordering': ['domain'],
            },
        ),
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('archived_on', models.DateTimeField(null=True)),
                ('name', models.CharField(help_text=b"Contact's full name", max_length=255, verbose_name=b'Full Name')),
                ('email', models.EmailField(help_text=b"Contact's email address", max_length=255, verbose_name=b'Email', blank=True)),
                ('phone', models.CharField(default=b'', help_text=b'ie (123) 456-7890', max_length=30, verbose_name=b'Phone', blank=True)),
                ('notes', models.TextField(default=b'', help_text=b'Any additional information you want to record', max_length=1000, verbose_name=b'Notes', blank=True)),
                ('last_action_time', models.DateTimeField(default=datetime.datetime.now, blank=True)),
            ],
            options={
                'verbose_name_plural': 'contacts',
            },
        ),
        migrations.CreateModel(
            name='ContactLogEntry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('action_flag', models.PositiveSmallIntegerField(verbose_name=b'action flag')),
                ('action_time', models.DateTimeField(auto_now=True, verbose_name=b'action time')),
                ('change_message', models.TextField(verbose_name=b'change message', blank=True)),
                ('contact_identifier', models.CharField(max_length=255)),
                ('delta', models.TextField(blank=True)),
                ('object_id', models.TextField(null=True, verbose_name=b'object id', blank=True)),
                ('object_repr', models.CharField(max_length=200, verbose_name=b'object repr')),
                ('successful', models.NullBooleanField(default=None)),
            ],
        ),
        migrations.CreateModel(
            name='ContactRecord',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('archived_on', models.DateTimeField(null=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('contact_type', models.CharField(max_length=50, verbose_name=b'Communication Type', choices=[(b'email', b'Email'), (b'phone', b'Phone'), (b'meetingorevent', b'Meeting or Event'), (b'job', b'Job Followup'), (b'pssemail', b'Partner Saved Search Email')])),
                ('contact_email', models.CharField(max_length=255, verbose_name=b'Contact Email', blank=True)),
                ('contact_phone', models.CharField(default=b'', max_length=30, verbose_name=b'Contact Phone Number', blank=True)),
                ('location', models.CharField(default=b'', max_length=255, verbose_name=b'Meeting Location', blank=True)),
                ('length', models.TimeField(null=True, verbose_name=b'Meeting Length', blank=True)),
                ('subject', models.CharField(default=b'', max_length=255, verbose_name=b'Subject or Topic', blank=True)),
                ('date_time', models.DateTimeField(verbose_name=b'Date & Time', blank=True)),
                ('notes', models.TextField(default=b'', max_length=1000, verbose_name=b'Details, Notes or Transcripts', blank=True)),
                ('job_id', models.CharField(default=b'', max_length=40, verbose_name=b'Job Number/ID', blank=True)),
                ('job_applications', models.CharField(default=b'', max_length=6, verbose_name=b'Number of Applications', blank=True)),
                ('job_interviews', models.CharField(default=b'', max_length=6, verbose_name=b'Number of Interviews', blank=True)),
                ('job_hires', models.CharField(default=b'', max_length=6, verbose_name=b'Number of Hires', blank=True)),
                ('last_action_time', models.DateTimeField(default=datetime.datetime.now, blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('address_line_one', models.CharField(help_text=b'ie 123 Main St', max_length=255, verbose_name=b'Address Line One', blank=True)),
                ('address_line_two', models.CharField(help_text=b'ie Suite 100', max_length=255, verbose_name=b'Address Line Two', blank=True)),
                ('city', models.CharField(help_text=b'ie Chicago, Washington, Dayton', max_length=255, verbose_name=b'City')),
                ('state', models.CharField(help_text=b'ie NY, WA, DC', max_length=200, verbose_name=b'State/Region')),
                ('country_code', models.CharField(default=b'USA', max_length=3, verbose_name=b'Country')),
                ('postal_code', models.CharField(help_text=b'ie 90210, 12345-7890', max_length=12, verbose_name=b'Postal Code', blank=True)),
                ('label', models.CharField(help_text=b'ie Main Office, Corporate, Regional', max_length=60, verbose_name=b'Address Name', blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='NonUserOutreach',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_added', models.DateTimeField(auto_now_add=True)),
                ('from_email', models.EmailField(help_text=b'Email outreach effort sent from.', max_length=255, verbose_name=b'Email')),
                ('email_body', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='OutreachEmailAddress',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('email', models.CharField(help_text=b'Email to send outreach efforts to.', unique=True, max_length=255, verbose_name=b'Email', validators=[django.core.validators.RegexValidator(re.compile('(^[-!#$%&\'*+/=?^_`{}|~0-9A-Z]+(\\.[-!#$%&\'*+/=?^_`{}|~0-9A-Z]+)*\\Z|^"([\\001-\\010\\013\\014\\016-\\037!#-\\[\\]-\\177]|\\\\[\\001-\\011\\013\\014\\016-\\177])*"\\Z)', 2), b'Enter a valid email username.')])),
            ],
        ),
        migrations.CreateModel(
            name='OutreachEmailDomain',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('domain', models.CharField(max_length=200)),
            ],
            options={
                'ordering': ['company', 'domain'],
            },
        ),
        migrations.CreateModel(
            name='OutreachWorkflowState',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('state', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Partner',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('archived_on', models.DateTimeField(null=True)),
                ('name', models.CharField(help_text=b'Name of the Organization', max_length=255, verbose_name=b'Partner Organization')),
                ('data_source', models.CharField(help_text=b'Website, event, or other source where you found the partner', max_length=255, verbose_name=b'Source', blank=True)),
                ('uri', models.URLField(help_text=b'Full url. ie http://partnerorganization.org', verbose_name=b'URL', blank=True)),
                ('last_action_time', models.DateTimeField(default=datetime.datetime.now, blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PartnerLibrary',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('data_source', models.CharField(default=b'Employment Referral Resource Directory', max_length=255)),
                ('name', models.CharField(max_length=255, verbose_name=b'Partner Organization')),
                ('uri', models.URLField(blank=True)),
                ('region', models.CharField(max_length=30, blank=True)),
                ('state', models.CharField(max_length=30, blank=True)),
                ('area', models.CharField(max_length=255, blank=True)),
                ('contact_name', models.CharField(max_length=255, blank=True)),
                ('phone', models.CharField(max_length=30, blank=True)),
                ('phone_ext', models.CharField(max_length=10, blank=True)),
                ('alt_phone', models.CharField(max_length=30, blank=True)),
                ('fax', models.CharField(max_length=30, blank=True)),
                ('email', models.CharField(max_length=255, blank=True)),
                ('street1', models.CharField(max_length=255, blank=True)),
                ('street2', models.CharField(max_length=255, blank=True)),
                ('city', models.CharField(max_length=255, blank=True)),
                ('st', models.CharField(max_length=10, blank=True)),
                ('zip_code', models.CharField(max_length=12, blank=True)),
                ('is_minority', models.BooleanField(default=False, verbose_name=b'minority')),
                ('is_female', models.BooleanField(default=False, verbose_name=b'female')),
                ('is_disabled', models.BooleanField(default=False, verbose_name=b'disabled')),
                ('is_veteran', models.BooleanField(default=False, verbose_name=b'veteran')),
                ('is_disabled_veteran', models.BooleanField(default=False, verbose_name=b'disabled_veteran')),
            ],
        ),
        migrations.CreateModel(
            name='PRMAttachment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('attachment', models.FileField(max_length=767, null=True, upload_to=mypartners.models.get_file_name, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Status',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('code', models.PositiveSmallIntegerField(default=1, verbose_name=b'Status Code', choices=[(0, b'Unprocessed'), (1, b'Approved'), (2, b'Denied')])),
                ('last_modified', models.DateTimeField(default=datetime.datetime.now, verbose_name=b'Last Modified', blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('hex_color', models.CharField(default=b'd4d4d4', max_length=6, blank=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'tag',
            },
        ),
    ]
