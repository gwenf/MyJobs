# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('mypartners', '0001_initial'),
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('seo', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='tag',
            name='company',
            field=models.ForeignKey(to='seo.Company'),
        ),
        migrations.AddField(
            model_name='tag',
            name='created_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='status',
            name='approved_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='prmattachment',
            name='contact_record',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='mypartners.ContactRecord', null=True),
        ),
        migrations.AddField(
            model_name='partner',
            name='approval_status',
            field=models.OneToOneField(null=True, verbose_name=b'Approval Status', to='mypartners.Status'),
        ),
        migrations.AddField(
            model_name='partner',
            name='library',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='mypartners.PartnerLibrary', null=True),
        ),
        migrations.AddField(
            model_name='partner',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='seo.Company', null=True),
        ),
        migrations.AddField(
            model_name='partner',
            name='primary_contact',
            field=models.ForeignKey(related_name='primary_contact', on_delete=django.db.models.deletion.SET_NULL, to='mypartners.Contact', help_text=b'Denotes who the primary contact is for this organization.', null=True),
        ),
        migrations.AddField(
            model_name='partner',
            name='tags',
            field=models.ManyToManyField(help_text=b"ie 'Disability', 'veteran-outreach', etc. Separate tags with a comma.", to='mypartners.Tag', null=True),
        ),
        migrations.AddField(
            model_name='outreachemaildomain',
            name='company',
            field=models.ForeignKey(to='seo.Company'),
        ),
        migrations.AddField(
            model_name='outreachemailaddress',
            name='company',
            field=models.ForeignKey(to='seo.Company'),
        ),
        migrations.AddField(
            model_name='nonuseroutreach',
            name='communication_records',
            field=models.ManyToManyField(to='mypartners.ContactRecord'),
        ),
        migrations.AddField(
            model_name='nonuseroutreach',
            name='contacts',
            field=models.ManyToManyField(to='mypartners.Contact'),
        ),
        migrations.AddField(
            model_name='nonuseroutreach',
            name='current_workflow_state',
            field=models.ForeignKey(to='mypartners.OutreachWorkflowState'),
        ),
        migrations.AddField(
            model_name='nonuseroutreach',
            name='outreach_email',
            field=models.ForeignKey(to='mypartners.OutreachEmailAddress'),
        ),
        migrations.AddField(
            model_name='nonuseroutreach',
            name='partners',
            field=models.ManyToManyField(to='mypartners.Partner'),
        ),
        migrations.AddField(
            model_name='contactrecord',
            name='approval_status',
            field=models.OneToOneField(null=True, verbose_name=b'Approval Status', to='mypartners.Status'),
        ),
        migrations.AddField(
            model_name='contactrecord',
            name='contact',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='mypartners.Contact', null=True),
        ),
        migrations.AddField(
            model_name='contactrecord',
            name='created_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='contactrecord',
            name='partner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='mypartners.Partner', null=True),
        ),
        migrations.AddField(
            model_name='contactrecord',
            name='tags',
            field=models.ManyToManyField(to='mypartners.Tag', null=True),
        ),
        migrations.AddField(
            model_name='contactlogentry',
            name='content_type',
            field=models.ForeignKey(blank=True, to='contenttypes.ContentType', null=True),
        ),
        migrations.AddField(
            model_name='contactlogentry',
            name='partner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='mypartners.Partner', null=True),
        ),
        migrations.AddField(
            model_name='contactlogentry',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='contact',
            name='approval_status',
            field=models.OneToOneField(null=True, verbose_name=b'Approval Status', to='mypartners.Status'),
        ),
        migrations.AddField(
            model_name='contact',
            name='library',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='mypartners.PartnerLibrary', null=True),
        ),
        migrations.AddField(
            model_name='contact',
            name='locations',
            field=models.ManyToManyField(related_name='contacts', to='mypartners.Location'),
        ),
        migrations.AddField(
            model_name='contact',
            name='partner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='mypartners.Partner', null=True),
        ),
        migrations.AddField(
            model_name='contact',
            name='tags',
            field=models.ManyToManyField(to='mypartners.Tag', null=True),
        ),
        migrations.AddField(
            model_name='contact',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AlterUniqueTogether(
            name='tag',
            unique_together=set([('name', 'company')]),
        ),
        migrations.AlterUniqueTogether(
            name='outreachemaildomain',
            unique_together=set([('company', 'domain')]),
        ),
    ]
