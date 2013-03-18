"""
"""

from django.test import TestCase
from django.utils.timezone import datetime, now, utc
from collections import defaultdict
from logging import getLogger
from logging import CRITICAL, DEBUG, ERROR, INFO, WARN
from mock import Mock
#from nose.tools import *

from subscriptions.feeds import FeedReader
from subscriptions.feeds import FeedLibrary
from subscriptions.feeds import FeedRecordCleaner
from subscriptions.feeds import FeedRecordUpdater
from subscriptions.feeds import SubscriptionDispatcher
from subscriptions.models import FeedRecord
from subscriptions.models import Subscriber
from subscriptions.models import Subscription
from subscriptions.models import SerializedObjectField
from subscriptions.views import SingleSubscriptionMixin

# Models

class DummyFeed (FeedReader):
    def get_content(self):
        [1,2,3,4]

    def calc_last_updated(self, item):
        return 2


class Test_Subscription_save (TestCase):
    def setUp(self):
        Subscriber.objects.all().delete()
        FeedRecord.objects.all().delete()
        Subscription.objects.all().delete()

        user = self.user = Subscriber(); user.save()
        record = self.record = FeedRecord(); record.save()

        sub = self.sub = Subscription(subscriber=user, feed_record=record); sub.save()

    def test_sets_lastSent_datetime_to_current_time_when_instance_is_new(self):
        subscription = Subscription(subscriber=self.user, feed_record=self.record)

        before = now()
        subscription.save()
        after = now()

        self.assert_(before <= subscription.last_sent <= after)

    def test_doesnt_change_lastSent_datetime_on_instance_thats_already_saved(self):
        subscription = self.sub

        before = now()
        subscription.save()

        self.assert_(subscription.last_sent <= before)

    def test_will_retain_its_value_after_being_queryied(self):
        subscription = Subscription.objects.get(pk=self.sub.pk)

        self.assertEqual(type(subscription.feed_record), type(self.record))


def fail(msg=None):
    ok_(False, msg)

class Test_Subscriber_subscribe (TestCase):

    def setUp(self):
        Subscriber.objects.all().delete()
        FeedRecord.objects.all().delete()
        Subscription.objects.all().delete()

        FeedLibrary().register(FeedReader, 'generic content feed')

        record = self.record = FeedRecord.objects.create(feed_type='generic content feed')
        subscriber = self.subscriber = Subscriber.objects.create()

    def test_creates_a_new_subscription_associating_the_user_and_feed(self):
        feed = FeedReader()
        feed.get_params = lambda: {}
        subscription = self.subscriber.subscribe(feed)

        self.assertEqual(subscription.subscriber, self.subscriber)
        self.assert_(subscription.feed_record.is_equivalent_to(self.record))

    def test_doesnt_save_subscription_if_commit_is_false(self):
        feed = FeedReader()
        feed.get_params = lambda: {}
        subscription = self.subscriber.subscribe(feed, commit=False)

        self.assertIsNone(subscription.pk)

    def test_raises_NotFound_when_feed_is_not_registered (self):
        class BogusFeed(FeedReader):
            pass

        feed = BogusFeed()
        try:
            self.subscriber.subscribe(feed)
            fail('Should have raised BogusFeed.NotFound exception')
        except BogusFeed.NotFound:
            pass


class Test_FeedLibrary_getFeed (TestCase):

    def test_raises_KeyError_when_feed_is_not_registered (self):
        library = FeedLibrary()
        record = Mock()
        record.feed_type = 'nonexistent'

        with self.assertRaises(KeyError):
            library.get_feed(record)


class ListItemFeed (FeedReader):
    def __init__(self, items):
        self.items = eval(items)

    def get_content(self):
        return self.items

    def get_params(self):
        return {'items': str(self.items)}

    def get_last_updated(self, item):
        return datetime.date.today()

    def get_last_updated_time(self):
        return datetime.today()


class Test_Subscriber_isSubscribed (TestCase):

    def setUp(self):
        Subscriber.objects.all().delete()
        FeedRecord.objects.all().delete()
        Subscription.objects.all().delete()

        library = self.library = FeedLibrary(shared=False)
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


class Test_FeedLibrary_caching (TestCase):

    def test_causes_the_same_content_feed_to_be_returned_on_different_calls_to_getFeed (self):
        library = FeedLibrary(shared=False)
        library.register(ListItemFeed, 'li')

        feed = ListItemFeed('[1, 2, 3]')
        record = library.get_record(feed)

        self.assertIs(feed, library.get_feed(record))

    def test_causes_the_same_feed_record_to_be_returned_on_different_calls_to_getRecord (self):
        library = FeedLibrary(shared=False)
        library.register(ListItemFeed, 'li')

        feed = ListItemFeed('[1, 2, 3]')
        record = library.get_record(feed)

        self.assertIs(record, library.get_record(feed))

    def test_doesnt_return_the_same_record_from_different_libraries (self):
        library1 = FeedLibrary(shared=False)
        library1.register(ListItemFeed, 'li')

        library2 = FeedLibrary(shared=False)
        library2.register(ListItemFeed, 'li')

        feed = ListItemFeed('[1, 2, 3]')
        record = library1.get_record(feed)

        self.assertIsNot(record, library2.get_record(feed))

    def test_doesnt_return_the_same_feed_from_different_libraries (self):
        library1 = FeedLibrary(shared=False)
        library1.register(ListItemFeed, 'li')

        library2 = FeedLibrary(shared=False)
        library2.register(ListItemFeed, 'li')

        feed = ListItemFeed('[1, 2, 3]')
        record = library1.get_record(feed)

        self.assertIsNot(feed, library2.get_feed(record))

# Management commands

