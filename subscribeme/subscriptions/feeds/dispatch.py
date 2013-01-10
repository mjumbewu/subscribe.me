from email.mime.text import MIMEText

from django.conf import settings
from django.contrib.sites.models import Site
from django.db.models.manager import Manager
from django.template import Context
from django.template.loader import get_template
from django.utils.encoding import smart_str, smart_unicode

from ..models import SubscriptionDispatchRecord
from .library import ContentFeedLibrary

from logging import getLogger
log = getLogger(__name__)


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

        content_changes = defaultdict(lambda: [dict(), datetime.min])

        for subscription in subscriptions:
            feed = library.get_feed(subscription.feed_record)

            # Check whether the feed has been updated since the subscription
            # was last sent (this assumes that the feed_record has been
            # updated to accurately represent the feed).
            if subscription.last_sent < subscription.feed_record.last_updated:
                new_contents = feed.get_updates_since(subscription.last_sent)

                for item in new_contents:
                    changes, change_time = feed.get_changes_to(item, subscription.last_sent)
                    content_changes[item][0].update(changes)
                    content_changes[item][1] = max(content_changes[item][1], change_time)

        log.debug('What changed: %s' % (content_changes,))

        return content_changes

    def render(self, subscriber, subscriptions, content_updates, library=None):
        """
        Render the given content updates to a template for the subscriber.
        """
        template = get_template(self.template_name)

        # I was having some trouble iterating over content_items as a dict
        # in the templates, so I'll just convert content updates to lists of
        # tuples.
        content_updates = sorted(content_updates.items(), key=lambda (i, (c, d)): d)
        content_updates = [(k, v.items()) for (k, (v, d)) in content_updates]

        context = Context({'library': library,
                           'subscriber':subscriber,
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
        if content_updates:
            delivery = self.render(subscriber, subscriptions, content_updates, library)
            self.deliver_to(subscriber, delivery)
            self.record_delivery(subscriber, subscriptions,
                                 content_updates, delivery)
            self.update_subscriptions(subscriptions)

    def record_delivery(self, subscriber, subscriptions, content_updates, delivery):
        """
        Add a record to the log in the database declaring the subscription(s)
        as having been sent.
        """
        content_updates = dict([(unicode(key), value) for key, value in content_updates.items()])
        content = 'Content updates:\n%s\nMessage:\n%s' % (json.dumps(content_updates, indent=2, cls=DjangoJSONEncoder), delivery)
        for subscription in subscriptions:
            SubscriptionDispatchRecord.objects.create(
                when=datetime.now(),
                subscription=subscription,
                dispatcher=self.__class__.__name__,
                content=content
            )


class SubscriptionEmailer (SubscriptionDispatcher):
    template_name = 'subscriptions/subscription_email.txt'
    subject_template_name = 'subscriptions/subscription_subject.txt'

    def send_email(self, you, emailbody, emailsubject=None):
        from django.core.mail import send_mail

        subject = emailsubject
        message = emailbody
        from_email = settings.SUBSCRIPTIONS_SENDER
        recipient_list = [you]

        send_mail(subject, message, from_email, recipient_list)

    def render_subject(self, context):
        template = get_template(subject_template_name)
        return template.render(context)

    def deliver_to(self, subscriber, delivery_text):
        """
        Send an email to the subscriber with the delivery_text
        """
        email_addr = subscriber.email
        email_body = delivery_text
        email_subject = self.render_subject({'subscriber': subscriber, 'text': delivery_text, 'today': date.today()})
        self.send_email(email_addr, email_body, email_subject)
