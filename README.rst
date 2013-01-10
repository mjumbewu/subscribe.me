Accessing a Subscriber instance from a User
-------------------------------------------

``Subscriber`` is a proxy model. You may find yourself wanting to access the
methods on a subscriber instance from an ``auth.User`` instance. There are a
few workarounds for this on StackOverflow:

* `using django, how do i construct a proxy object instance from a superclass object instance? <http://stackoverflow.com/questions/3920909/using-django-how-do-i-construct-a-proxy-object-instance-from-a-superclass-objec>`_
* `customizing request.user with a proxy model that extends Django User model <http://stackoverflow.com/questions/9593877/customizing-request-user-with-a-proxy-model-that-extends-django-user-model>`_
* `User proxy model from request <http://stackoverflow.com/questions/10682414/django-user-proxy-model-from-request>`_

If you are using Django 1.5 or above, I recommend using the ``AUTH_USER_MODEL``
configuration variable, and setting it to ``'subscriptions.Subscriber'``. If
you cannot use Django 1.5 or above, we provide an authentication backend that
loads a ``Subscriber`` instance. Just add the following to your settings::

    AUTHENTICATION_BACKENDS = ['subscriptions.auth_backends.SubscriberBackend']
