"""
"""

import datetime
import pickle

from django.test import TestCase
from logging import getLogger
from logging import CRITICAL, DEBUG, ERROR, INFO, WARN
from mock import Mock
from nose.tools import *

from subscriptions.feeds import ContentFeedReader
from subscriptions.feeds import ContentFeedLibrary
from subscriptions.feeds import ContentFeedRecordCleaner
from subscriptions.feeds import ContentFeedRecordUpdater
from subscriptions.feeds import SubscriptionDispatcher
from subscriptions.forms import SubscriptionForm
from subscriptions.models import ContentFeedRecord
from subscriptions.models import Subscriber
from subscriptions.models import Subscription
from subscriptions.models import SerializedObjectField
from subscriptions.views import SingleSubscriptionMixin

# Models

class DummyFeed (ContentFeedReader):
    def get_content(self):
        [1,2,3,4]

    def calc_last_updated(self, item):
        return 2


class Test_Subscription_save (TestCase):
    def setUp(self):
        Subscriber.objects.all().delete()
        ContentFeedRecord.objects.all().delete()
        Subscription.objects.all().delete()

        user = self.user = Subscriber(); user.save()
        record = self.record = ContentFeedRecord(); record.save()

        sub = self.sub = Subscription(subscriber=user, feed_record=record); sub.save()

    def test_sets_lastSent_datetime_to_current_time_when_instance_is_new(self):
        subscription = Subscription(subscriber=self.user, feed_record=self.record)

        before = datetime.datetime.now()
        subscription.save()
        after = datetime.datetime.now()

        self.assert_(before <= subscription.last_sent <= after)

    def test_doesnt_change_lastSent_datetime_on_instance_thats_already_saved(self):
        subscription = self.sub

        before = datetime.datetime.now()
        subscription.save()

        self.assert_(subscription.last_sent <= before)

    def test_will_retain_its_value_after_being_queryied(self):
        subscription = Subscription.objects.get(pk=self.sub.pk)

        assert_equal(type(subscription.feed_record), type(self.record))


def fail(msg=None):
    ok_(False, msg)

class Test_Subscriber_subscribe (TestCase):

    def setUp(self):
        Subscriber.objects.all().delete()
        ContentFeedRecord.objects.all().delete()
        Subscription.objects.all().delete()

        ContentFeedLibrary().register(ContentFeedReader, 'generic content feed')

        record = self.record = ContentFeedRecord.objects.create(feed_name='generic content feed')
        subscriber = self.subscriber = Subscriber.objects.create()

    def test_creates_a_new_subscription_associating_the_user_and_feed(self):
        feed = ContentFeedReader()
        feed.get_params = lambda: {}
        subscription = self.subscriber.subscribe(feed)

        self.assertEqual(subscription.subscriber, self.subscriber)
        self.assert_(subscription.feed_record.is_equivalent_to(self.record))

    def test_doesnt_save_subscription_if_commit_is_false(self):
        feed = ContentFeedReader()
        feed.get_params = lambda: {}
        subscription = self.subscriber.subscribe(feed, commit=False)

        self.assertIsNone(subscription.pk)

    def test_raises_NotFound_when_feed_is_not_registered (self):
        class BogusFeed(ContentFeedReader):
            pass

        feed = BogusFeed()
        try:
            self.subscriber.subscribe(feed)
            fail('Should have raised BogusFeed.NotFound exception')
        except BogusFeed.NotFound:
            pass


class ListItemFeed (ContentFeedReader):
    def __init__(self, items):
        self.items = eval(items)

    def get_content(self):
        return self.items

    def get_params(self):
        return {'items': str(self.items)}

    def get_last_updated(self, item):
        return datetime.date.today()


class Test_Subscriber_isSubscribed (TestCase):

    def setUp(self):
        Subscriber.objects.all().delete()
        ContentFeedRecord.objects.all().delete()
        Subscription.objects.all().delete()

        library = self.library = ContentFeedLibrary(shared=False)
        library.register(ListItemFeed, 'list feed')

        feed = self.feed = ListItemFeed('[1,2,3]')
        record = self.record = library.get_record(feed)
        subscriber = self.subscriber = Subscriber.objects.create()

        subscriber.subscribe(feed, library)
        subscriber.save()

    def test_returns_true_when_feed_is_found(self):
        feed2 = ListItemFeed('[1,2,3]')
        record2 = self.library.get_record(feed2)
#        import pdb; pdb.set_trace()
        subscription = self.subscriber.subscription(feed2, self.library)

        assert subscription is not None

    def test_returns_false_when_feed_is_not_found(self):
        feed2 = ListItemFeed('[2,3,4]')
        record2 = self.library.get_record(feed2)
        subscription = self.subscriber.subscription(feed2, self.library)

        assert subscription is None


