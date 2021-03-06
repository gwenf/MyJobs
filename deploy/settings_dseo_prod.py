import datetime
from S3 import CallingFormat

from default_settings import *
from secrets import SOLR_AUTH, REDIRECT_PROD, ARCHIVE_PROD, REDIRECT_QC

COMPRESS_ENABLED = True
COMPRESS_OFFLINE_MANIFEST = 'manifest.json'
STATIC_URL = "//d2e48ltfsb5exy.cloudfront.net/content_ms/files/"

ALLOWED_HOSTS = ['*', ]

DATABASES = {
    'default': dict({
        'NAME': 'redirect',
        'ENGINE': 'django.db.backends.mysql',
        'HOST': 'db-redirect.c9shuxvtcmer.us-east-1.rds.amazonaws.com',
        'PORT': '3306',
    }, **REDIRECT_PROD),
    'qc-redirect': dict({
        'NAME': 'redirect',
        'ENGINE': 'django.db.backends.mysql',
        'HOST': 'db-redirectqc.c9shuxvtcmer.us-east-1.rds.amazonaws.com',
        'PORT': '3306',
    }, **REDIRECT_QC),
    'archive': dict({
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'redirect',
        'HOST': 'db-redirectarchive.c9shuxvtcmer.us-east-1.rds.amazonaws.com',
        'PORT': '3306',
    }, **ARCHIVE_PROD)
}

SESSION_CACHE_ALIAS = 'sessions'
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        # Set version number to date that this file was last modified
        # This should update the cache key on deployments and ensure any servers
        # deployed to on the same day will have matching keys. This won't clear
        # the cache for multiple deployments per day.
        'VERSION': str(datetime.date.fromtimestamp(os.path.getmtime(__file__))),
        'LOCATION': [
            'prod-microsites.qksjst.0001.use1.cache.amazonaws.com:11211',
            'prod-microsites.qksjst.0002.use1.cache.amazonaws.com:11211',
            'prod-microsites.qksjst.0003.use1.cache.amazonaws.com:11211',
            'prod-microsites.qksjst.0004.use1.cache.amazonaws.com:11211'
        ]
    },
    'sessions': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': [
            'dseomj-mc-cluster.qksjst.0001.use1.cache.amazonaws.com:11211',
            'dseomj-mc-cluster.qksjst.0002.use1.cache.amazonaws.com:11211',
            'dseomj-mc-cluster.qksjst.0003.use1.cache.amazonaws.com:11211',
            'dseomj-mc-cluster.qksjst.0004.use1.cache.amazonaws.com:11211',
            'dseomj-mc-cluster.qksjst.0005.use1.cache.amazonaws.com:11211',
            'dseomj-mc-cluster.qksjst.0006.use1.cache.amazonaws.com:11211',
        ]
    },
    'blocks': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'VERSION': str(datetime.date.fromtimestamp(os.path.getmtime(__file__))),
        'LOCATION': [
            'blocks.qksjst.0001.use1.cache.amazonaws.com:11211',
            'blocks.qksjst.0002.use1.cache.amazonaws.com:11211',
        ]
    }
}

# Add newrelic here since it shouldn't be used on non-production servers
NEW_RELIC_TRACKING = True
MIDDLEWARE_CLASSES = MIDDLEWARE_CLASSES + ('middleware.NewRelic',)

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'seo.search_backend.DESolrEngine',
        # 'solr_server' must be defined in /etc/hosts on the server where this
        # code is deployed. Check the deployment project in
        # direct_seo/web/conf/hosts and make sure the one in production looks
        # like that.
        'URL': 'http://solr_server:8983/solr/seo',
        'TIMEOUT': 300,
        'HTTP_AUTH_USERNAME': SOLR_AUTH['username'],
        'HTTP_AUTH_PASSWORD': SOLR_AUTH['password']
    },
    'groups': {
        'ENGINE': 'saved_search.groupsearch.SolrGrpEngine',
        'URL': 'http://solr_server:8983/solr/seo',
        'TIMEOUT': 300,
        'HTTP_AUTH_USERNAME': SOLR_AUTH['username'],
        'HTTP_AUTH_PASSWORD': SOLR_AUTH['password']
    }
}

AWS_STORAGE_BUCKET_NAME = 'src-nlx-org'
AWS_CALLING_FORMAT = CallingFormat.SUBDOMAIN
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'

ROOT_URLCONF = 'dseo_urls'
MIDDLEWARE_CLASSES += (
    'wildcard.middleware.WildcardMiddleware',
    'middleware.RedirectOverrideMiddleware',
)
TEMPLATE_CONTEXT_PROCESSORS += (
    "social_links.context_processors.social_links_context",
    "seo.context_processors.site_config_context",
)

ABSOLUTE_URL = 'https://secure.my.jobs/'

PROJECT = "dseo"


BROKER_HOST = '204.236.236.123'
BROKER_PORT = 5672
BROKER_USER = 'celery'
BROKER_VHOST = 'dseo-vhost'

CELERY_DEFAULT_EXCHANGE = 'tasks'
CELERY_DEFAULT_EXCHANGE_TYPE = 'topic'
CELERY_DEFAULT_ROUTING_KEY = 'dseo.default'

EMAIL_HOST_USER = PRODUCTION_EMAIL_HOST_USER
EMAIL_HOST_PASSWORD = PRODUCTION_EMAIL_HOST_PASSWORD

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
