from .settings_common import *

import os
import re

DEBUG = True

# logging
LOGGING_DIR = os.path.join(SERVICES_DIR, 'logs')
LOGGING['handlers']['file']['filename'] = os.path.join(LOGGING_DIR, 'django.log')

# user-generated files
AWS_S3_ENDPOINT_URL = 'https://perma.minio.test:9000'
AWS_ACCESS_KEY_ID = 'accesskey'
AWS_SECRET_ACCESS_KEY = 'secretkey'
AWS_STORAGE_BUCKET_NAME = 'perma-storage'
AWS_S3_VERIFY = False

# static files
STATIC_ROOT = os.path.join(SERVICES_DIR, 'django/static_assets/')

# print email to console
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'secret'

# Google Analytics
GOOGLE_ANALYTICS_KEY = 'UA-XXXXX-X'
GOOGLE_ANALYTICS_DOMAIN = 'example.com'

CELERY_RESULT_BACKEND = None
# don't require celery listener
CELERY_TASK_ALWAYS_EAGER = True
# propagate exceptions from eager tasks for easier debugging
CELERY_TASK_EAGER_PROPAGATES = True

### optional dev packages ###

# django-debug-toolbar
if os.environ.get('DEBUG_TOOLBAR'):
    # import debug_toolbar  # noqa
    INSTALLED_APPS += (
        'debug_toolbar',
    )
    DEBUG_TOOLBAR_CONFIG = {
        'SHOW_TOOLBAR_CALLBACK': 'perma.utils.show_debug_toolbar'  # we have to override this check because the default depends on IP address, which doesn't work inside Vagrant
    }
    MIDDLEWARE = ('debug_toolbar.middleware.DebugToolbarMiddleware',) + MIDDLEWARE

# django_extensions
try:
    import django_extensions  # noqa
    INSTALLED_APPS += (
        # Switch to this when we upgrade to Django 1.7.x:
        #'debug_toolbar.apps.DebugToolbarConfig',
        'django_extensions',
    )
except ImportError:
    pass


# Our Sorl thumbnail stuff. In prod we use Redis, we'll just use
# the local uncached DB here in dev.
THUMBNAIL_KVSTORE = 'sorl.thumbnail.kvstores.cached_db_kvstore.KVStore'


#
# Perma Payments
#
PURCHASE_URL = 'http://localhost/purchase/'
PURCHASE_HISTORY_URL = 'http://perma-payments/purchase-history/'
ACKNOWLEDGE_PURCHASE_URL = 'http://perma-payments/acknowledge-purchase/'
SUBSCRIBE_URL = 'http://localhost/subscribe/'
CANCEL_URL = 'http://localhost/cancel-request/'
SUBSCRIPTION_STATUS_URL = 'http://perma-payments/subscription/'
UPDATE_URL = 'http://localhost/update/'
CHANGE_URL = 'http://localhost/change/'

# Perma.cc encryption keys for communicating with Perma-Payments
# generated using perma_payments.security.generate_public_private_keys
# SECURITY WARNING: keep the production secret key secret!
# These keys are just for local development, and are safe to commit to the repo
PERMA_PAYMENTS_ENCRYPTION_KEYS = {
    'id': 1,
    'perma_secret_key': "hneZHHft4QieiNmyVPfyYFJs3toRgixbiTqSQKJ1r2E=",
    'perma_public_key': "+Y3Kni4Pm+5kWFJgsBL28TyKcgciQdPofRsTwUKaVSE=",
    'perma_payments_public_key': "FhfWRc3QmLzG9SY+QwvTNMT9vcACNzpcMyvNSxKg0jA="
}


# Upload scanning
SCAN_UPLOADS = True
SCAN_URL = 'http://filecheck:8888/scan/'


# Scoop
SCOOP_API_URL = 'http://scoop-rest-api:5000/'
if not SCOOP_API_KEY:
    try:
        # Extract the latest API key from the file.
        # This approach could be slow if the file gets too long... but I'm not worried about it.
        with open('/tmp/scoop_access_key/access_key.txt', 'r') as f:
            last_line = f.readlines()[-1]
            match = re.search(r': (.*?) ', last_line)
            SCOOP_API_KEY = match.groups()[0]
    except Exception:
        print("Did not locate Scoop API Key.")
