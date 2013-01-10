from ..models import ContentFeedRecord

from logging import getLogger
log = getLogger(__name__)


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
