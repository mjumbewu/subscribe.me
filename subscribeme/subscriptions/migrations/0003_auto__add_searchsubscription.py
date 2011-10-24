# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'SearchSubscription'
        db.create_table('subscriptions_searchsubscription', (
            ('subscription_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['subscriptions.Subscription'], unique=True, primary_key=True)),
            ('query', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('subscriptions', ['SearchSubscription'])


    def backwards(self, orm):
        
        # Deleting model 'SearchSubscription'
        db.delete_table('subscriptions_searchsubscription')


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
        'subscriptions.distributionchannel': {
            'Meta': {'object_name': 'DistributionChannel'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'recipient': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True'})
        },
        'subscriptions.emailchannel': {
            'Meta': {'object_name': 'EmailChannel', '_ormbases': ['subscriptions.DistributionChannel']},
            'distributionchannel_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['subscriptions.DistributionChannel']", 'unique': 'True', 'primary_key': 'True'}),
            'email': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        'subscriptions.rsschannel': {
            'Meta': {'object_name': 'RssChannel', '_ormbases': ['subscriptions.DistributionChannel']},
            'distributionchannel_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['subscriptions.DistributionChannel']", 'unique': 'True', 'primary_key': 'True'})
        },
        'subscriptions.searchsubscription': {
            'Meta': {'object_name': 'SearchSubscription', '_ormbases': ['subscriptions.Subscription']},
            'query': ('django.db.models.fields.TextField', [], {}),
            'subscription_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['subscriptions.Subscription']", 'unique': 'True', 'primary_key': 'True'})
        },
        'subscriptions.smschannel': {
            'Meta': {'object_name': 'SmsChannel', '_ormbases': ['subscriptions.DistributionChannel']},
            'carrier': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'distributionchannel_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['subscriptions.DistributionChannel']", 'unique': 'True', 'primary_key': 'True'}),
            'number': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        },
        'subscriptions.subscription': {
            'Meta': {'object_name': 'Subscription'},
            'channel': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['subscriptions.DistributionChannel']", 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_sent': ('django.db.models.fields.DateTimeField', [], {})
        }
    }

    complete_apps = ['subscriptions']
