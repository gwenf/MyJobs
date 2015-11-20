# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mysearches', '0002_auto_20151117_1452'),
        ('auth', '0006_require_contenttypes_0002'),
        ('myjobs', '0001_initial'),
        ('seo', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='role',
            name='company',
            field=models.ForeignKey(to='seo.Company'),
        ),
        migrations.AddField(
            model_name='emaillog',
            name='send_log',
            field=models.ForeignKey(related_name='sendgrid_response', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='mysearches.SavedSearchLog', help_text=b'Entries prior to the\n                                 release of saved search logging will\n                                 have no categories, meaning we cannot\n                                 match them with a SendGrid\n                                 response.', null=True),
        ),
        migrations.AddField(
            model_name='activity',
            name='app_access',
            field=models.ForeignKey(to='myjobs.AppAccess'),
        ),
        migrations.AddField(
            model_name='user',
            name='groups',
            field=models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Group', blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', verbose_name='groups'),
        ),
        migrations.AddField(
            model_name='user',
            name='roles',
            field=models.ManyToManyField(to='myjobs.Role'),
        ),
        migrations.AddField(
            model_name='user',
            name='user_permissions',
            field=models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Permission', blank=True, help_text='Specific permissions for this user.', verbose_name='user permissions'),
        ),
        migrations.AlterUniqueTogether(
            name='ticket',
            unique_together=set([('ticket', 'user')]),
        ),
        migrations.AlterUniqueTogether(
            name='role',
            unique_together=set([('company', 'name')]),
        ),
    ]
