from ..models import FeedRecord

from logging import getLogger
log = getLogger(__name__)


class FeedLibrary (object):

    feeds = {}
    """Map of { feed_type_name : FeedClass }"""

    _reverse = {}
    """Map of { FeedClass : feed_type_name }. For reverse-lookup"""

    _feed_cache = {}
    _record_cache = {}

    def __init__(self, shared=True):
        if not shared:
            self.feeds = {}
            self._reverse = {}
            self._feed_cache = {}
            self._record_cache = {}

    def register(self, FeedType, type_name):
        """Add the given feed type to the registry by the given type name."""
        self.feeds[type_name] = FeedType
        self._reverse[FeedType] = type_name

    def _cache(self, feed, record):
        self._feed_cache[record] = feed
        self._record_cache[feed] = record

    def get_feed(self, record):
        """Retrieve a feed based on the given record."""

        if record in self._feed_cache:
            return self._feed_cache[record]

        try:
            FeedType = self.feeds[record.feed_type]
        except KeyError:
            raise KeyError('No feed with type %r registered' % record.feed_type)

        kwargs = record.feed_params
        feed = FeedType(**kwargs)

        self._cache(feed, record)

        log.debug('The record %r represents the feed %r' % (record, feed))

        return feed

    def get_record(self, feed):
        """Retrieve a record describing the given feed."""

        if feed in self._record_cache:
            return self._record_cache[feed]

        FeedType = feed.__class__
        try:
            type_name = self._reverse[FeedType]
        except KeyError:
            log.debug('%s is not registered in the library: %s' %
                (feed.__class__.__name__, self.feeds))
            raise FeedType.NotFound(
                '%s is not registered in the library' %
                (feed.__class__.__name__,))

        record = FeedRecord()
        record.feed_type = type_name
        record.feed_params = feed.get_params()
        record.save()

        self._cache(feed, record)

        return record
