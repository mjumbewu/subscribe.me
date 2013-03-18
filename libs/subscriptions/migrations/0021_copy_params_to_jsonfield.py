# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

class Migration(DataMigration):

    def forwards(self, orm):
        "Write your forwards methods here."
        # Note: Remember to use orm['appname.ModelName'] rather than "from appname.models..."
        ContentFeedRecord = orm['subscriptions.ContentFeedRecord']

        for record in ContentFeedRecord.objects.all():
            old_params = record.feed_params_old.values('name', 'value')
            record.feed_params = dict([
                (param['name'], param['value'])
                for param in old_params
            ])
            record.save()

    def backwards(self, orm):
        "Write your backwards methods here."
        ContentFeedRecord = orm['subscriptions.ContentFeedRecord']

        for record in ContentFeedRecord.objects.all():
            for name, value in record.feed_params.items():
                record.feed_params_old.create(name=name, value=value)

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
        'subscriptions.contentfeedparameter': {
            'Meta': {'object_name': 'ContentFeedParameter'},
            'feed_record': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'feed_params_old'", 'to': "orm['subscriptions.ContentFeedRecord']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'value': ('django.db.models.fields.TextField', [], {})
        },
        'subscriptions.contentfeedrecord': {
            'Meta': {'object_name': 'ContentFeedRecord'},
            'feed_name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'feed_params': ('jsonfield.fields.JSONField', [], {'default': '{}'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(1, 1, 1, 0, 0)'})
        },
        'subscriptions.subscriber': {
            'Meta': {'object_name': 'Subscriber', '_ormbases': ['auth.User']},
            'user_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True', 'primary_key': 'True'})
        },
        'subscriptions.subscription': {
            'Meta': {'object_name': 'Subscription'},
            'feed_record': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['subscriptions.ContentFeedRecord']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_sent': ('django.db.models.fields.DateTimeField', [], {'blank': 'True'}),
            'subscriber': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'subscriptions'", 'to': "orm['subscriptions.Subscriber']"})
        },
        'subscriptions.subscriptiondispatchrecord': {
            'Meta': {'object_name': 'SubscriptionDispatchRecord'},
            'content': ('django.db.models.fields.TextField', [], {}),
            'dispatcher': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'subscription': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'dispatches'", 'to': "orm['subscriptions.Subscription']"}),
            'when': ('django.db.models.fields.DateTimeField', [], {})
        }
    }

    complete_apps = ['subscriptions']
    symmetrical = True
