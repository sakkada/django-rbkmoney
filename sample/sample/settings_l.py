import os, sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__)))
DB_SQLITE_PATH = os.path.abspath(os.path.join(PROJECT_ROOT, 'sqlite.db'))
sys.path.insert(0, PROJECT_ROOT)

# django settings
DEBUG = True
TEMPLATE_DEBUG = DEBUG

LANGUAGE_CODE = 'ru-RU'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': DB_SQLITE_PATH,
    }
}

INSTALLED_APPS = (
    'django.contrib.sites',
    'rbkmoney',
    'orderapp',
)

# rbkmoney settings
RBKMONEY_SHOP_ID = 000001
RBKMONEY_SECRET_KEY = '5#+*(8k$q#q58(+#g)&$)hhv1ezo#75j(aobnqfgwsx&bf%l7-'
RBKMONEY_HASH_CHECK = 'MD5'