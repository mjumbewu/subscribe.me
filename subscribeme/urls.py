from __future__ import absolute_import

from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
admin.autodiscover()

import main.views

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),

    url(r'^$',
        main.views.LandingView.as_view(),
        name='main_landing'),

    url(r'^dashboard$',
        main.views.DashboardView.as_view(),
        name='main_dashboard'),
)
