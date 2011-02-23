DEBUG = True
TEMPLATE_DEBUG = DEBUG
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
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
SITE_NAME = 'Blake\'s Q/A Site (beta)'
SITE_DOMAIN = 'localhost:8000'
MEDIA_ROOT = ''
MEDIA_URL = ''
ADMIN_MEDIA_PREFIX = '/media/'
SECRET_KEY = ''
MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'
TEMPLATE_DIRS = (
	'/absolute/path/to/templates'
)
AMAZON_DOMAIN = 'authorize.payments-sandbox.amazon.com'
AWS_KEY_ID = 'AKIAJJSGY3AIETRPFIZA'
AWS_SECRET_KEY = ''