class Test_ContentFeedLibrary_caching:

    @istest
    def causes_the_same_content_feed_to_be_returned_on_different_calls_to_getFeed (self):
        library = ContentFeedLibrary(shared=False)
        library.register(ListItemFeed, 'li')

        feed = ListItemFeed('[1, 2, 3]')
        record = library.get_record(feed)

        assert_is(feed, library.get_feed(record))

    @istest
    def causes_the_same_feed_record_to_be_returned_on_different_calls_to_getRecord (self):
        library = ContentFeedLibrary(shared=False)
        library.register(ListItemFeed, 'li')

        feed = ListItemFeed('[1, 2, 3]')
        record = library.get_record(feed)

        assert_is(record, library.get_record(feed))

    @istest
    def doesnt_return_the_same_record_from_different_libraries (self):
        library1 = ContentFeedLibrary(shared=False)
        library1.register(ListItemFeed, 'li')

        library2 = ContentFeedLibrary(shared=False)
        library2.register(ListItemFeed, 'li')

        feed = ListItemFeed('[1, 2, 3]')
        record = library1.get_record(feed)

        assert_is_not(record, library2.get_record(feed))

    @istest
    def doesnt_return_the_same_feed_from_different_libraries (self):
        library1 = ContentFeedLibrary(shared=False)
        library1.register(ListItemFeed, 'li')

        library2 = ContentFeedLibrary(shared=False)
        library2.register(ListItemFeed, 'li')

        feed = ListItemFeed('[1, 2, 3]')
        record = library1.get_record(feed)

        assert_is_not(feed, library2.get_feed(record))

# Management commands

class Test_ContentFeedUpdater_updateAll (TestCase):

    def setUp(self):

        library = self.library = ContentFeedLibrary(shared=False)
        library.register(ListItemFeed, 'list feed')

        self.feeds = [ ListItemFeed("['hello']"),
                       ListItemFeed("['world']") ]

        for feed in self.feeds:
            feed.get_last_updated = Mock(return_value=datetime.date.today())

        self.feed_records = [library.get_record(feed) for feed in self.feeds]

    @istest
    def calls_get_last_updated_on_all_feed_objects(self):

        updater = ContentFeedRecordUpdater()

        updater.update_all(self.feed_records, self.library)

        self.feeds[0].get_last_updated.assert_called_with('hello')
        self.feeds[1].get_last_updated.assert_called_with('world')


class Test_ContentFeedCleaner_clean (TestCase):

    def setUp(self):
        ContentFeedRecord.objects.all().delete()
        Subscriber.objects.all().delete()

        library = self.library = ContentFeedLibrary(shared=False)
        library.register(ListItemFeed, 'list feed')

        feeds = [ ListItemFeed("['hello']"),
                  ListItemFeed("['world']") ]

        feed_records = [library.get_record(feed) for feed in feeds]
        subscriber = Subscriber.objects.create()
        subscriber.subscribe(feeds[0], library)

        self.keeper = feed_records[0]
        self.tosser = feed_records[1]

    @istest
    def removes_unused_feed_records_and_leaves_used_ones(self):
        cleaner = ContentFeedRecordCleaner()
        cleaner.clean()

        feed_records = ContentFeedRecord.objects.all()
        assert_equal(len(feed_records), 1)
        assert_in(self.keeper, feed_records)
        assert_not_in(self.tosser, feed_records)


#class Test_FeedCollector_collectNewContent (TestCase):

#    def test_returns_exactly_those_items_newer_than_the_last_sent_datetime(self):
#        feed = Mock()
#        feed.get_content = Mock(return_value=[datetime.datetime(2009, 1, 1),
#                                              datetime.datetime(2010, 1, 1),
#                                              datetime.datetime(2011, 1, 1),
#                                              datetime.datetime(2012, 1, 1),])
#        feed.get_last_updated = lambda item: item
#        last_sent = datetime.datetime(2010, 1, 1)

#        collector = FeedCollector()
#        content = collector.collect_new_content(feed, last_sent)

#        self.assertEqual(content, [datetime.datetime(2011, 1, 1),
#                                   datetime.datetime(2012, 1, 1),])

#    def test_converts_dates_to_datetimes_for_comparison(self):
#        feed = Mock()
#        feed.get_content = Mock(return_value=[False, '1', '2', '3', '4', '5'])

#        # The last_sent value is compared with feed.get_last_updated(...), so
#        # check one direction first...
#        feed.get_last_updated = lambda item: datetime.date(2011, 8, 23)
#        last_sent = datetime.datetime(2011, 8, 23)

#        collector = FeedCollector()
#        try:
#            content = collector.collect_new_content(feed, last_sent)
#        except TypeError, e:
#            self.fail(e)

#        # ...then check the other direction.
#        feed.get_last_updated = lambda item: datetime.datetime(2011, 8, 23)
#        last_sent = datetime.date(2011, 8, 23)

#        collector = FeedCollector()
#        try:
#            content = collector.collect_new_content(feed, last_sent)
#        except TypeError, e:
#            self.fail(e)


class Test_SerializedObjectField_toPython (TestCase):

    def test_converts_unicode_strings_to_nonunicode_before_loading(self):
        pickled_list = u'(lp0\n.'
        field = SerializedObjectField()

        result = field.to_python(pickled_list)

        self.assertEqual(result, [])


