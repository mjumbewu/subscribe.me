from __future__ import absolute_import

from django.views import generic as views


class LandingView (views.TemplateView):
    template_name = 'landing.html'


class DashboardView (views.TemplateView):
    template_name = 'dashboard.html'
