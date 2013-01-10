"""
An analogy to charachterize the system
======================================

A ``ContentFeedReader`` reads the pages (content) of a book (feed). At any given
point, you can have it read all the pages that have been written for a book. A
``ContentFeedRecord`` holds information about how the book (content feed) can be
retrieved -- it is the card in the catalog for the book.

The ``ContentFeedLibrary`` is the librarian and card catalog all in one. It
knows about all the books and how to retrieve them based on the information in
the card (content parameters) to see if it has any more pages. A book must be
registered with the librarian so that it knows what to look for when it finds
its entry in the card catalog.

A ``Subscription`` is a ledger of information of what pages have been checked
out of the library on your behalf. Based on the contents of that ledger, the
``SubscriptionDispatcher`` gets new book pages from the library for you. You
could go and get the books yourself, but the dispatcher will just go and grab
anything new each day.

The courier (dispatcher) will actually not deliver the pages to you from one
book (feed) at a time. Instead it will take into account all the books that
you're subscribed to and coallate the content. Interestingly, some of the
content may appear in more than one book. And that's ok! When the courier gets
the same pages from two different authors, it'll make sure to deliver that page
only once.

feed_readers.py
===============

class NewLegislationFeedReader (ContentFeedReader):
    def get_query_set(self):
        ...

ContentFeedLibrary.register(NewLegislationFeedReader, 'Newly introduced legislation')
ContentFeedLibrary.register(...)

sendupdates.py
==============

new_content = subscription.get_new_content(library)
if new_content:
    dispatcher.send(subscriber, new_content)

"""
