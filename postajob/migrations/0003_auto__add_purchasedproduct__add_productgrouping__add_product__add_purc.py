# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'PurchasedProduct'
        db.create_table(u'postajob_purchasedproduct', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('product', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['postajob.Product'])),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['mydashboard.Company'])),
            ('purchase_date', self.gf('django.db.models.fields.DateField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'postajob', ['PurchasedProduct'])

        # Adding model 'ProductGrouping'
        db.create_table(u'postajob_productgrouping', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('score', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('grouping_name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal(u'postajob', ['ProductGrouping'])

        # Adding M2M table for field products on 'ProductGrouping'
        db.create_table(u'postajob_productgrouping_products', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('productgrouping', models.ForeignKey(orm[u'postajob.productgrouping'], null=False)),
            ('product', models.ForeignKey(orm[u'postajob.product'], null=False))
        ))
        db.create_unique(u'postajob_productgrouping_products', ['productgrouping_id', 'product_id'])

        # Adding model 'Product'
        db.create_table(u'postajob_product', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('site_package', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['postajob.SitePackage'], null=True)),
            ('cost', self.gf('django.db.models.fields.DecimalField')(max_digits=20, decimal_places=2)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['mydashboard.Company'])),
            ('posting_window_length', self.gf('django.db.models.fields.IntegerField')(default=30)),
            ('max_job_length', self.gf('django.db.models.fields.IntegerField')(default=30)),
            ('num_jobs_allowed', self.gf('django.db.models.fields.IntegerField')(default=5)),
        ))
        db.send_create_signal(u'postajob', ['Product'])

        # Adding model 'PurchasedJob'
        db.create_table(u'postajob_purchasedjob', (
            (u'job_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['postajob.Job'], unique=True, primary_key=True)),
            ('max_expired_date', self.gf('django.db.models.fields.DateField')()),
            ('purchased_product', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['postajob.PurchasedProduct'])),
            ('is_approved', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'postajob', ['PurchasedJob'])


    def backwards(self, orm):
        # Deleting model 'PurchasedProduct'
        db.delete_table(u'postajob_purchasedproduct')

        # Deleting model 'ProductGrouping'
        db.delete_table(u'postajob_productgrouping')

        # Removing M2M table for field products on 'ProductGrouping'
        db.delete_table('postajob_productgrouping_products')

        # Deleting model 'Product'
        db.delete_table(u'postajob_product')

        # Deleting model 'PurchasedJob'
        db.delete_table(u'postajob_purchasedjob')


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
        u'mydashboard.businessunit': {
            'Meta': {'object_name': 'BusinessUnit', 'db_table': "'seo_businessunit'"},
            'id': ('django.db.models.fields.IntegerField', [], {'max_length': '10', 'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '500', 'null': 'True', 'blank': 'True'})
        },
        u'mydashboard.company': {
            'Meta': {'object_name': 'Company', 'db_table': "'seo_company'"},
            'admins': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['myjobs.User']", 'through': u"orm['mydashboard.CompanyUser']", 'symmetrical': 'False'}),
            'id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'job_source_ids': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['mydashboard.BusinessUnit']", 'symmetrical': 'False'}),
            'member': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'}),
            'site_package': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['postajob.SitePackage']", 'null': 'True', 'on_delete': 'models.SET_NULL'})
        },
        u'mydashboard.companyuser': {
            'Meta': {'unique_together': "(('user', 'company'),)", 'object_name': 'CompanyUser'},
            'company': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['mydashboard.Company']"}),
            'date_added': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['myjobs.User']"})
        },
        u'mydashboard.seosite': {
            'Meta': {'ordering': "('domain',)", 'object_name': 'SeoSite', 'db_table': "'seo_seosite'", '_ormbases': [u'sites.Site']},
            'business_units': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['mydashboard.BusinessUnit']", 'null': 'True', 'blank': 'True'}),
            'site_package': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['postajob.SitePackage']", 'null': 'True', 'on_delete': 'models.SET_NULL'}),
            u'site_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['sites.Site']", 'unique': 'True', 'primary_key': 'True'}),
            'site_title': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200', 'blank': 'True'}),
            'view_sources': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['mydashboard.ViewSource']", 'null': 'True', 'blank': 'True'})
        },
        u'mydashboard.viewsource': {
            'Meta': {'object_name': 'ViewSource', 'db_table': "'seo_viewsource'"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200'}),
            'view_source': ('django.db.models.fields.IntegerField', [], {'default': "''", 'max_length': '20'})
        },
        u'myjobs.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'unique': 'True', 'max_length': '255', 'db_index': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'gravatar': ('django.db.models.fields.EmailField', [], {'db_index': 'True', 'max_length': '255', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_disabled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
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
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'postajob.job': {
            'Meta': {'object_name': 'Job'},
            'apply_info': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'apply_link': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'autorenew': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'company': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['mydashboard.Company']"}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'country_short': ('django.db.models.fields.CharField', [], {'max_length': '3'}),
            'date_expired': ('django.db.models.fields.DateField', [], {}),
            'date_new': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'date_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'guid': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'unique': 'True', 'primary_key': 'True'}),
            'is_expired': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_syndicated': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'reqid': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'site_packages': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['postajob.SitePackage']", 'null': 'True', 'symmetrical': 'False'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'state_short': ('django.db.models.fields.CharField', [], {'max_length': '3'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'zipcode': ('django.db.models.fields.CharField', [], {'max_length': '15', 'blank': 'True'})
        },
        u'postajob.product': {
            'Meta': {'object_name': 'Product'},
            'cost': ('django.db.models.fields.DecimalField', [], {'max_digits': '20', 'decimal_places': '2'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max_job_length': ('django.db.models.fields.IntegerField', [], {'default': '30'}),
            'num_jobs_allowed': ('django.db.models.fields.IntegerField', [], {'default': '5'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['mydashboard.Company']"}),
            'posting_window_length': ('django.db.models.fields.IntegerField', [], {'default': '30'}),
            'site_package': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['postajob.SitePackage']", 'null': 'True'})
        },
        u'postajob.productgrouping': {
            'Meta': {'object_name': 'ProductGrouping'},
            'grouping_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'products': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['postajob.Product']", 'null': 'True', 'symmetrical': 'False'}),
            'score': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'postajob.purchasedjob': {
            'Meta': {'object_name': 'PurchasedJob', '_ormbases': [u'postajob.Job']},
            'is_approved': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'job_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['postajob.Job']", 'unique': 'True', 'primary_key': 'True'}),
            'max_expired_date': ('django.db.models.fields.DateField', [], {}),
            'purchased_product': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['postajob.PurchasedProduct']"})
        },
        u'postajob.purchasedproduct': {
            'Meta': {'object_name': 'PurchasedProduct'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['mydashboard.Company']"}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['postajob.Product']"}),
            'purchase_date': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        u'postajob.sitepackage': {
            'Meta': {'object_name': 'SitePackage'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'sites': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['mydashboard.SeoSite']", 'null': 'True', 'symmetrical': 'False'})
        },
        u'sites.site': {
            'Meta': {'ordering': "('domain',)", 'object_name': 'Site', 'db_table': "'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['postajob']