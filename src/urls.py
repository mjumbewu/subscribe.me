from __future__ import absolute_import

from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
from django.contrib.auth import urls as auth_urls

import subscriptions.urls
from subscribeme import LandingView

admin.autodiscover()


urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),

    url(r'^$',
        LandingView.as_view(),
        name='main_landing'),

    url(r'^subscriptions/',
        include(subscriptions.urls)),

    url(r'^accounts/logout/$',
        'django.contrib.auth.views.logout',
        {'next_page': '/'}, name='logout'),
    url(r'^accounts/',
        include(auth_urls)),
)
