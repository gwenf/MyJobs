# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('myemails', '0001_initial'),
        ('seo', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='owner',
            field=models.ForeignKey(to='seo.Company'),
        ),
        migrations.AddField(
            model_name='event',
            name='sites',
            field=models.ManyToManyField(to='seo.SeoSite'),
        ),
        migrations.AddField(
            model_name='emailtemplate',
            name='event',
            field=models.ForeignKey(to='myemails.Event', null=True),
        ),
        migrations.AddField(
            model_name='emailtemplate',
            name='footer',
            field=models.ForeignKey(related_name='footer_for', to='myemails.EmailSection'),
        ),
        migrations.AddField(
            model_name='emailtemplate',
            name='header',
            field=models.ForeignKey(related_name='header_for', to='myemails.EmailSection'),
        ),
        migrations.AddField(
            model_name='emailtemplate',
            name='owner',
            field=models.ForeignKey(blank=True, to='seo.Company', null=True),
        ),
        migrations.AddField(
            model_name='emailtask',
            name='event_model',
            field=models.ForeignKey(related_name='email_type', to='contenttypes.ContentType'),
        ),
        migrations.AddField(
            model_name='emailtask',
            name='object_model',
            field=models.ForeignKey(related_name='email_model', to='contenttypes.ContentType'),
        ),
        migrations.AddField(
            model_name='emailsection',
            name='owner',
            field=models.ForeignKey(blank=True, to='seo.Company', null=True),
        ),
    ]
