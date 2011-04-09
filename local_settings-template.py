#import sys
#sys.path.append('/path/to/qa')

ADMIN_MEDIA_PREFIX = '/media/'
AMAZON_COBRAND = ''
AMAZON_DOMAIN = 'fps.sandbox.amazonaws.com'
AWS_KEY_ID = 'AKIAJJSGY3AIETRPFIZA'
AWS_SECRET_KEY = ''
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': '',                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}
DEBUG = True
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
MEDIA_ROOT = ''
MEDIA_URL = ''
MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'
SECRET_KEY = ''
SITE_DOMAIN = 'localhost:8000'
TEMPLATE_DEBUG = DEBUG
TEMPLATE_DIRS = (
	'/absolute/path/to/templates'
)
