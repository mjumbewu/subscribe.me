import logging as log

from django.views import generic as views
from django import http
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response

import subscriptions.feeds as feeds
import subscriptions.forms as forms
import subscriptions.models as models

class SingleSubscriptionMixin (object):
    def get_content_feed_library(self):
        """Return a ContentFeedLibrary to be used for the subscriptions"""
        return feeds.ContentFeedLibrary()

    def get_content_feed(self):
        """A factory for the ContentFeed object that describes this content feed"""
        raise NotImplementedError()

    def get_subscription(self, feed):
        if self.request.user and self.request.user.is_authenticated():
            try:
                subscriber = self.request.user.subscriber

            # If the user doesn't have a subscriber attribute, then they must
            # not be subscribed.
            except models.Subscriber.DoesNotExist:
                return None

            library = self.get_content_feed_library()
            return subscriber.subscription(feed, library)

        return None

    def get_subscription_form(self, feed):
        if self.request.user and self.request.user.is_authenticated():
            try:
                subscriber = self.request.user.subscriber

            except models.Subscriber.DoesNotExist:
                return None

            subscription = self.get_subscription(feed)

            if subscription is None:
                library = self.get_content_feed_library()
                form = forms.SubscriptionForm(
                    {'feed_record': library.get_record(feed).pk,
                     'subscriber': subscriber.pk})
                return form

        return None

    def get_context_data(self, **kwargs):
        context_data = super(SingleSubscriptionMixin, self).get_context_data(**kwargs)

        feed = self.get_content_feed()
        subscription = self.get_subscription(feed)
        subscription_form = self.get_subscription_form(feed)
        is_subscribed = (subscription is not None)

        context_data.update({'feed': feed,
                             'subscription': subscription,
                             'subscription_form': subscription_form,
                             'is_subscribed': is_subscribed})
        return context_data


class CreateSubscriptionView (views.CreateView):
    model = models.Subscription

    def get_success_url(self):
        return self.request.REQUEST['success']


class DeleteSubscriptionView (views.DeleteView):
    model = models.Subscription

    def get_success_url(self):
        return self.request.REQUEST['success']


def subscribe(request):
    subscriber = request.user.subscriber
    feed = ContentFeed.object.get(request.REQUEST['feed'])
    redirect_to = request.REQUEST['next']

    subscriber.subscribe(feed)
    return HttpResponseRedirect(redirect_to)


#    def get_subscription_form(self):
#        pass
#
#    def __call__(self, request):
#        if request.method == 'POST':
#
#            subs_form = self.get_subscription_form()
#        else:
#            return super(SubscribeToSearchView, self).__call__(request)