class Test_SingleSubscriptionMixin_getContextData:

    def setUp(self):
        class DoNothinView (object):
            def get_context_data(self, **kwargs):
                # This is just so that SingleSubscriptionMixin.get_context_data
                # super has something to call.
                return {}

        library = ContentFeedLibrary(shared=False)
        library.register(ListItemFeed, 'my list item feed')

        class SubscriptionView (SingleSubscriptionMixin, DoNothinView):
            def get_content_feed_library(self):
                return library

            def get_content_feed(self):
                return ListItemFeed('[1,2,3]')

        self.view = SubscriptionView()
        self.view.request = Mock()
        self.view.feed_data = ContentFeedReader

    @istest
    def has_isSubscribed_set_to_False_when_unauthenticated (self):
        class AnonymousUser (Mock):
            def is_authenticated(self):
                return False
        self.view.request.user = AnonymousUser()

        data = self.view.get_context_data()

        assert_equal(data['is_subscribed'], False)
        assert_is_none(data['subscription'])
        assert_is_none(data['subscription_form'])

    @istest
    def has_isSubscribed_set_to_True_when_subscribed (self):
        class MyUser (Mock):
            def is_authenticated(self):
                return True
            def subscription(self, feed, library):
                return Mock()
        self.view.request.user = MyUser()

        data = self.view.get_context_data()

        assert_equal(data['is_subscribed'], True)
        assert_is_not_none(data['subscription'])
        assert_is_none(data['subscription_form'])

    @istest
    def has_isSubscribed_set_to_False_when_not_subscribed (self):
        class Subscriber (Mock):
            def subscription(self, feed, library):
                return None
        class MyUser (Mock):
            def is_authenticated(self):
                return True
            def subscription(self, feed, library):
                return None
            subscriber = Subscriber()

        self.view.request.user = MyUser()

        data = self.view.get_context_data()

        assert_equal(data['is_subscribed'], False)
        assert_is_none(data['subscription'])
        assert_is_not_none(data['subscription_form'])

    @istest
    def configures_the_form_correctly_when_not_subscribed (self):
        # i.e.:
        #  * the form subscriber and feed_record are set to primary keys
        #    instead of objects of types Subscriber and ContentFeedRecord
        #  * their is no last_sent field on the form (it should be set
        #    automatically)

        class Subscriber (Mock):
            def subscription(self, feed, library):
                return None
            pk = 1
        class MyUser (Mock):
            def is_authenticated(self):
                return True
            def subscription(self, feed, library):
                return None
            subscriber = Subscriber()

        self.view.request.user = MyUser()

        data = self.view.get_context_data()
        form = data['subscription_form']

        assert_is_instance(form.data['feed_record'], (int, basestring))
        assert_is_instance(form.data['subscriber'], (int, basestring))
        assert_not_in('last_sent', form.fields)


class Test_SubscriptionDispatcher_dispatch:

    def setup(self):
        library = self.library = ContentFeedLibrary()
        subscriber = self.subscriber = Mock()
        subscription = self.subscription = Mock()
        subscription.last_sent = datetime.datetime(2011,1,1,0,0)
        subscription.feed_record.last_updated = datetime.datetime(2011,8,4,6,50)
        subscription.feed_record.feed_name = 'MockFeed'
        subscription.feed.feed_params = {'p1': '1', 'p2': '2'}
        subscriber.subscriptions.all = lambda: [subscription]

    @istest
    def updates_the_lastSent_time_of_the_subscription_to_the_feeds_lastUpdated_time (self):
        mock_feed = Mock()
        self.library.get_feed = lambda *a, **k: mock_feed
        mock_feed.get_updates_since = lambda *a, **k: []

        dispatcher = SubscriptionDispatcher()
        dispatcher.template_name = 'subscriptions/subscription_email.txt'
        dispatcher.deliver_to = Mock()
        dispatcher.record_delivery = Mock()

        dispatcher.dispatch_subscriptions_for(self.subscriber, self.library)

        assert_equal(self.subscription.last_sent, datetime.datetime(2011,8,4,6,50))


class Test_SubscriptionForm_save:

    def setup(self):
        Subscription.objects.all().delete()
        Subscriber.objects.all().delete()
        ContentFeedRecord.objects.all().delete()

        self.library = ContentFeedLibrary(shared=False)
        self.library.register(ListItemFeed, 'my list items')

        self.subscriber = Subscriber.objects.create()
        self.feed = ListItemFeed('[1, 2, 3]')
        self.feed_record = self.library.get_record(self.feed)

    @istest
    def creates_a_subscription_for_the_subscriber_to_the_feed (self):
        form = SubscriptionForm({'subscriber':self.subscriber.pk,
                                 'feed_record':self.feed_record.pk})

        assert form.is_valid(), 'The form had errors: %r' % (form.errors,)
        form.save()
        subscription = self.subscriber.subscription(self.feed, self.library)

        assert subscription is not None
