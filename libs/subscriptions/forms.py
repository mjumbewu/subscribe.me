from django import forms
from django.contrib import auth

import subscriptions.models as models


class UserSubscriptionForm (forms.ModelForm):

    class Meta:
        model = models.Subscription
        exclude = ('last_sent', 'subscriber')

    def __init__(self, user=None, *args, **kwargs):
        super(UserSubscriptionForm, self).__init__(*args, **kwargs)
        self.instance.subscriber = user


class FeedRecordForm (forms.ModelForm):

    class Meta:
        model = models.FeedRecord
        exclude = ('last_updated',)


class RssFeedRecordForm (forms.ModelForm):
    url = forms.URLField()

    class Meta:
        model = models.FeedRecord
        exclude = ('last_updated', 'feed_type', 'feed_params')

    def save(self, *args, **kwargs):
        self.instance.feed_type = 'rss'
        self.instance.feed_params = {'url': self.cleaned_data['url']}
        return super(RssFeedRecordForm, self).save(*args, **kwargs)
