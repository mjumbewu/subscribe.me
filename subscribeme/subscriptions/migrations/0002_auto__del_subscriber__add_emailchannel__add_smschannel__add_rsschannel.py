# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'EmailChannel'
        db.create_table('subscriptions_emailchannel', (
            ('distributionchannel_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['subscriptions.DistributionChannel'], unique=True, primary_key=True)),
            ('email', self.gf('django.db.models.fields.CharField')(max_length=256)),
        ))
        db.send_create_signal('subscriptions', ['EmailChannel'])

        # Adding model 'SmsChannel'
        db.create_table('subscriptions_smschannel', (
            ('distributionchannel_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['subscriptions.DistributionChannel'], unique=True, primary_key=True)),
            ('number', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('carrier', self.gf('django.db.models.fields.CharField')(max_length=32)),
        ))
        db.send_create_signal('subscriptions', ['SmsChannel'])

        # Adding model 'RssChannel'
        db.create_table('subscriptions_rsschannel', (
            ('distributionchannel_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['subscriptions.DistributionChannel'], unique=True, primary_key=True)),
        ))
        db.send_create_signal('subscriptions', ['RssChannel'])

        # Adding model 'DistributionChannel'
        db.create_table('subscriptions_distributionchannel', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('recipient', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True)),
        ))
        db.send_create_signal('subscriptions', ['DistributionChannel'])

        # Deleting field 'Subscription.subscriber'
        db.delete_column('subscriptions_subscription', 'subscriber_id')

        # Deleting field 'Subscription.method'
        db.delete_column('subscriptions_subscription', 'method')

        # Adding field 'Subscription.channel'
        db.add_column('subscriptions_subscription', 'channel', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['subscriptions.DistributionChannel'], null=True), keep_default=False)


    def backwards(self, orm):
        
        # Adding model 'Subscriber'
#        db.create_table('auth_user', (
#            ,
#        ))
        db.send_create_signal('subscriptions', ['Subscriber'])

        # Deleting model 'EmailChannel'
        db.delete_table('subscriptions_emailchannel')

        # Deleting model 'SmsChannel'
        db.delete_table('subscriptions_smschannel')

        # Deleting model 'RssChannel'
        db.delete_table('subscriptions_rsschannel')

        # Deleting model 'DistributionChannel'
        db.delete_table('subscriptions_distributionchannel')

        # User chose to not deal with backwards NULL issues for 'Subscription.subscriber'
        raise RuntimeError("Cannot reverse this migration. 'Subscription.subscriber' and its values cannot be restored.")

        # Adding field 'Subscription.method'
        db.add_column('subscriptions_subscription', 'method', self.gf('django.db.models.fields.CharField')(default='email', max_length=5), keep_default=False)

        # Deleting field 'Subscription.channel'
        db.delete_column('subscriptions_subscription', 'channel_id')


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
