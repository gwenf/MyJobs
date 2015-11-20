# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('myblocks', '0001_initial'),
        ('seo', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='page',
            name='sites',
            field=models.ManyToManyField(to='seo.SeoSite'),
        ),
        migrations.AddField(
            model_name='columnblockorder',
            name='block',
            field=models.ForeignKey(to='myblocks.Block'),
        ),
        migrations.AddField(
            model_name='blockorder',
            name='block',
            field=models.ForeignKey(to='myblocks.Block'),
        ),
        migrations.AddField(
            model_name='blockorder',
            name='row',
            field=models.ForeignKey(to='myblocks.Row'),
        ),
        migrations.AddField(
            model_name='block',
            name='content_type',
            field=models.ForeignKey(editable=False, to='contenttypes.ContentType'),
        ),
        migrations.AddField(
            model_name='columnblockorder',
            name='column_block',
            field=models.ForeignKey(related_name='included_column_blocks', to='myblocks.ColumnBlock'),
        ),
        migrations.AddField(
            model_name='columnblock',
            name='blocks',
            field=models.ManyToManyField(related_name='included_blocks', through='myblocks.ColumnBlockOrder', to='myblocks.Block'),
        ),
    ]
