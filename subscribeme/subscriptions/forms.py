import django.forms
from django.contrib import auth

import subscriptions.models as models


class SubscriptionForm (django.forms.ModelForm):

    # TODO: This form currently takes the feed_record ID, which means that the
    # feed record has to be created before the form is served/processed.  This
    # is an artifact of the old way that we were doing things, where this was
    # thought a necessity.  Now, with the simpler content feeds system, we can
    # update this form to take in a feed name and feed parameters, and create
    # the feed record before creating the subscription.  This will save on
    # unused, lingering database records that would have to get cleaned up by
    # a cron job.
    #
    # So, change this form to use feed name/params and to use a two-step save
    # process.

    class Meta:
        model = models.Subscription
        exclude = ('last_sent',)
        widgets = {
            'feed_record' : django.forms.HiddenInput(),
            'subscriber' : django.forms.HiddenInput(),
        }
