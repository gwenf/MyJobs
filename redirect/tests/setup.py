import os
import sys

from django.core.management import call_command
from django.core.urlresolvers import clear_url_caches
from django.db import connections
from django.test import TransactionTestCase
from django.conf import settings

import redirect_settings
import secrets


class RedirectBase(TransactionTestCase):
    def setUp(self):
        super(RedirectBase, self).setUp()
        self._middleware_classes = settings.MIDDLEWARE_CLASSES
        self._template_context = settings.TEMPLATE_CONTEXT_PROCESSORS
        self._default_solr = getattr(settings, 'SOLR', None)

        # Set some settings that don't get set when not using redirect
        # settings.
        settings.ROOT_URLCONF = 'redirect_urls'
        settings.PROJECT = 'redirect'
        settings.MIDDLEWARE_CLASSES = redirect_settings.MIDDLEWARE_CLASSES
        settings.TEMPLATE_CONTEXT_PROCESSORS = (
            redirect_settings.TEMPLATE_CONTEXT_PROCESSORS)
        settings.SOLR = {'default': 'http://127.0.0.1:8983/solr/seo/'}
        settings.options = secrets.options
        settings.my_agent_auth = secrets.my_agent_auth
        clear_url_caches()

        stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')
        fixture = os.path.join(settings.PROJECT_PATH,
                               'redirect/migrations/excluded_view_sources.json')
        try:
            # This makes lots of output that we don't care about; suppress it.
            call_command("loaddata",
                         fixture)
        finally:
            sys.stdout.close()
            sys.stdout = stdout

        default_backend, archive_backend = (
            settings.DATABASES['default']['ENGINE'].split('.')[-1],
            settings.DATABASES['archive']['ENGINE'].split('.')[-1],
        )
        for backend, db in [(default_backend, 'default'),
                            (archive_backend, 'archive')]:
            if backend == 'mysql':
                cursor = connections[db].cursor()
                cursor.execute('alter table redirect_redirect convert to '
                               'character set utf8 collate utf8_unicode_ci')
                cursor.execute('alter table redirect_redirectarchive '
                               'convert to character set utf8 collate '
                               'utf8_unicode_ci')

    def tearDown(self):
        super(RedirectBase, self).tearDown()
        settings.MIDDLEWARE_CLASSES = self._middleware_classes
        settings.TEMPLATE_CONTEXT_PROCESSORS = self._template_context
        if self._default_solr:
            settings.SOLR = self._default_solr
