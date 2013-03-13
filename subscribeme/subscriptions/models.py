import datetime
import logging
from django.db import models
from jsonfield import JSONField

import django.contrib.auth.models as auth
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from subscriptions.fields import SerializedObjectField

log = logging.getLogger(__name__)


class FeedRecord (models.Model):
    """
    Stores information necessary for retrieving a content feed.

    The parameters necessary to construct a ``FeedReader`` are stored
    in a JSON field. Calling ``get_content`` on a ``FeedReader`` will
    will return you the content associated with this record.

    To create a ``FeedRecord`` object, use the ``factory`` method. This will
    take your parameters and serialize them for you, returning a valid
    ``FeedRecord`` object. You must specify a last_updated_calc callable,
    because each set of content may have a different way of determining when it
    was last updated.

    """

    feed_type = models.CharField(max_length=256)
    """The identifier for the content feed type registered with the library"""

    feed_params = JSONField()
    """A JSON blob representing the parameters used to retrieve the content
       feed from the library"""

    last_updated = models.DateTimeField(default=datetime.datetime.min)
    """The stored value of the last time content in the feed was updated."""

    def __unicode__(self):
        return u'a %s feed with parameters %r' % (self.feed_type, self.feed_params)

    def is_equivalent_to(self, other):
        if self.feed_type != other.feed_type:
            return False

        if self.feed_params != other.feed_params:
            return False

        return True


# Subscriber

class Subscriber (auth.User): # TODO: Should use the configured User model, not necessarily auth.User

    # subscriptions (backref)
    """The set of subscriptions for this user"""

    class Meta:
        proxy = True

    def subscribe(self, feed, library=None, commit=True):
        """Subscribe the user to a content feed."""
        if library is None:
            from feeds import FeedLibrary
            library = FeedLibrary()

        record = library.get_record(feed)
        subscription = Subscription(subscriber=self, feed_record=record)
        if commit:
            subscription.save()
        return subscription

    def subscription(self, feed, library=None):
        """Returns the subscription to the given content feed."""
        if library is None:
            from feeds import FeedLibrary
            library = FeedLibrary()

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

            other_params = record.feed_params
            for sub in subs:
                self_params = sub.feed_record.feed_params
                log.debug('Checking parameters %r against %r' %
                          (self_params, other_params))
                if self_params == other_params:
                    return sub

        except Subscription.DoesNotExist:
            return None


class Subscription (models.Model):
    subscriber = models.ForeignKey('Subscriber', related_name='subscriptions')
    feed_record = models.ForeignKey('FeedRecord')
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
