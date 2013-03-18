from django.conf.urls.defaults import patterns, include, url
#import subscriptions.api.urls
from subscriptions.views import (
    SubscriptionListView, SubscriptionDetailView, CreateSubscriptionView, DeleteSubscriptionView,
    CreateFeedRecordView, FeedRecordDetailView,
    CreateRssFeedRecordView)

urlpatterns = patterns('',
#    url('^api/', include(subscriptions.api.urls)),

    url('^$', SubscriptionListView.as_view(), name='subscription_list'),
    url('^create$', CreateSubscriptionView.as_view(), name='create_subscription'),
    url('^(?P<pk>[^/]+)/$', SubscriptionDetailView.as_view(), name='subscription_detail'),
    url('^(?P<pk>[^/]+)/delete$', DeleteSubscriptionView.as_view(), name='delete_subscription'),

    url('^feeds/create$', CreateFeedRecordView.as_view(), name='create_feedrecord'),
    url('^feeds/create_rss$', CreateRssFeedRecordView.as_view(), name='create_rss_feedrecord'),
    url('^feeds/(?P<pk>[^/]+)/$', FeedRecordDetailView.as_view(), name='feedrecord_detail'),
)
