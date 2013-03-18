from django.views import generic as views
from django.contrib.auth.decorators import user_passes_test, login_required
from django.core.urlresolvers import reverse
from django.utils.decorators import method_decorator
import subscriptions.feeds as feeds
import subscriptions.forms as forms
import subscriptions.models as models


# Project-wide Views

class LandingView (views.TemplateView):
    template_name = 'landing.html'
