from os import path

def projectpath(rel_path):
    """
    Convert a path relative to the project root into an absolute path.
    """
    project_path = path.dirname(__file__)
    abspath = path.join(project_path, rel_path)
    return abspath

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = ()

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'subscribeme.db',
    }
}

TIME_ZONE = 'America/Chicago'
USE_TZ = True

LANGUAGE_CODE = 'en-us'
USE_I18N = True
USE_L10N = True

SITE_ID = 1

MEDIA_ROOT = ''
MEDIA_URL = ''
ADMIN_MEDIA_PREFIX = '/static/admin/'

STATIC_ROOT = ''
STATIC_URL = '/static/'
STATICFILES_DIRS = (
    projectpath('static'),
)
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = '0r19kk&q0k!f42kwc=82wumo=x&g0o&pe2f(s^6htsn7=mdvyq'

TEMPLATE_DIRS = (
    projectpath('templates')
)
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'urls'


AUTHENTICATION_BACKENDS = (
    'social_auth.backends.twitter.TwitterBackend',
#    'social_auth.backends.facebook.FacebookBackend',
#    'social_auth.backends.google.GoogleOAuthBackend',
#    'social_auth.backends.google.GoogleOAuth2Backend',
#    'social_auth.backends.google.GoogleBackend',
#    'social_auth.backends.yahoo.YahooBackend',
#    'social_auth.backends.contrib.linkedin.LinkedinBackend',
#    'social_auth.backends.contrib.livejournal.LiveJournalBackend',
#    'social_auth.backends.contrib.orkut.OrkutBackend',
#    'social_auth.backends.contrib.foursquare.FoursquareBackend',
#    'social_auth.backends.contrib.github.GithubBackend',
#    'social_auth.backends.OpenIDBackend',
    'django.contrib.auth.backends.ModelBackend',
)

SOCIAL_AUTH_ENABLED_BACKENDS = (
#    'google',
#    'google-oauth',
#    'facebook',
#    'github',
    'twitter',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',

    # 3rd-party reusable apps
    'social_auth',
    'south',
    'crispy_forms',
    'rest_framework',

    # Project apps
    'subscriptions',
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

# Override with local settings
try:
    from local_settings import *
except ImportError:
    pass
