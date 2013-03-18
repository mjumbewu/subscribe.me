import logging as log

from django.views import generic as views
from django import http
from django.contrib.auth.decorators import user_passes_test, login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.utils.decorators import method_decorator

import subscriptions.feeds as feeds
import subscriptions.forms as forms
import subscriptions.models as models

class SingleSubscriptionMixin (object):
    def get_content_feed_library(self):
        """Return a FeedLibrary to be used for the subscriptions"""
        return feeds.FeedLibrary()

    def get_content_feed(self):
        """A factory for the FeedRecord object that describes this content feed"""
        raise NotImplementedError()

    def get_subscription(self, feed):
        if self.request.user and self.request.user.is_authenticated():
            try:
                subscriber = self.request.user

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
                subscriber = self.request.user

            except models.Subscriber.DoesNotExist:
                return None

            subscription = self.get_subscription(feed)

            if subscription is None:
                library = self.get_content_feed_library()
                form = forms.UserSubscriptionForm(
                    initial={'feed_record': library.get_record(feed).pk},
                    user=subscriber)
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


def subscribe(request):
    subscriber = request.user.subscriber
    feed_record = FeedRecord.object.get(request.REQUEST['feed'])
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


# View Mixins

class LoginRequiredMixin (object):
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(request, *args, **kwargs)


class SubscriberAccessibleMixin (object):
    def get_subscription(self):
        return super(SubscriberAccessibleMixin, self).get_object()

    def user_can_access(self, user):
        self.subscription = self.get_subscription()
        return user.is_superuser or (self.subscription.subscriber == user)

    def dispatch(self, request, *args, **kwargs):
        user_is_subscriber = user_passes_test(self.user_can_access)
        view_func = user_is_subscriber(super(SubscriberAccessibleMixin, self).dispatch)
        return view_func(request, *args, **kwargs)


# Subscription Views

class SubscriptionListView (LoginRequiredMixin, views.ListView):
    model = models.Subscription

    def get_queryset(self):
        queryset = super(SubscriptionListView, self).get_queryset()
        return queryset.filter(subscriber=self.request.user)


class CreateSubscriptionView (LoginRequiredMixin, views.CreateView):
    model = models.Subscription
    form_class = forms.UserSubscriptionForm

    def get_success_url(self):
        return reverse('subscription_detail', args=[self.object.pk])

    def get_form_kwargs(self):
        kwargs = super(CreateSubscriptionView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class SubscriptionDetailView (SubscriberAccessibleMixin, views.DetailView):
    model = models.Subscription


class DeleteSubscriptionView (SubscriberAccessibleMixin, views.DeleteView):
    model = models.Subscription

    def get_success_url(self):
        return reverse('subscription_list')


# Feed Record Views

class FeedRecordDetailView (views.DetailView):
    model = models.FeedRecord


class CreateFeedRecordView (views.CreateView):
    model = models.FeedRecord
    form_class = forms.FeedRecordForm

    def get_success_url(self):
        return reverse('feedrecord_detail', args=[self.object.pk])


class CreateRssFeedRecordView (views.CreateView):
    model = models.FeedRecord
    form_class = forms.RssFeedRecordForm

    def get_success_url(self):
        return reverse('feedrecord_detail', args=[self.object.pk])


class DeleteFeedRecordView (views.DeleteView):
    model = models.FeedRecord

    def get_success_url(self):
        return self.request.REQUEST['success']
