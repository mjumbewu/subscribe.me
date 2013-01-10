def import_all_feeds():
    """
    Import the feeds module from all the installed apps. The assumption is that
    apps will register their feed classes in that module. If not, they're SOL.
    """
    from django.conf.settings import settings
    for app in settings.INSTALLED_APPS:
        feeds_mod = '.'.join([app, 'feed_readers'])
        try:
            __import__(feeds_mod)
        except ImportError:
            pass


class ContentFeedReader (object):
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
        a feed reader identical to this one. The dictionary should be JSON
        serializable.
        """
        raise NotImplementedError()

    def get_updated_since(self, previous):
        """
        Return the content items that have been updated since the given time.
        """
        raise NotImplementedError()

    def get_changes_to(self, item, since):
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


class TimestampedModelFeedReader (ContentFeedReader):
    def __init__(self, app_label, model_name, object_id, updated_datetime_field='updated_datetime'):
        self.app_label = app_label
        self.model_name = model_name
        self.object_id = object_id
        self.updated_datetime_field = updated_datetime_field

    def get_params(self):
        return {
            'app_label': self.app_label,
            'model_name': self.model_name,
            'object_id': self.object_id,
            'updated_datetime_field': self.updated_datetime_field
        }

    def get_content(self):
        if not hasattr(self, 'object_'):
            from django.contrib.contenttypes.models import ContentType
            content_type = ContentType.objects.get(app_label=self.app_label, model=self.model_name)
            self.object_ = content_type.get_object_for_this_type(pk=self.object_id)
        return [self.object_]

    def get_updated_since(self, previous):
        content = self.get_content()
        object_ = content[0]
        if getattr(object_, self.updated_datetime_field) > previous:
            return content
        else:
            return []

    def get_changes_to(self, item, since):
        # We don't know which attributes
        pass

class RSSFeedReader (ContentFeedReader):
    pass
