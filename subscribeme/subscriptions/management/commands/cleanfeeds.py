from django.core.management.base import BaseCommand, CommandError

from subscriptions.feeds import ContentFeedRecordCleaner


class Command(BaseCommand):
    help = "Clean the list of content feeds of all that are unusubscribed to."

    def handle(self, *args, **options):
        # Get rid of unused records
        cleaner = ContentFeedRecordCleaner()
        cleaner.clean()
