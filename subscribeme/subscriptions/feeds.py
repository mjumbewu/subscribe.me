import json
import smtplib

from collections import defaultdict
from datetime import date, datetime
from email.mime.text import MIMEText
from logging import getLogger

from django.contrib.sites.models import Site
from django.db.models.manager import Manager
from django.template import Context
from django.template.loader import get_template
from django.utils.encoding import smart_str, smart_unicode

from models import ContentFeedRecord
from models import ContentFeedParameter
from models import Subscription
from models import SubscriptionDispatchRecord

log = getLogger(__name__)


def import_all_feeds():
    """
    Import the feeds module from all the installed apps. The assumption is that
    apps will register their feed classes in that module. If not, they're SOL.
    """
    import settings
    for app in settings.INSTALLED_APPS:
        feeds_mod = '.'.join([app, 'feeds'])
        try:
            __import__(feeds_mod)
        except ImportError:
            pass


class ContentFeed (object):
    def get_content(self):
        """
        Returns the content items that appear in this feed.
        """
        raise NotImplementedError()

    def all(self):
        return self.get_content()

    def get_params(self):
        """
        Return a dictionary of keyword arguments that can be used to construct
        a feed identical to this one.  The values in the dictionary should be
        strings only.
        """
        raise NotImplementedError()

    def get_updated_since(self, previous):
        """
        Return the content items that have been updated since the given time.
        """
        raise NotImplementedError()

    def get_changes_to(self, item):
        """
        Returns a dictionary representing the changes to the item.  The nature
        of this dictionary may vary depending on the item type.
        """
        raise NotImplementedError()

    def get_last_updated_time(self):
        """
        Return the latest time that any content in the feed was updated.
        """
        raise NotImplementedError()

    class NotFound (Exception):
        pass


class ContentFeedLibrary (object):

    feeds = {}
    """Map of { feed_name : ContentFeedClass }"""

    _reverse = {}
    """Map of { ContentFeedClass : feed_name }. For reverse-lookup"""

    _feed_cache = {}
    _record_cache = {}

    def __init__(self, shared=True):
        if not shared:
            self.feeds = {}
            self._reverse = {}
            self._feed_cache = {}
            self._record_cache = {}

    def register(self, ContentFeedClass, name):
        """Add the given manager class to the registry by the given name."""
        self.feeds[name] = ContentFeedClass
        self._reverse[ContentFeedClass] = name

    def _cache(self, feed, record):
        self._feed_cache[record] = feed
        self._record_cache[feed] = record

    def get_feed(self, record):
        """Retrieve a feed based on the given record."""

        if record in self._feed_cache:
            return self._feed_cache[record]

        ContentFeedClass = self.feeds[record.feed_name]
        kwargs = record.feed_params
        feed = ContentFeedClass(**kwargs)

        self._cache(feed, record)

        log.debug('The record %r represents the feed %r' % (record, feed))

        return feed

    def get_record(self, feed):
        """Retrieve a record describing the given feed."""

        if feed in self._record_cache:
            return self._record_cache[feed]

        ContentFeedClass = feed.__class__
        try:
            name = self._reverse[ContentFeedClass]
        except KeyError:
            log.debug('%s is not registered in the library: %s' %
                (feed.__class__.__name__, self.feeds))
            raise ContentFeedClass.NotFound(
                '%s is not registered in the library' %
                (feed.__class__.__name__,))

        record = ContentFeedRecord()
        record.feed_name = name
        record.feed_params = feed.get_params()
        record.save()

        self._cache(feed, record)

        return record


class ContentFeedRecordUpdater (object):
    """Responsible for updating the metadata in a content feed"""

    def update(self, record, library=None):
        """
        Changes the last_updated of a legfiles feed to most recent intro date.

        Iterate through each item (page) in the feed (book) and check when it
        was last updated.  Be careful and don't use this as a matter of normal
        course; it may be slow.
        """
        if library is None:
            library = ContentFeedLibrary()

        feed = library.get_feed(record)

        all_content = feed.get_content()
        latest = None
        if all_content:
            latest = max(feed.get_last_updated(item) for item in all_content)

        if latest is None:
            latest = datetime.min

        record.last_updated = latest
        record.save()

    def update_all(self, records, library=None):
        """Updates all the feeds in a collection (yes, it's just a for loop)"""
        for record in records:
            self.update(record, library)


class ContentFeedRecordCleaner (object):
    """Responsible for identifying and removing all unused feeds"""

    def clean(self, library=None):
        """
        Removes all content feeds that are not subscribed to by some
        subscription.

        """
        used_record_ids = Subscription.objects.values('feed_record__id').distinct()
        ContentFeedRecord.objects.exclude(id__in=used_record_ids).delete()


