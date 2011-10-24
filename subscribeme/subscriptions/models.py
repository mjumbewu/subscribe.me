import datetime
import logging
from django.db import models

import django.contrib.auth.models as auth
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from subscriptions.fields import SerializedObjectField

log = logging.getLogger(__name__)


class ContentFeedRecord (models.Model):
    """
    Stores information necessary for retrieving a content feed.

    The query for the ``ContentFeed`` is stored as a pickled iterable object.
    Don't judge me!!! Calling ``get_content`` on a ``ContentFeed`` will return
    you the results of the query. Calling ``get_last_updated`` will return you
    the last time the given set of content was updated.

    To create a ``ContentFeedRecord`` object, use the ``factory`` method. This will
    take your parameters and serialize them for you, returning a valid
    ``ContentFeedRecord`` object. You must specify a last_updated_calc callable,
    because each set of content may have a different way of determining when it
    was last updated.

    """

    feed_name = models.CharField(max_length=256)
    """The identifier for the content feed type registered with the library"""

    # feed_params (backref)
    """The set of parameters used to retrieve the content feed from the
       library"""

    last_updated = models.DateTimeField(default=datetime.datetime.min)
    """The stored value of the last time content in the feed was updated."""

    def __unicode__(self):
        return u'a %s feed' % (self.feed_name,)

    def is_equivalent_to(self, other):
        if self.feed_name != other.feed_name:
            return False

        other_params = other.feed_params.all().values('name', 'value')
        for self_param in self.feed_params.all().values('name', 'value'):
            if self_param not in other_params:
                return False
        return True


class ContentFeedParameter (models.Model):
    """One of the parameters used to retrieve the content feed from the
       library"""

    feed_record = models.ForeignKey(ContentFeedRecord, related_name='feed_params')
    name = models.CharField(max_length=256)
    value = models.TextField()


# Subscriber

class Subscriber (auth.User):

    # subscriptions (backref)
    """The set of subscriptions for this user"""

    def subscribe(self, feed, library=None, commit=True):
        """Subscribe the user to a content feed."""
        if library is None:
            from feeds import ContentFeedLibrary
            library = ContentFeedLibrary()

        record = library.get_record(feed)
        subscription = Subscription(subscriber=self, feed_record=record)
        if commit:
            subscription.save()
        return subscription

    def subscription(self, feed, library=None):
        """Returns the subscription to the given content feed."""
        if library is None:
            from feeds import ContentFeedLibrary
            library = ContentFeedLibrary()

        log.debug('Checking whether %s is subscribed to %s at %s' %
                  (self, feed, library))

        record = library.get_record(feed)
        try:
            subs = self.subscriptions.select_related() \
                .filter(feed_record__feed_name=record.feed_name)

            if not subs:
                log.debug('No subscription record found with the name %s' %
                          (record.feed_name,))
                return None

            other_params = list(record.feed_params.values('name', 'value'))
            for sub in subs:
                self_params = list(sub.feed_record.feed_params.values('name', 'value'))
                log.debug('Checking parameters %r against %r' %
                          (self_params, other_params))
                if self_params == other_params:
                    return sub

        except Subscription.DoesNotExist:
            return None


from django.dispatch import receiver
from django.db.models.signals import post_save
@receiver(post_save, sender=auth.User)
def create_subscriber_for_user(sender, **kwargs):
    """
    Create a Subscriber object whenever a user is created.  This is useful so
    that we don't have to patch whatever different registration processes we
    end up using.
    """
    user = kwargs.get('instance')
    created = kwargs.get('created')
    raw = kwargs.get('raw')

    logging.debug('user is %r' % user)

    if created and not raw:
        if not hasattr(user, 'subscriber') or user.subscriber is None:
            user.subscriber = Subscriber()
            user.subscriber.save()
            logging.debug('created subscriber')


class Subscription (models.Model):
    subscriber = models.ForeignKey('Subscriber', related_name='subscriptions')
    feed_record = models.ForeignKey('ContentFeedRecord')
    last_sent = models.DateTimeField(blank=True)

    def __unicode__(self):
        return u"%s's subscription to %s" % (self.subscriber, self.feed_record)

    def save(self, *args, **kwargs):
        """
        Sets the last_sent datetime to the current time when instance is new.
        Doesn't change the last_sent datetime on instance if it's already
        saved.

        """
        # We could use Django's built-in ability to make this an auto_now_add
        # field, but then we couldn't change the value when we want.
        if not self.id:
            self.last_sent = datetime.datetime.now()
        super(Subscription, self).save(*args, **kwargs)


class SubscriptionDispatchRecord (models.Model):
    """Records a subscription delivery"""

    subscription = models.ForeignKey('Subscription', related_name='dispatches')
    when = models.DateTimeField()
    content = models.TextField()
    dispatcher = models.CharField(max_length=256)
