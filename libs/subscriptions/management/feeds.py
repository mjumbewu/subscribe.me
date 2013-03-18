import datetime

class FeedCollector (object):
    def __date_to_datetime(self, d):
        if isinstance(d, datetime.date):
            return datetime.datetime(d.year, d.month, d.day)
        else:
            return d

    def collect_new_content(self, feed, last_sent):
        """Returns exactly those items in the given feed that are newer than the
           last_sent datetime. Converts dates to datetimes for comparison, if
           necessary."""
        content = []

        last_sent = self.__date_to_datetime(last_sent)
        for item in feed.get_content():

            last_updated = feed.get_last_updated(item)
            last_updated = self.__date_to_datetime(last_updated)

            if last_updated > last_sent:
                content.append(item)

        return content
