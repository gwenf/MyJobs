# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

class Migration(DataMigration):
    def forwards(self, orm):
        """Create User Management Activities."""

        app = orm.AppAccess.objects.create(name="User Management")
        orm.Activity.objects.bulk_create([
            orm.Activity(name=args[0], description=args[1], app_access=app)
            for args in [
                ("create role", "Create new roles."),
                ("read role", "View existing roles."),
                ("update role", "Edit existing roles."),
                ("delete role", "Remove existing roles."),
                ("create user", "Create new users."),
                ("read user", "View existing users."),
                ("update user", "Edit existing users."),
                ("delete user", "Remove existing users.")]])

    def backwards(self, orm):
        """Remove User Management Activities."""

        app_access = orm.AppAccess.objects.get(name="User Management")
        orm.Activity.objects.filter(app_access=app_access).delete()
        app_access.delete()

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
        u'myjobs.activity': {
            'Meta': {'object_name': 'Activity'},
            'app_access': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['myjobs.AppAccess']"}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'})
        },
        u'myjobs.appaccess': {
            'Meta': {'object_name': 'AppAccess'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'})
        },
        u'myjobs.customhomepage': {
            'Meta': {'ordering': "(u'domain',)", 'object_name': 'CustomHomepage', '_ormbases': [u'sites.Site']},
            'logo_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'show_signup_form': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            u'site_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['sites.Site']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'myjobs.emaillog': {
            'Meta': {'object_name': 'EmailLog'},
            'category': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '254'}),
            'event': ('django.db.models.fields.CharField', [], {'max_length': '11'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'processed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'reason': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'received': ('django.db.models.fields.DateField', [], {}),
            'send_log': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'sendgrid_response'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['mysearches.SavedSearchLog']"})
        },
        u'myjobs.faq': {
            'Meta': {'object_name': 'FAQ'},
            'answer': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_visible': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'question': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'myjobs.role': {
            'Meta': {'unique_together': "(('company', 'name'),)", 'object_name': 'Role'},
            'activities': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['myjobs.Activity']", 'symmetrical': 'False'}),
            'company': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['seo.Company']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'myjobs.shared_sessions': {
            'Meta': {'object_name': 'Shared_Sessions'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'session': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['myjobs.User']", 'unique': 'True'})
        },
        u'myjobs.ticket': {
            'Meta': {'unique_together': "(['ticket', 'user'],)", 'object_name': 'Ticket'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ticket': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['myjobs.User']"})
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
            'roles': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['myjobs.Role']", 'symmetrical': 'False'}),
            'source': ('django.db.models.fields.CharField', [], {'default': "'https://secure.my.jobs'", 'max_length': '255'}),
            'timezone': ('django.db.models.fields.CharField', [], {'default': "'America/New_York'", 'max_length': '255'}),
            'user_guid': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100', 'db_index': 'True'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"})
        },
        u'mypartners.contact': {
            'Meta': {'object_name': 'Contact'},
            'approval_status': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['mypartners.Status']", 'unique': 'True', 'null': 'True'}),
            'archived_on': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '255', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'library': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['mypartners.PartnerLibrary']", 'null': 'True', 'on_delete': 'models.SET_NULL'}),
            'locations': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'contacts'", 'symmetrical': 'False', 'to': u"orm['mypartners.Location']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'notes': ('django.db.models.fields.TextField', [], {'default': "''", 'max_length': '1000', 'blank': 'True'}),
            'partner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['mypartners.Partner']", 'null': 'True', 'on_delete': 'models.SET_NULL'}),
            'phone': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '30', 'blank': 'True'}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['mypartners.Tag']", 'null': 'True', 'symmetrical': 'False'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['myjobs.User']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'})
        },
        u'mypartners.contactrecord': {
            'Meta': {'object_name': 'ContactRecord'},
            'approval_status': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['mypartners.Status']", 'unique': 'True', 'null': 'True'}),
            'archived_on': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'contact': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['mypartners.Contact']", 'null': 'True', 'on_delete': 'models.SET_NULL'}),
            'contact_email': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'contact_phone': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '30', 'blank': 'True'}),
            'contact_type': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['myjobs.User']", 'null': 'True', 'on_delete': 'models.SET_NULL'}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_time': ('django.db.models.fields.DateTimeField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'job_applications': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '6', 'blank': 'True'}),
            'job_hires': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '6', 'blank': 'True'}),
            'job_id': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '40', 'blank': 'True'}),
            'job_interviews': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '6', 'blank': 'True'}),
            'last_modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'length': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'default': "''", 'max_length': '1000', 'blank': 'True'}),
            'partner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['mypartners.Partner']", 'null': 'True', 'on_delete': 'models.SET_NULL'}),
            'subject': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['mypartners.Tag']", 'null': 'True', 'symmetrical': 'False'})
        },
        u'mypartners.location': {
            'Meta': {'object_name': 'Location'},
            'address_line_one': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'address_line_two': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'country_code': ('django.db.models.fields.CharField', [], {'default': "'USA'", 'max_length': '3'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '60', 'blank': 'True'}),
            'postal_code': ('django.db.models.fields.CharField', [], {'max_length': '12', 'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'mypartners.partner': {
            'Meta': {'object_name': 'Partner'},
            'approval_status': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['mypartners.Status']", 'unique': 'True', 'null': 'True'}),
            'archived_on': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'data_source': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'library': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['mypartners.PartnerLibrary']", 'null': 'True', 'on_delete': 'models.SET_NULL'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['seo.Company']", 'null': 'True', 'on_delete': 'models.SET_NULL'}),
            'primary_contact': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'primary_contact'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['mypartners.Contact']"}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['mypartners.Tag']", 'null': 'True', 'symmetrical': 'False'}),
            'uri': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'})
        },
        u'mypartners.partnerlibrary': {
            'Meta': {'object_name': 'PartnerLibrary'},
            'alt_phone': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'area': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'contact_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'data_source': ('django.db.models.fields.CharField', [], {'default': "'Employment Referral Resource Directory'", 'max_length': '255'}),
            'email': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'fax': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_disabled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_disabled_veteran': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_female': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_minority': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_veteran': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'phone_ext': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'region': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'st': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'street1': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'street2': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'uri': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'zip_code': ('django.db.models.fields.CharField', [], {'max_length': '12', 'blank': 'True'})
        },
        u'mypartners.status': {
            'Meta': {'object_name': 'Status'},
            'approved_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['myjobs.User']", 'null': 'True', 'on_delete': 'models.SET_NULL'}),
            'code': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '1'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'})
        },
        u'mypartners.tag': {
            'Meta': {'unique_together': "(('name', 'company'),)", 'object_name': 'Tag'},
            'company': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['seo.Company']"}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['myjobs.User']", 'null': 'True', 'on_delete': 'models.SET_NULL'}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'hex_color': ('django.db.models.fields.CharField', [], {'default': "'d4d4d4'", 'max_length': '6', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'mysearches.savedsearchlog': {
            'Meta': {'object_name': 'SavedSearchLog'},
            'backfill_jobs': ('django.db.models.fields.IntegerField', [], {}),
            'contact_record': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['mypartners.ContactRecord']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'date_sent': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'new_jobs': ('django.db.models.fields.IntegerField', [], {}),
            'reason': ('django.db.models.fields.TextField', [], {}),
            'recipient': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['myjobs.User']", 'null': 'True', 'on_delete': 'models.SET_NULL'}),
            'recipient_email': ('django.db.models.fields.EmailField', [], {'max_length': '255'}),
            'uuid': ('django.db.models.fields.CharField', [], {'max_length': '32', 'db_index': 'True'}),
            'was_received': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'was_sent': ('django.db.models.fields.BooleanField', [], {})
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
            'app_access': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['myjobs.AppAccess']", 'symmetrical': 'False', 'blank': 'True'}),
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
            'doc_type': ('django.db.models.fields.CharField', [], {'default': '\'<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">\'', 'max_length': '255'}),
            'facet_tag': ('django.db.models.fields.CharField', [], {'default': "'new-jobs'", 'max_length': '50'}),
            'fontColor': ('django.db.models.fields.CharField', [], {'default': "'666666'", 'max_length': '6'}),
            'footer': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.Group']", 'null': 'True'}),
            'header': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'home_page_template': ('django.db.models.fields.CharField', [], {'default': "'home_page/home_page_listing.html'", 'max_length': '200'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language_code': ('django.db.models.fields.CharField', [], {'default': "'en'", 'max_length': '16'}),
            'location_tag': ('django.db.models.fields.CharField', [], {'default': "'jobs'", 'max_length': '50'}),
            'meta': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'moc_helptext': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'moc_label': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'moc_placeholder': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'moc_tag': ('django.db.models.fields.CharField', [], {'default': "'vet-jobs'", 'max_length': '50'}),
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

    complete_apps = ['myjobs']
    symmetrical = True
