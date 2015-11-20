import os.path
from contextlib import contextmanager

from django.conf import settings
from django.core.cache import cache
from django.core.urlresolvers import clear_url_caches
from django.db import connections
from django.test import TransactionTestCase
from django.test.client import Client
from django.template import context

from import_jobs import DATA_DIR
from saved_search.groupsearch import SolrGrpEngine, SolrGroupSearchBackend
from seo.search_backend import DESolrSearchBackend, DESolrEngine
from seo.tests.factories import BusinessUnitFactory
from seo.tests.factories import SeoSiteFactory, ConfigurationFactory
from seo_pysolr import Solr
import solr_settings


class TestDESolrSearchBackend(DESolrSearchBackend):
    def search(self, *args, **kwargs):
        counter = getattr(settings, 'SOLR_QUERY_COUNTER', 0)
        settings.SOLR_QUERY_COUNTER = counter + 1
        return super(TestDESolrSearchBackend, self).search(*args, **kwargs)


class TestDESolrEngine(DESolrEngine):
    backend = TestDESolrSearchBackend


class TestSolrGrpSearchBackend(SolrGroupSearchBackend):
    def search(self, *args, **kwargs):
        counter = getattr(settings, 'SOLR_QUERY_COUNTER', 0)
        settings.SOLR_QUERY_COUNTER = counter + 1
        return super(TestDESolrSearchBackend, self).search(*args, **kwargs)


class TestSolrGrpEngine(SolrGrpEngine):
    backend = TestSolrGrpSearchBackend


class DirectSEOBase(TransactionTestCase):
    urls = 'dseo_urls'

    def setUp(self):
        db_backend = settings.DATABASES['default']['ENGINE'].split('.')[-1]

        # Set columns that are utf8 in production to utf8
        if db_backend == 'mysql':
            cursor = connections['default'].cursor()
            cursor.execute("alter table seo_customfacet convert to character "
                           "set utf8 collate utf8_unicode_ci")
            cursor.execute("alter table seo_seositefacet convert to character "
                           "set utf8 collate utf8_unicode_ci")
            cursor.execute("alter table seo_company convert to character set "
                           "utf8 collate utf8_unicode_ci")
            cursor.execute("alter table seo_queryredirect convert to character "
                           "set utf8 collate utf8_unicode_ci")
            cursor.execute("alter table taggit_tag convert to character set "
                           "utf8 collate utf8_unicode_ci")
            cursor.execute("alter table taggit_taggeditem convert to "
                           "character set "
                           "utf8 collate utf8_unicode_ci")
            cursor.execute("alter table seo_seositeredirect convert to "
                           "character set utf8 collate utf8_unicode_ci")
            cursor.execute("alter table django_redirect convert to "
                           "character set utf8 collate utf8_unicode_ci")

        #setattr(settings, 'ROOT_URLCONF', 'dseo_urls')
        setattr(settings, "PROJECT", 'dseo')
        clear_url_caches()

        self.base_middleware_classes = settings.MIDDLEWARE_CLASSES
        middleware_classes = self.base_middleware_classes + (
            'wildcard.middleware.WildcardMiddleware',
            'middleware.RedirectOverrideMiddleware')
        setattr(settings, 'MIDDLEWARE_CLASSES', middleware_classes)

        self.base_context_processors = settings.TEMPLATE_CONTEXT_PROCESSORS
        context_processors = self.base_context_processors + (
            "social_links.context_processors.social_links_context",
            "seo.context_processors.site_config_context",
        )
        setattr(settings, 'TEMPLATE_CONTEXT_PROCESSORS', context_processors)
        context._standard_context_processors = None

        self.conn = Solr('http://127.0.0.1:8983/solr/seo')
        self.conn.delete(q="*:*")
        cache.clear()
        clear_url_caches()

        setattr(settings, 'MEMOIZE', False)

    def tearDown(self):
        from django.conf import settings
        from django.template import context

        setattr(settings, 'TEMPLATE_CONTEXT_PROCESSORS',
                self.base_context_processors)
        context._standard_context_processors = None
        setattr(settings, 'MIDDLEWARE_CLASSES',
                self.base_middleware_classes)


class DirectSEOTestCase(DirectSEOBase):
    def setUp(self):
        super(DirectSEOTestCase, self).setUp()
        self.solr_docs = solr_settings.SOLR_FIXTURE
        self.conn.add(self.solr_docs)

        # uids and numjobs in feed file for test business unit 0
        self.feed_uids = [57621597, 57311147, 60351047, 59891656, 58867671,
                          57495178, 59773973, 59326433, 57311143, 57311166]
        self.feed_numjobs = 14

        self.businessunit = BusinessUnitFactory(id=0)
        self.buid_id = self.businessunit.id
        # Ensure DATA_DIR used by import_jobs.download_feed_file exists
        data_path = DATA_DIR
        if not os.path.exists(data_path):
            os.mkdir(data_path)

    def tearDown(self):
        super(DirectSEOTestCase, self).tearDown()
        self.conn.delete(q="*:*")
        self.assertEqual(self.conn.search(q='*:*').hits, 0)


class DirectSeoTCWithSiteAndConfig(DirectSEOTestCase):
    """
        Test case with a job added and site configured
        Attributes:
            site - test seosite instance
            config - config for test seosite
            client - same as default client, but uses test seosite's domain as HTTP_HOST
    """
    def setUp(self):
        super(DirectSeoTCWithSiteAndConfig, self).setUp()
        self.site = SeoSiteFactory()
        self.site.business_units.add(self.businessunit)

        self.config = ConfigurationFactory.build(status=2)
        self.config.save()

        self.site.configurations.add(self.config)

        # ensure tests in this class use the correct domain
        self.client = Client(HTTP_HOST=self.site.domain)


class SettingDoesNotExist:
    pass


@contextmanager
def patch_settings(**kwargs):
    from django.conf import settings
    old_settings = []
    for key, new_value in kwargs.items():
        old_value = getattr(settings, key, SettingDoesNotExist)
        old_settings.append((key, old_value))
        setattr(settings, key, new_value)
    yield

    for key, old_value in old_settings:
        if old_value is SettingDoesNotExist:
            delattr(settings, key)
        else:
            setattr(settings, key, old_value)
