# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Block',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('element_id', models.CharField(max_length=255, null=True)),
                ('name', models.CharField(max_length=255)),
                ('offset', models.PositiveIntegerField()),
                ('span', models.PositiveIntegerField()),
                ('template', models.TextField()),
                ('head', models.TextField(blank=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='BlockOrder',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order', models.PositiveIntegerField()),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ('order',),
            },
        ),
        migrations.CreateModel(
            name='ColumnBlockOrder',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order', models.PositiveIntegerField()),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ('order',),
            },
        ),
        migrations.CreateModel(
            name='Page',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('page_type', models.CharField(max_length=255, choices=[(b'404', b'404'), (b'home_page', b'Home Page'), (b'job_detail', b'Job Detail Page'), (b'search_results', b'Job Search Results Page'), (b'login', b'Login Page'), (b'no_results', b'No Results Found')])),
                ('name', models.CharField(max_length=255)),
                ('status', models.CharField(default=b'production', max_length=255, choices=[(b'staging', b'Staging'), (b'production', b'Production')])),
                ('head', models.TextField(blank=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('doc_type', models.CharField(default=b'', max_length=255, choices=[(b'', b'Inherit from Configuration'), (b'<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">', b'HTML 4.01 Transitional'), (b'<!DOCTYPE html>', b'HTML 5')])),
                ('language_code', models.CharField(default=b'', max_length=16, choices=[(b'', b'Inherit from Configuration'), (b'zh', b'Chinese'), (b'da', b'Danish'), (b'en', b'English'), (b'fr', b'French'), (b'de', b'German'), (b'hi', b'Hindi'), (b'it', b'Italian'), (b'ja', b'Japanese'), (b'ko', b'Korean'), (b'pt', b'Portuguese'), (b'ru', b'Russian'), (b'es', b'Spanish')])),
            ],
        ),
        migrations.CreateModel(
            name='Row',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='RowOrder',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order', models.PositiveIntegerField()),
                ('updated', models.DateTimeField(auto_now=True)),
                ('page', models.ForeignKey(to='myblocks.Page')),
                ('row', models.ForeignKey(to='myblocks.Row')),
            ],
            options={
                'ordering': ('order',),
            },
        ),
        migrations.CreateModel(
            name='ApplyLinkBlock',
            fields=[
                ('block_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='myblocks.Block')),
            ],
            bases=('myblocks.block',),
        ),
        migrations.CreateModel(
            name='BreadboxBlock',
            fields=[
                ('block_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='myblocks.Block')),
            ],
            bases=('myblocks.block',),
        ),
        migrations.CreateModel(
            name='ColumnBlock',
            fields=[
                ('block_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='myblocks.Block')),
            ],
            bases=('myblocks.block',),
        ),
        migrations.CreateModel(
            name='ContentBlock',
            fields=[
                ('block_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='myblocks.Block')),
            ],
            bases=('myblocks.block',),
        ),
        migrations.CreateModel(
            name='FacetBlurbBlock',
            fields=[
                ('block_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='myblocks.Block')),
            ],
            bases=('myblocks.block',),
        ),
        migrations.CreateModel(
            name='JobDetailBlock',
            fields=[
                ('block_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='myblocks.Block')),
            ],
            bases=('myblocks.block',),
        ),
        migrations.CreateModel(
            name='JobDetailBreadboxBlock',
            fields=[
                ('block_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='myblocks.Block')),
            ],
            bases=('myblocks.block',),
        ),
        migrations.CreateModel(
            name='JobDetailHeaderBlock',
            fields=[
                ('block_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='myblocks.Block')),
            ],
            bases=('myblocks.block',),
        ),
        migrations.CreateModel(
            name='LoginBlock',
            fields=[
                ('block_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='myblocks.Block')),
            ],
            bases=('myblocks.block',),
        ),
        migrations.CreateModel(
            name='MoreButtonBlock',
            fields=[
                ('block_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='myblocks.Block')),
            ],
            bases=('myblocks.block',),
        ),
        migrations.CreateModel(
            name='RegistrationBlock',
            fields=[
                ('block_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='myblocks.Block')),
            ],
            bases=('myblocks.block',),
        ),
        migrations.CreateModel(
            name='SavedSearchWidgetBlock',
            fields=[
                ('block_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='myblocks.Block')),
            ],
            bases=('myblocks.block',),
        ),
        migrations.CreateModel(
            name='SearchBoxBlock',
            fields=[
                ('block_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='myblocks.Block')),
            ],
            bases=('myblocks.block',),
        ),
        migrations.CreateModel(
            name='SearchFilterBlock',
            fields=[
                ('block_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='myblocks.Block')),
            ],
            bases=('myblocks.block',),
        ),
        migrations.CreateModel(
            name='SearchResultBlock',
            fields=[
                ('block_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='myblocks.Block')),
            ],
            bases=('myblocks.block',),
        ),
        migrations.CreateModel(
            name='SearchResultHeaderBlock',
            fields=[
                ('block_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='myblocks.Block')),
            ],
            bases=('myblocks.block',),
        ),
        migrations.CreateModel(
            name='ShareBlock',
            fields=[
                ('block_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='myblocks.Block')),
            ],
            bases=('myblocks.block',),
        ),
        migrations.CreateModel(
            name='VeteranSearchBox',
            fields=[
                ('block_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='myblocks.Block')),
            ],
            bases=('myblocks.block',),
        ),
        migrations.AddField(
            model_name='row',
            name='blocks',
            field=models.ManyToManyField(to='myblocks.Block', through='myblocks.BlockOrder'),
        ),
        migrations.AddField(
            model_name='page',
            name='rows',
            field=models.ManyToManyField(to='myblocks.Row', through='myblocks.RowOrder'),
        ),
    ]
