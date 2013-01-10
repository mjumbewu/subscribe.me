from ..models import Subscription
from ..models import ContentFeedRecord
from .library import ContentFeedLibrary

from logging import getLogger
log = getLogger(__name__)


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
