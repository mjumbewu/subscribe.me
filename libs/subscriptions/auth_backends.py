from django.contrib.auth.backends import ModelBackend
from .models import Subscriber

class SubscriberBackend(ModelBackend):
    def get_user(self, user_id):
        try:
            return Subscriber.objects.get(pk=user_id)
        except Subscriber.DoesNotExist:
            return None
