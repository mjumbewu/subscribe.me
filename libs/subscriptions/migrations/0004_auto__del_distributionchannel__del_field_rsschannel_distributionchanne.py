# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting model 'DistributionChannel'
        db.delete_table('subscriptions_distributionchannel')

        # Renaming field 'RssChannel.distributionchannel_ptr' as 'RssChannel.id'
        db.rename_column('subscriptions_rsschannel', 'distributionchannel_ptr_id', 'id')

        # Adding field 'RssChannel.recipient'
        db.add_column('subscriptions_rsschannel', 'recipient', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True), keep_default=False)

        # Renaming field 'EmailChannel.distributionchannel_ptr' as 'EmailChannel.id'
        db.rename_column('subscriptions_emailchannel', 'distributionchannel_ptr_id', 'id')

        # Adding field 'EmailChannel.recipient'
        db.add_column('subscriptions_emailchannel', 'recipient', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True), keep_default=False)

        # Deleting field 'SmsChannel.distributionchannel_ptr' as 'SmsChannel.id'
        db.rename_column('subscriptions_smschannel', 'distributionchannel_ptr_id', 'id')

        # Adding field 'SmsChannel.recipient'
        db.add_column('subscriptions_smschannel', 'recipient', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True), keep_default=False)

        # Changing field 'Subscription.channel'
        db.alter_column('subscriptions_subscription', 'channel_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['subscriptions.EmailChannel'], null=True))


    def backwards(self, orm):
        
        # Adding model 'DistributionChannel'
        db.create_table('subscriptions_distributionchannel', (
            ('recipient', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('subscriptions', ['DistributionChannel'])

        # Adding field 'RssChannel.distributionchannel_ptr'
        db.add_column('subscriptions_rsschannel', 'distributionchannel_ptr', self.gf('django.db.models.fields.related.OneToOneField')(default=0, to=orm['subscriptions.DistributionChannel'], unique=True, primary_key=True), keep_default=False)

        # Deleting field 'RssChannel.id'
        db.delete_column('subscriptions_rsschannel', 'id')

        # Deleting field 'RssChannel.recipient'
        db.delete_column('subscriptions_rsschannel', 'recipient_id')

        # Adding field 'EmailChannel.distributionchannel_ptr'
        db.add_column('subscriptions_emailchannel', 'distributionchannel_ptr', self.gf('django.db.models.fields.related.OneToOneField')(default=0, to=orm['subscriptions.DistributionChannel'], unique=True, primary_key=True), keep_default=False)

        # Deleting field 'EmailChannel.id'
        db.delete_column('subscriptions_emailchannel', 'id')

        # Deleting field 'EmailChannel.recipient'
        db.delete_column('subscriptions_emailchannel', 'recipient_id')

        # Adding field 'SmsChannel.distributionchannel_ptr'
        db.add_column('subscriptions_smschannel', 'distributionchannel_ptr', self.gf('django.db.models.fields.related.OneToOneField')(default=0, to=orm['subscriptions.DistributionChannel'], unique=True, primary_key=True), keep_default=False)

        # Deleting field 'SmsChannel.id'
        db.delete_column('subscriptions_smschannel', 'id')

        # Deleting field 'SmsChannel.recipient'
        db.delete_column('subscriptions_smschannel', 'recipient_id')

        # Changing field 'Subscription.channel'
        db.alter_column('subscriptions_subscription', 'channel_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['subscriptions.DistributionChannel'], null=True))


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
        'subscriptions.emailchannel': {
            'Meta': {'object_name': 'EmailChannel'},
            'email': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'recipient': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True'})
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
        'subscriptions.subscription': {
            'Meta': {'object_name': 'Subscription'},
            'channel': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['subscriptions.EmailChannel']", 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_sent': ('django.db.models.fields.DateTimeField', [], {})
        }
    }

    complete_apps = ['subscriptions']
