# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'ListQueryStore'
        db.create_table('subscriptions_listquerystore', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('value', self.gf('subscriptions.models.SerializedObjectField')()),
        ))
        db.send_create_signal('subscriptions', ['ListQueryStore'])

        # Deleting field 'ContentFeed.queryset'
        db.delete_column('subscriptions_contentfeed', 'queryset')

        # Adding field 'ContentFeed.querystore_type'
        db.add_column('subscriptions_contentfeed', 'querystore_type', self.gf('django.db.models.fields.related.ForeignKey')(default=0, to=orm['contenttypes.ContentType']), keep_default=False)

        # Adding field 'ContentFeed.querystore_id'
        db.add_column('subscriptions_contentfeed', 'querystore_id', self.gf('django.db.models.fields.PositiveIntegerField')(default=0), keep_default=False)

        # Changing field 'ContentFeed.last_updated_calc'
        db.alter_column('subscriptions_contentfeed', 'last_updated_calc', self.gf('subscriptions.models.SerializedObjectField')())


    def backwards(self, orm):
        
        # Deleting model 'ListQueryStore'
        db.delete_table('subscriptions_listquerystore')

        # Adding field 'ContentFeed.queryset'
        db.add_column('subscriptions_contentfeed', 'queryset', self.gf('django.db.models.fields.TextField')(default='N.'), keep_default=False)

        # Deleting field 'ContentFeed.querystore_type'
        db.delete_column('subscriptions_contentfeed', 'querystore_type_id')

        # Deleting field 'ContentFeed.querystore_id'
        db.delete_column('subscriptions_contentfeed', 'querystore_id')

        # Changing field 'ContentFeed.last_updated_calc'
        db.alter_column('subscriptions_contentfeed', 'last_updated_calc', self.gf('django.db.models.fields.TextField')())


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'subscriptions.contentfeed': {
            'Meta': {'object_name': 'ContentFeed'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(1970, 1, 1, 0, 0)'}),
            'last_updated_calc': ('subscriptions.models.SerializedObjectField', [], {}),
            'querystore_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'querystore_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"})
        },
        'subscriptions.emailchannel': {
            'Meta': {'object_name': 'EmailChannel'},
            'email': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'recipient': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True'})
        },
        'subscriptions.listquerystore': {
            'Meta': {'object_name': 'ListQueryStore'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'value': ('subscriptions.models.SerializedObjectField', [], {})
        },
        'subscriptions.rsschannel': {
            'Meta': {'object_name': 'RssChannel'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'recipient': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True'})
        },
        'subscriptions.searchsubscription': {
            'Meta': {'object_name': 'SearchSubscription', '_ormbases': ['subscriptions.Subscription']},
            'query': ('django.db.models.fields.TextField', [], {}),
            'subscription_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['subscriptions.Subscription']", 'unique': 'True', 'primary_key': 'True'})
        },
        'subscriptions.smschannel': {
            'Meta': {'object_name': 'SmsChannel'},
            'carrier': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'number': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'recipient': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True'})
        },
        'subscriptions.subscriber': {
            'Meta': {'object_name': 'Subscriber', '_ormbases': ['auth.User']},
            'user_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True', 'primary_key': 'True'})
        },
        'subscriptions.subscription': {
            'Meta': {'object_name': 'Subscription'},
            'feed': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['subscriptions.ContentFeed']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_sent': ('django.db.models.fields.DateTimeField', [], {}),
            'subscriber': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'subscriptions'", 'to': "orm['subscriptions.Subscriber']"})
        }
    }

    complete_apps = ['subscriptions']