class Test_FeedUpdater_updateAll (TestCase):

    def setUp(self):

        library = self.library = FeedLibrary(shared=False)
        library.register(ListItemFeed, 'list feed')

        self.feeds = [ ListItemFeed("['hello']"),
                       ListItemFeed("['world']") ]

        for feed in self.feeds:
            feed.get_last_updated_time = Mock(return_value=datetime.today())

        self.feed_records = [library.get_record(feed) for feed in self.feeds]

    def test_calls_get_last_updated_time_on_all_feed_objects(self):

        updater = FeedRecordUpdater()

        updater.update_all(self.feed_records, self.library)

        self.assertEqual(self.feeds[0].get_last_updated_time.call_count, 1)
        self.assertEqual(self.feeds[1].get_last_updated_time.call_count, 1)


class Test_FeedCleaner_clean (TestCase):

    def setUp(self):
        FeedRecord.objects.all().delete()
        Subscriber.objects.all().delete()

        library = self.library = FeedLibrary(shared=False)
        library.register(ListItemFeed, 'list feed')

        feeds = [ ListItemFeed("['hello']"),
                  ListItemFeed("['world']") ]

        feed_records = [library.get_record(feed) for feed in feeds]
        subscriber = Subscriber.objects.create()
        subscriber.subscribe(feeds[0], library)

        self.keeper = feed_records[0]
        self.tosser = feed_records[1]

    def test_removes_unused_feed_records_and_leaves_used_ones(self):
        cleaner = FeedRecordCleaner()
        cleaner.clean()

        feed_records = FeedRecord.objects.all()
        self.assertEqual(len(feed_records), 1)
        self.assertIn(self.keeper, feed_records)
        self.assertNotIn(self.tosser, feed_records)


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


class Test_SingleSubscriptionMixin_getContextData (TestCase):

    def setUp(self):
        class DoNothinView (object):
            def get_context_data(self, **kwargs):
                # This is just so that SingleSubscriptionMixin.get_context_data
                # super has something to call.
                return {}

        library = FeedLibrary(shared=False)
        library.register(ListItemFeed, 'my list item feed')

        class SubscriptionView (SingleSubscriptionMixin, DoNothinView):
            def get_content_feed_library(self):
                return library

            def get_content_feed(self):
                return ListItemFeed('[1,2,3]')

        self.view = SubscriptionView()
        self.view.request = Mock()
        self.view.feed_data = FeedReader

    def tearDown(self):
        Subscriber.objects.all().delete()

    def test_has_isSubscribed_set_to_False_when_unauthenticated (self):
        class AnonymousUser (Mock):
            def is_authenticated(self):
                return False
        self.view.request.user = AnonymousUser()

        data = self.view.get_context_data()

        self.assertEqual(data['is_subscribed'], False)
        self.assertIsNone(data['subscription'])
        self.assertIsNone(data['subscription_form'])

    def test_has_isSubscribed_set_to_True_when_subscribed (self):
        class MyUser (Mock):
            def is_authenticated(self):
                return True
            def subscription(self, feed, library):
                return Mock()
        self.view.request.user = MyUser()

        data = self.view.get_context_data()

        self.assertEqual(data['is_subscribed'], True)
        self.assertIsNotNone(data['subscription'])
        self.assertIsNone(data['subscription_form'])

    def test_has_isSubscribed_set_to_False_when_not_subscribed (self):
        self.view.request.user = Subscriber.objects.create(username='123', email='a@b.com', password='456')
        self.view.request.user.subscription = lambda *args, **kwargs: None

        data = self.view.get_context_data()

        self.assertEqual(data['is_subscribed'], False)
        self.assertIsNone(data['subscription'])
        self.assertIsNotNone(data['subscription_form'])

    def test_configures_the_form_correctly_when_not_subscribed (self):
        # i.e.:
        #  * the form subscriber and feed_record are set to primary keys
        #    instead of objects of types Subscriber and FeedRecord
        #  * their is no last_sent field on the form (it should be set
        #    automatically)

        self.view.request.user = Subscriber.objects.create(username='abc', email='a@b.com', password='def')
        self.view.request.user.subscription = lambda *args, **kwargs: None

        data = self.view.get_context_data()
        form = data['subscription_form']

        self.assertNotIn('last_sent', form.fields)


class Test_SubscriptionDispatcher_dispatch (TestCase):

    def setUp(self):
        library = self.library = FeedLibrary()
        subscriber = self.subscriber = Mock()
        subscription = self.subscription = Mock()
        subscription.last_sent = datetime(2011,1,1,0,0).replace(tzinfo=utc)  # Never been sent
        subscription.feed_record.feed_type = 'MockFeed'
        subscription.feed_record.feed_params = {'p1': '1', 'p2': '2'}
        subscription.feed_record.last_updated = datetime(2011,8,4,6,50).replace(tzinfo=utc)
        subscriber.subscriptions.all = lambda: [subscription]

    def test_updates_the_lastSent_time_of_the_subscription_to_the_feeds_lastUpdated_time (self):
        mock_feed = Mock()
        self.library.get_feed = lambda *a, **k: mock_feed

        # Iff we say that there is updated content, the last_sent datetime
        # should be updated.
        mock_feed.get_updated_since = lambda *a, **k: ['item']
        mock_feed.get_changes_to = lambda *a, **k: ({}, datetime(2011,8,4,5,40).replace(tzinfo=utc))

        dispatcher = SubscriptionDispatcher()
        dispatcher.template_name = 'subscriptions/subscription_email.txt'
        dispatcher.deliver_to = Mock()
        dispatcher.record_delivery = Mock()

        dispatcher.dispatch_subscriptions_for(self.subscriber, self.library)

        self.assertEqual(self.subscription.last_sent, datetime(2011,8,4,6,50).replace(tzinfo=utc))
