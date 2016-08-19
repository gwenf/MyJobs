from default_settings import *

DEBUG = True

ABSOLUTE_URL = "/"

PROJECT = 'myjobs'
ENVIRONMENT = 'Jenkins'

DATABASES = {
    'default': {
        'NAME': 'redirect',
        'ENGINE': 'django.db.backends.mysql',
        'USER': 'root',
        'PASSWORD': 'P@ssW0rd',
        'HOST': '',
        'PORT': '3306',
    },
    'qc-redirect': {
        'NAME': 'qcredirect',
        'ENGINE': 'django.db.backends.mysql',
        'USER': 'root',
        'PASSWORD': 'P@ssW0rd',
        'HOST': '',
        'PORT': '3306',
    },
    'archive': {
        'NAME': 'qcredirect',
        'ENGINE': 'django.db.backends.mysql',
        'USER': 'root',
        'PASSWORD': 'P@ssW0rd',
        'HOST': '',
        'PORT': '3306',
    },
}
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}
SESSION_ENGINE = 'django.contrib.sessions.backends.db'

PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.MD5PasswordHasher',
)
JENKINS_TEST_RUNNER = 'silent_testrunner.SilentTestRunner'
CELERY_ALWAYS_EAGER = True

CC_AUTH = TESTING_CC_AUTH

ALLOWED_HOSTS = ['*', ]

ROOT_URLCONF = 'myjobs_urls'

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'seo.search_backend.DESolrEngine',
        'URL': 'http://127.0.0.1:8983/solr/seo',
        'HTTP_AUTH_USERNAME': SOLR_AUTH['username'],
        'HTTP_AUTH_PASSWORD': SOLR_AUTH['password'],
    },
    'groups': {
        'ENGINE': 'saved_search.groupsearch.SolrGrpEngine',
        'URL': 'http://127.0.0.1:8983/solr/seo',
        'HTTP_AUTH_USERNAME': SOLR_AUTH['username'],
        'HTTP_AUTH_PASSWORD': SOLR_AUTH['password'],
    },
}

TEMPLATE_CONTEXT_PROCESSORS += (
    'mymessages.context_processors.message_lists',
)


LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'standard': {
            'format': "[%(asctime)s] %(levelname)s "
                      "[%(name)s:%(lineno)s] %(message)s",
            'datefmt': "%d/%b/%Y %H:%M:%S"
        },
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
    },
    'loggers': {
        '': {
            'handlers': ['null'],
            'propagate': True,
            'level': 'WARN',
        }
    }
}

SOLR = {
    # seo_test would be better...
    'seo_test': 'http://127.0.0.1:8983/solr/seo',
}