class SubscriptionDispatcher (object):
    """
    The ``SubscriptionDispatcher`` gets new feed content from the library for
    you. You could go and get the feeds yourself, but the dispatcher will just
    go and grab anything new each day.

    The dispatcher will actually not deliver the content to you from one feed at
    a time. Instead it will take into account all the feeds that you're
    subscribed to and coallate the content. When the dispatcher gets the same
    content from two different managers, it'll make sure to deliver that content
    only once.
    """

    template_name = None
    """The file name of the template used to render the dispatch delivery
       "message"."""

    feed_updated_times = {}
    """A variable (essentialy global) mapping feeds to the last time that they
       were updated. Used as a cache."""

    def get_content_updates_for(self, subscriptions, library):
        """
        Check the library for the manager of each subscription feed. Check the
        managers for content that has been updated.

        Return a map of {piece_of_content: updates_as_dict} containing each
        piece of updated content and its updates as a dictionary.
        """
        log.debug('Checking for updates to %s in %s' % (subscriptions, library))

        content_changes = defaultdict(dict)

        for subscription in subscriptions:
            feed = library.get_feed(subscription.feed_record)

            # Check whether the feed has been updated since the subscription
            # was last sent (this assumes that the feed_record has been
            # updated to accurately represent the feed).
            if subscription.last_sent < subscription.feed_record.last_updated:
                new_contents = feed.get_updates_since(subscription.last_sent)

                for item in new_contents:
                    changes = feed.get_changes_to(item, subscription.last_sent)
                    content_changes[item].update(changes)

        log.debug('What changed: %s' % (content_changes,))

        return content_changes

    def render(self, subscriber, subscriptions, content_updates):
        """
        Render the given content updates to a template for the subscriber.
        """
        template = get_template(self.template_name)

        # I was having some trouble iterating over content_items as a dict
        # in the templates, so I'll just convert content updates to lists of
        # tuples.
        content_updates = content_updates.items()
        content_updates = [(k, v.items()) for (k, v) in content_updates]

        context = Context({'subscriber':subscriber,
                           'subscriptions': subscriptions,
                           'content_updates':content_updates,
                           'SITE': Site.objects.get_current()})
        return template.render(context)

    def deliver_to(self, subscriber, delivery_text):
        """
        Send the delivery_text to the subscriber by whatever method is
        appropriate for the dispatcher
        """
        raise NotImplementedError()

    def update_subscriptions(self, subscriptions):
        """
        Update the last_sent property of the subscriptions to the values found
        in feed_updated_times dictionary.  These times should have been cached
        during the get_content_updates_for step.
        """
        log.debug('Updating the subscriptions in %s' % (subscriptions))

        for subscription in subscriptions:
            if subscription.last_sent != subscription.feed_record.last_updated:
                subscription.last_sent = subscription.feed_record.last_updated
                subscription.save()

    def dispatch_subscriptions_for(self, subscriber, library=None):
        log.debug('Dispatching subscriptions for %s' % (subscriber))

        if library is None:
            library = ContentFeedLibrary()

        subscriptions = subscriber.subscriptions.all()

        content_updates = self.get_content_updates_for(subscriptions, library)
        delivery = self.render(subscriber, subscriptions, content_updates)
        self.deliver_to(subscriber, delivery)
        self.record_delivery(subscriber, subscriptions, content_updates, delivery)
        self.update_subscriptions(subscriptions)

    def record_delivery(self, subscriber, subscriptions, content_updates, delivery):
        """
        Add a record to the log in the database declaring the subscription(s)
        as having been sent.
        """
        content_updates = dict([(unicode(key), value) for key, value in content_updates.items()])
        content = 'Content updates:\n%s\nMessage:\n%s' % (json.dumps(content_updates, indent=2), delivery)
        for subscription in subscriptions:
            SubscriptionDispatchRecord.objects.create(
                when=datetime.now(),
                subscription=subscription,
                dispatcher=self.__class__.__name__,
                content=content
            )


class SubscriptionEmailer (SubscriptionDispatcher):
    template_name = 'subscriptions/subscription_email.txt'
    EMAIL_TITLE = "Philly Councilmatic %(date)s"

    def send_email(self, you, emailbody, emailsubject=None):
#        from django.core.mail import send_mail

#        subject = emailsubject or self.EMAIL_TITLE % {'date': date.today()}
#        message = emailbody
#        from_email = 'philly.legislative.list@gmail.com'
#        recipient_list = [you]

#        import settings
#        settings.EMAIL_HOST = 'smtp.gmail.com'
#        settings.EMAIL_PORT = '465'
#        settings.EMAIL_HOST_USER = 'philly.legislative.list'
#        settings.EMAIL_HOST_PASSWORD = 'phillydatacamp'
#        settings.EMAIL_USE_TSL = True

#        send_mail(subject, message, from_email, recipient_list)

        smtphost = "smtp.gmail.com"
        smtpport = '465'
        me =  'philly.legislative.list'
        msg = MIMEText(smart_str(emailbody))
        msg['Subject'] = emailsubject or self.EMAIL_TITLE % {'date': date.today()}
        msg['From'] = me
        msg['To'] = you
        s = smtplib.SMTP_SSL(smtphost, smtpport)
        s.login(me, 'phillydatacamp')
        s.sendmail(me, [you], msg.as_string())
        s.quit()

    def deliver_to(self, subscriber, delivery_text):
        """
        Send an email to the subscriber with the delivery_text
        """
        email_addr = subscriber.email
        email_body = delivery_text
        self.send_email(email_addr, email_body)
