from django.views import generic as views


# Project-wide Views

class LandingView (views.TemplateView):
    template_name = 'landing.html'
