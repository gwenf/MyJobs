from importlib import import_module
from mock import patch

from django.conf import settings
from django.contrib.auth import login
from django.core.cache import cache
from django.core.urlresolvers import clear_url_caches, reverse
from django.http import HttpRequest
from django.test import TestCase
from django.test.client import Client, MULTIPART_CONTENT
from myjobs.decorators import MissingActivity
from myjobs.tests.factories import (AppAccessFactory, RoleFactory, UserFactory,
                                    ActivityFactory)
from myjobs.tests.helpers import return_file
from seo.models import SeoSite
from seo.tests.factories import CompanyFactory
from seo_pysolr import Solr


class TestClient(Client):
    """
    Custom test client that decouples testing from the authentication bits, as
    well as reduces boilerplate when sending requests.
    """

    def __init__(self, enforce_csrf_checks=False, path=None,
                 data=None, **defaults):
        """
        In addition to Django's test client, this method also takes an optional
        path and data attribute to be used for get and post requests.
        """
        self.path = path
        self.data = data or {}
        super(TestClient, self).__init__(enforce_csrf_checks, **defaults)

    def get(self, path=None, data=None, follow=False, secure=False, **extra):
        """
        Like the builtin get method, but uses the instances path and data when
        available.
        """
        path = path or self.path

        if not path:
            raise TypeError("get expects a path. None given. Either "
                            "instantiate TestClient with a default path or be "
                            "sure that the first argument to get is a valid "
                            "path.")
        data = data or self.data

        return super(TestClient, self).get(
            path, data=data, follow=follow, secure=secure, **extra)

    def post(self, path=None, data=None, content_type=MULTIPART_CONTENT,
             secure=False, **extra):
        path = path or self.path
        data = data or self.data

        return super(TestClient, self).post(
            path, data=data, content_type=content_type,
            secure=secure, **extra)

    def login_user(self, user):
        if 'django.contrib.sessions' not in settings.INSTALLED_APPS:
            raise AssertionError("Unable to login without "
                                 "django.contrib.sessions in INSTALLED_APPS")
        user.backend = "%s.%s" % ("django.contrib.auth.backends",
                                  "ModelBackend")
        engine = import_module(settings.SESSION_ENGINE)

        # Create a fake request to store login details.
        request = HttpRequest()
        if self.session:
            request.session = self.session
        else:
            request.session = engine.SessionStore()
        login(request, user)

        # Set the cookie to represent the session.
        session_cookie = settings.SESSION_COOKIE_NAME
        self.cookies[session_cookie] = request.session.session_key
        cookie_data = {
            'max-age': None,
            'path': '/',
            'domain': settings.SESSION_COOKIE_DOMAIN,
            'secure': settings.SESSION_COOKIE_SECURE or None,
            'expires': None,
        }
        self.cookies[session_cookie].update(cookie_data)

        # Save the session values.
        request.session.save()


class MyJobsBase(TestCase):
    def setUp(self):
        settings.ROOT_URLCONF = "myjobs_urls"
        settings.PROJECT = "myjobs"

        self.app_access = AppAccessFactory()
        self.activities = [
            ActivityFactory(name=activity, app_access=self.app_access)
            for activity in [
                "create communication record", "create contact",
                "create partner saved search", "create partner", "create role",
                "create tag", "create user", "delete tag", "delete partner",
                "delete role", "delete user", "read contact",
                "read communication record", "read partner saved search",
                "read partner", "read role", "read user", "read tag",
                "update communication record", "update contact",
                "update partner", "update role", "update tag", "update user",
                "read outreach email address", "create outreach email address",
                "delete outreach email address",
                "update outreach email address", "read outreach record",
                "convert outreach record"]]

        self.company = CompanyFactory(app_access=[self.app_access])
        # this role will be populated by activities on a test-by-test basis
        self.role = RoleFactory(company=self.company, name="Admin")
        self.user = UserFactory(roles=[self.role], is_staff=True)

        cache.clear()
        clear_url_caches()
        self.ms_solr = Solr(settings.SOLR['seo_test'])
        self.ms_solr.delete(q='*:*')

        self.base_context_processors = settings.TEMPLATE_CONTEXT_PROCESSORS
        context_processors = self.base_context_processors + (
            'mymessages.context_processors.message_lists',
        )
        setattr(settings, 'TEMPLATE_CONTEXT_PROCESSORS', context_processors)
        setattr(settings, 'MEMOIZE', False)

        self.patcher = patch('urllib2.urlopen', return_file())
        self.mock_urlopen = self.patcher.start()

        self.client = TestClient()
        self.client.login_user(self.user)

    def tearDown(self):
        self.ms_solr.delete(q='*:*')
        setattr(settings, 'TEMPLATE_CONTEXT_PROCESSORS',
                self.base_context_processors)
        try:
            self.patcher.stop()
        except RuntimeError:
            # patcher was stopped in a test
            pass

    def assertRequires(self, view_name, *activities, **kwargs):
        """
        Asserts that the given view is only accessible when a user has a role
        with the given activities.

        """
        url = reverse(view_name, kwargs=kwargs.get('kwargs'))
        method = kwargs.get("method", "get").lower()

        response = getattr(self.client, method)(path=url)
        self.assertEqual(type(response), MissingActivity)

        self.role.activities = [activity for activity in self.activities
                                if activity.name in activities]

        response = getattr(self.client, method)(path=url)
        self.assertNotEqual(type(response), MissingActivity)

        self.role.activities.clear()
