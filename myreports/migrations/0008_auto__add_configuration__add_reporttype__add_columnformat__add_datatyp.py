# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Configuration'
        db.create_table(u'myreports_configuration', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'myreports', ['Configuration'])

        # Adding model 'ReportType'
        db.create_table(u'myreports_reporttype', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('report_type', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('description', self.gf('django.db.models.fields.TextField')(max_length=500)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'myreports', ['ReportType'])

        # Adding M2M table for field data_types on 'ReportType'
        m2m_table_name = db.shorten_name(u'myreports_reporttype_data_types')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('reporttype', models.ForeignKey(orm[u'myreports.reporttype'], null=False)),
            ('datatype', models.ForeignKey(orm[u'myreports.datatype'], null=False))
        ))
        db.create_unique(m2m_table_name, ['reporttype_id', 'datatype_id'])

        # Adding model 'ColumnFormat'
        db.create_table(u'myreports_columnformat', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('format_code', self.gf('django.db.models.fields.CharField')(max_length=2000)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'myreports', ['ColumnFormat'])

        # Adding model 'DataType'
        db.create_table(u'myreports_datatype', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('data_type', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('description', self.gf('django.db.models.fields.TextField')(max_length=500)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'myreports', ['DataType'])

        # Adding model 'ReportingType'
        db.create_table(u'myreports_reportingtype', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('reporting_type', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('description', self.gf('django.db.models.fields.TextField')(max_length=500)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'myreports', ['ReportingType'])

        # Adding M2M table for field user_types on 'ReportingType'
        m2m_table_name = db.shorten_name(u'myreports_reportingtype_user_types')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('reportingtype', models.ForeignKey(orm[u'myreports.reportingtype'], null=False)),
            ('usertype', models.ForeignKey(orm[u'myreports.usertype'], null=False))
        ))
        db.create_unique(m2m_table_name, ['reportingtype_id', 'usertype_id'])

        # Adding M2M table for field report_types on 'ReportingType'
        m2m_table_name = db.shorten_name(u'myreports_reportingtype_report_types')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('reportingtype', models.ForeignKey(orm[u'myreports.reportingtype'], null=False)),
            ('reporttype', models.ForeignKey(orm[u'myreports.reporttype'], null=False))
        ))
        db.create_unique(m2m_table_name, ['reportingtype_id', 'reporttype_id'])

        # Adding model 'PresentationType'
        db.create_table(u'myreports_presentationtype', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('presentation_type', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('description', self.gf('django.db.models.fields.TextField')(max_length=500)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'myreports', ['PresentationType'])

        # Adding model 'UserType'
        db.create_table(u'myreports_usertype', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user_type', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'myreports', ['UserType'])

        # Adding model 'ReportRepresentation'
        db.create_table(u'myreports_reportrepresentation', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('presentation_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['myreports.PresentationType'])),
            ('data_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['myreports.DataType'])),
            ('configuration', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['myreports.Configuration'])),
        ))
        db.send_create_signal(u'myreports', ['ReportRepresentation'])

        # Adding model 'ConfigurationColumn'
        db.create_table(u'myreports_configurationcolumn', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('configuration', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['myreports.Configuration'])),
            ('column', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['myreports.Column'])),
            ('interface_element_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['myreports.InterfaceElementType'])),
            ('alias', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('multi_value_expansion', self.gf('django.db.models.fields.PositiveSmallIntegerField')()),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'myreports', ['ConfigurationColumn'])

        # Adding M2M table for field column_formats on 'ConfigurationColumn'
        m2m_table_name = db.shorten_name(u'myreports_configurationcolumn_column_formats')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('configurationcolumn', models.ForeignKey(orm[u'myreports.configurationcolumn'], null=False)),
            ('columnformat', models.ForeignKey(orm[u'myreports.columnformat'], null=False))
        ))
        db.create_unique(m2m_table_name, ['configurationcolumn_id', 'columnformat_id'])

        # Adding model 'Column'
        db.create_table(u'myreports_column', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('table_name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('column_name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'myreports', ['Column'])

        # Adding model 'InterfaceElementType'
        db.create_table(u'myreports_interfaceelementtype', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('interface_element_type', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('description', self.gf('django.db.models.fields.TextField')(max_length=500)),
            ('element_code', self.gf('django.db.models.fields.CharField')(max_length=2000)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'myreports', ['InterfaceElementType'])


    def backwards(self, orm):
        # Deleting model 'Configuration'
        db.delete_table(u'myreports_configuration')

        # Deleting model 'ReportType'
        db.delete_table(u'myreports_reporttype')

        # Removing M2M table for field data_types on 'ReportType'
        db.delete_table(db.shorten_name(u'myreports_reporttype_data_types'))

        # Deleting model 'ColumnFormat'
        db.delete_table(u'myreports_columnformat')

        # Deleting model 'DataType'
        db.delete_table(u'myreports_datatype')

        # Deleting model 'ReportingType'
        db.delete_table(u'myreports_reportingtype')

        # Removing M2M table for field user_types on 'ReportingType'
        db.delete_table(db.shorten_name(u'myreports_reportingtype_user_types'))

        # Removing M2M table for field report_types on 'ReportingType'
        db.delete_table(db.shorten_name(u'myreports_reportingtype_report_types'))

        # Deleting model 'PresentationType'
        db.delete_table(u'myreports_presentationtype')

        # Deleting model 'UserType'
        db.delete_table(u'myreports_usertype')

        # Deleting model 'ReportRepresentation'
        db.delete_table(u'myreports_reportrepresentation')

        # Deleting model 'ConfigurationColumn'
        db.delete_table(u'myreports_configurationcolumn')

        # Removing M2M table for field column_formats on 'ConfigurationColumn'
        db.delete_table(db.shorten_name(u'myreports_configurationcolumn_column_formats'))

        # Deleting model 'Column'
        db.delete_table(u'myreports_column')

        # Deleting model 'InterfaceElementType'
        db.delete_table(u'myreports_interfaceelementtype')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'myjobs.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'deactivate_type': ('django.db.models.fields.CharField', [], {'default': "'none'", 'max_length': '11'}),
            'email': ('django.db.models.fields.EmailField', [], {'unique': 'True', 'max_length': '255', 'db_index': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'gravatar': ('django.db.models.fields.EmailField', [], {'db_index': 'True', 'max_length': '255', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'in_reserve': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_disabled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_verified': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'last_response': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'opt_in_employers': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'opt_in_myjobs': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'password_change': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'profile_completion': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'source': ('django.db.models.fields.CharField', [], {'default': "'https://secure.my.jobs'", 'max_length': '255'}),
            'timezone': ('django.db.models.fields.CharField', [], {'default': "'America/New_York'", 'max_length': '255'}),
            'user_guid': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100', 'db_index': 'True'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"})
        },
        u'myreports.column': {
            'Meta': {'object_name': 'Column'},
            'column_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'table_name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'myreports.columnformat': {
            'Meta': {'object_name': 'ColumnFormat'},
            'format_code': ('django.db.models.fields.CharField', [], {'max_length': '2000'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'myreports.configuration': {
            'Meta': {'object_name': 'Configuration'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'myreports.configurationcolumn': {
            'Meta': {'object_name': 'ConfigurationColumn'},
            'alias': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'column': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['myreports.Column']"}),
            'column_formats': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['myreports.ColumnFormat']", 'symmetrical': 'False'}),
            'configuration': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['myreports.Configuration']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'interface_element_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['myreports.InterfaceElementType']"}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'multi_value_expansion': ('django.db.models.fields.PositiveSmallIntegerField', [], {})
        },
        u'myreports.datatype': {
            'Meta': {'object_name': 'DataType'},
            'data_type': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'description': ('django.db.models.fields.TextField', [], {'max_length': '500'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'myreports.interfaceelementtype': {
            'Meta': {'object_name': 'InterfaceElementType'},
            'description': ('django.db.models.fields.TextField', [], {'max_length': '500'}),
            'element_code': ('django.db.models.fields.CharField', [], {'max_length': '2000'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'interface_element_type': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'myreports.presentationtype': {
            'Meta': {'object_name': 'PresentationType'},
            'description': ('django.db.models.fields.TextField', [], {'max_length': '500'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'presentation_type': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'myreports.report': {
            'Meta': {'object_name': 'Report'},
            'app': ('django.db.models.fields.CharField', [], {'default': "'mypartners'", 'max_length': '50'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['myjobs.User']", 'null': 'True', 'on_delete': 'models.SET_NULL'}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'filters': ('django.db.models.fields.TextField', [], {'default': "'{}'"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'default': "'contactrecord'", 'max_length': '50'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'order_by': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '50', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['seo.Company']"}),
            'results': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'values': ('django.db.models.fields.CharField', [], {'default': "'[]'", 'max_length': '500'})
        },
        u'myreports.reportingtype': {
            'Meta': {'object_name': 'ReportingType'},
            'description': ('django.db.models.fields.TextField', [], {'max_length': '500'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'report_types': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['myreports.ReportType']", 'symmetrical': 'False'}),
            'reporting_type': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'user_types': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['myreports.UserType']", 'symmetrical': 'False'})
        },
        u'myreports.reportrepresentation': {
            'Meta': {'object_name': 'ReportRepresentation'},
            'configuration': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['myreports.Configuration']"}),
            'data_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['myreports.DataType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'presentation_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['myreports.PresentationType']"})
        },
        u'myreports.reporttype': {
            'Meta': {'object_name': 'ReportType'},
            'data_types': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['myreports.DataType']", 'symmetrical': 'False'}),
            'description': ('django.db.models.fields.TextField', [], {'max_length': '500'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'report_type': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'myreports.usertype': {
            'Meta': {'object_name': 'UserType'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'user_type': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        },
        u'postajob.package': {
            'Meta': {'object_name': 'Package'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'postajob.sitepackage': {
            'Meta': {'object_name': 'SitePackage', '_ormbases': [u'postajob.Package']},
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['seo.Company']", 'null': 'True', 'blank': 'True'}),
            u'package_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['postajob.Package']", 'unique': 'True', 'primary_key': 'True'}),
            'sites': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['seo.SeoSite']", 'null': 'True', 'symmetrical': 'False'})
        },
        u'redirects.redirect': {
            'Meta': {'ordering': "('old_path',)", 'unique_together': "(('site', 'old_path'),)", 'object_name': 'Redirect', 'db_table': "'django_redirect'"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'new_path': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'old_path': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['sites.Site']"})
        },
        u'seo.atssourcecode': {
            'Meta': {'object_name': 'ATSSourceCode'},
            'ats_name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.Group']", 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200'}),
            'value': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200'})
        },
        u'seo.billboardimage': {
            'Meta': {'object_name': 'BillboardImage'},
            'copyright_info': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.Group']", 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image_url': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'logo_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'source_url': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'sponsor_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'seo.businessunit': {
            'Meta': {'object_name': 'BusinessUnit'},
            'associated_jobs': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'date_crawled': ('django.db.models.fields.DateTimeField', [], {}),
            'date_updated': ('django.db.models.fields.DateTimeField', [], {}),
            'enable_markdown': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'federal_contractor': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.IntegerField', [], {'max_length': '10', 'primary_key': 'True'}),
            'ignore_includeinindex': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'site_packages': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['postajob.SitePackage']", 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '500', 'null': 'True', 'blank': 'True'}),
            'title_slug': ('django.db.models.fields.SlugField', [], {'max_length': '500', 'null': 'True', 'blank': 'True'})
        },
        u'seo.company': {
            'Meta': {'ordering': "['name']", 'unique_together': "(('name', 'user_created'),)", 'object_name': 'Company'},
            'admins': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['myjobs.User']", 'through': u"orm['seo.CompanyUser']", 'symmetrical': 'False'}),
            'canonical_microsite': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'company_slug': ('django.db.models.fields.SlugField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'digital_strategies_customer': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'enhanced': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'job_source_ids': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['seo.BusinessUnit']", 'symmetrical': 'False'}),
            'linkedin_id': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'logo_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'member': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'og_img': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'posting_access': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'prm_access': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'prm_saved_search_sites': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['seo.SeoSite']", 'null': 'True', 'blank': 'True'}),
            'product_access': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'site_package': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['postajob.SitePackage']", 'null': 'True', 'on_delete': 'models.SET_NULL'}),
            'user_created': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'seo.companyuser': {
            'Meta': {'unique_together': "(('user', 'company'),)", 'object_name': 'CompanyUser', 'db_table': "'mydashboard_companyuser'"},
            'company': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['seo.Company']"}),
            'date_added': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'group': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['myjobs.User']"})
        },
        u'seo.configuration': {
            'Meta': {'object_name': 'Configuration'},
            'backgroundColor': ('django.db.models.fields.CharField', [], {'max_length': '6', 'null': 'True', 'blank': 'True'}),
            'body': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'browse_city_order': ('django.db.models.fields.IntegerField', [], {'default': '5'}),
            'browse_city_show': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'browse_city_text': ('django.db.models.fields.CharField', [], {'default': "'City'", 'max_length': '50'}),
            'browse_company_order': ('django.db.models.fields.IntegerField', [], {'default': '7'}),
            'browse_company_show': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'browse_company_text': ('django.db.models.fields.CharField', [], {'default': "'Company'", 'max_length': '50'}),
            'browse_country_order': ('django.db.models.fields.IntegerField', [], {'default': '3'}),
            'browse_country_show': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'browse_country_text': ('django.db.models.fields.CharField', [], {'default': "'Country'", 'max_length': '50'}),
            'browse_facet_order': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'browse_facet_order_2': ('django.db.models.fields.IntegerField', [], {'default': '2'}),
            'browse_facet_order_3': ('django.db.models.fields.IntegerField', [], {'default': '3'}),
            'browse_facet_order_4': ('django.db.models.fields.IntegerField', [], {'default': '4'}),
            'browse_facet_show': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'browse_facet_show_2': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'browse_facet_show_3': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'browse_facet_show_4': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'browse_facet_text': ('django.db.models.fields.CharField', [], {'default': "'Job Profiles'", 'max_length': '50'}),
            'browse_facet_text_2': ('django.db.models.fields.CharField', [], {'default': "'Job Profiles'", 'max_length': '50'}),
            'browse_facet_text_3': ('django.db.models.fields.CharField', [], {'default': "'Job Profiles'", 'max_length': '50'}),
            'browse_facet_text_4': ('django.db.models.fields.CharField', [], {'default': "'Job Profiles'", 'max_length': '50'}),
            'browse_moc_order': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'browse_moc_show': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'browse_moc_text': ('django.db.models.fields.CharField', [], {'default': "'Military Titles'", 'max_length': '50'}),
            'browse_state_order': ('django.db.models.fields.IntegerField', [], {'default': '4'}),
            'browse_state_show': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'browse_state_text': ('django.db.models.fields.CharField', [], {'default': "'State'", 'max_length': '50'}),
            'browse_title_order': ('django.db.models.fields.IntegerField', [], {'default': '6'}),
            'browse_title_show': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'browse_title_text': ('django.db.models.fields.CharField', [], {'default': "'Title'", 'max_length': '50'}),
            'company_tag': ('django.db.models.fields.CharField', [], {'default': "'careers'", 'max_length': '50'}),
            'defaultBlurb': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'defaultBlurbTitle': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'directemployers_link': ('django.db.models.fields.URLField', [], {'default': "'http://directemployers.org'", 'max_length': '200'}),
            'facet_tag': ('django.db.models.fields.CharField', [], {'default': "'new-jobs'", 'max_length': '50'}),
            'fontColor': ('django.db.models.fields.CharField', [], {'default': "'666666'", 'max_length': '6'}),
            'footer': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.Group']", 'null': 'True'}),
            'header': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'home_page_template': ('django.db.models.fields.CharField', [], {'default': "'home_page/home_page_listing.html'", 'max_length': '200'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location_tag': ('django.db.models.fields.CharField', [], {'default': "'jobs'", 'max_length': '50'}),
            'meta': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'moc_helptext': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'moc_label': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'moc_placeholder': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'moc_tag': ('django.db.models.fields.CharField', [], {'default': "'vet-jobs'", 'max_length': '50'}),
            'not_found_override': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['redirects.Redirect']", 'null': 'True', 'blank': 'True'}),
            'num_filter_items_to_show': ('django.db.models.fields.IntegerField', [], {'default': '10'}),
            'num_job_items_to_show': ('django.db.models.fields.IntegerField', [], {'default': '15'}),
            'num_subnav_items_to_show': ('django.db.models.fields.IntegerField', [], {'default': '9'}),
            'percent_featured': ('django.db.models.fields.DecimalField', [], {'default': "'0.5'", 'max_digits': '3', 'decimal_places': '2'}),
            'primaryColor': ('django.db.models.fields.CharField', [], {'default': "'990000'", 'max_length': '6'}),
            'publisher': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'revision': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'show_home_microsite_carousel': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'show_home_social_footer': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'show_saved_search_widget': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'show_social_footer': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '1', 'null': 'True', 'db_index': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'title_tag': ('django.db.models.fields.CharField', [], {'default': "'jobs-in'", 'max_length': '50'}),
            'view_all_jobs_detail': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'what_helptext': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'what_label': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'what_placeholder': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'where_helptext': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'where_label': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'where_placeholder': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'wide_footer': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'wide_header': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        u'seo.customfacet': {
            'Meta': {'object_name': 'CustomFacet'},
            'always_show': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'blurb': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'business_units': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['seo.BusinessUnit']", 'null': 'True', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '800', 'null': 'True', 'blank': 'True'}),
            'company': ('django.db.models.fields.CharField', [], {'max_length': '800', 'null': 'True', 'blank': 'True'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '800', 'null': 'True', 'blank': 'True'}),
            'date_created': ('django.db.models.fields.DateField', [], {'auto_now': 'True', 'blank': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.Group']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name_slug': ('django.db.models.fields.SlugField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'onet': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'querystring': ('django.db.models.fields.CharField', [], {'max_length': '2000', 'null': 'True', 'blank': 'True'}),
            'saved_querystring': ('django.db.models.fields.CharField', [], {'max_length': '10000', 'blank': 'True'}),
            'show_blurb': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'show_production': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '800', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '800', 'null': 'True', 'blank': 'True'}),
            'url_slab': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        u'seo.googleanalytics': {
            'Meta': {'object_name': 'GoogleAnalytics'},
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.Group']", 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'web_property_id': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        u'seo.googleanalyticscampaign': {
            'Meta': {'object_name': 'GoogleAnalyticsCampaign'},
            'campaign_content': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200'}),
            'campaign_medium': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200'}),
            'campaign_name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200'}),
            'campaign_source': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200'}),
            'campaign_term': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.Group']", 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200'})
        },
        u'seo.seosite': {
            'Meta': {'ordering': "(u'domain',)", 'object_name': 'SeoSite', '_ormbases': [u'sites.Site']},
            'ats_source_codes': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['seo.ATSSourceCode']", 'null': 'True', 'blank': 'True'}),
            'billboard_images': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['seo.BillboardImage']", 'null': 'True', 'blank': 'True'}),
            'business_units': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['seo.BusinessUnit']", 'null': 'True', 'blank': 'True'}),
            'canonical_company': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'canonical_company_for'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['seo.Company']"}),
            'configurations': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['seo.Configuration']", 'symmetrical': 'False', 'blank': 'True'}),
            'email_domain': ('django.db.models.fields.CharField', [], {'default': "'my.jobs'", 'max_length': '255'}),
            'facets': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['seo.CustomFacet']", 'null': 'True', 'through': u"orm['seo.SeoSiteFacet']", 'blank': 'True'}),
            'featured_companies': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['seo.Company']", 'null': 'True', 'blank': 'True'}),
            'google_analytics': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['seo.GoogleAnalytics']", 'null': 'True', 'blank': 'True'}),
            'google_analytics_campaigns': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['seo.GoogleAnalyticsCampaign']", 'null': 'True', 'blank': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.Group']", 'null': 'True'}),
            'microsite_carousel': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['social_links.MicrositeCarousel']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'parent_site': ('seo.models.NonChainedForeignKey', [], {'blank': 'True', 'related_name': "'child_sites'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['seo.SeoSite']"}),
            'postajob_filter_type': ('django.db.models.fields.CharField', [], {'default': "'this site only'", 'max_length': '255'}),
            'site_description': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200', 'blank': 'True'}),
            'site_heading': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200', 'blank': 'True'}),
            'site_package': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['postajob.SitePackage']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            u'site_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['sites.Site']", 'unique': 'True', 'primary_key': 'True'}),
            'site_tags': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['seo.SiteTag']", 'null': 'True', 'blank': 'True'}),
            'site_title': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200', 'blank': 'True'}),
            'special_commitments': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['seo.SpecialCommitment']", 'null': 'True', 'blank': 'True'}),
            'view_sources': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['seo.ViewSource']", 'null': 'True', 'blank': 'True'})
        },
        u'seo.seositefacet': {
            'Meta': {'object_name': 'SeoSiteFacet'},
            'boolean_operation': ('django.db.models.fields.CharField', [], {'default': "'or'", 'max_length': '3', 'db_index': 'True'}),
            'customfacet': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['seo.CustomFacet']"}),
            'facet_group': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'facet_type': ('django.db.models.fields.CharField', [], {'default': "'STD'", 'max_length': '4', 'db_index': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'seosite': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['seo.SeoSite']"})
        },
        u'seo.sitetag': {
            'Meta': {'object_name': 'SiteTag'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'site_tag': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'tag_navigation': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'seo.specialcommitment': {
            'Meta': {'object_name': 'SpecialCommitment'},
            'commit': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'seo.viewsource': {
            'Meta': {'object_name': 'ViewSource'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200'}),
            'view_source': ('django.db.models.fields.IntegerField', [], {'default': "''", 'max_length': '20'})
        },
        u'sites.site': {
            'Meta': {'ordering': "(u'domain',)", 'object_name': 'Site', 'db_table': "u'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'social_links.micrositecarousel': {
            'Meta': {'object_name': 'MicrositeCarousel'},
            'carousel_title': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'display_rows': ('django.db.models.fields.IntegerField', [], {}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.Group']", 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'include_all_sites': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'link_sites': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'linked_carousel'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['seo.SeoSite']"})
        }
    }

    complete_apps = ['myreports']