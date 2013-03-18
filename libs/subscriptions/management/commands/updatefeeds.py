from django.core.management.base import BaseCommand, CommandError

from subscriptions.feeds import autodiscover
from subscriptions.feeds import FeedRecordUpdater
from subscriptions.models import FeedRecord


class Command(BaseCommand):
    help = "Update the meta-information for the subscription content feeds."

    def get_records(self):
        records = FeedRecord.objects.all()
        return records

    def handle(self, *args, **options):
        # Make sure that the library knows about all the types of feeds.
        autodiscover()

        records = self.get_records()
        updater = FeedRecordUpdater()
        updater.update_all(records)
