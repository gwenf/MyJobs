import json

from django.test.client import RequestFactory
from django.conf import settings
from django.core.urlresolvers import reverse

from mysearches.models import SavedSearch

from mysearches.views import (get_value_from_request,
                              add_or_activate_saved_search,
                              user_creation_retrieval)

from mysearches.tests.factories import SavedSearchFactory


from myblocks.tests.test_secure_blocks import (make_cors_request,
                                               make_jsonp_request)
from myjobs.tests.setup import MyJobsBase
from myjobs.tests.factories import UserFactory

class SecureSavedSearchHelpersTestCase(MyJobsBase):
    """
    Test cases for the helper functions of secure saved search API
    (currently used by secure blocks saved search widget)

    """

    def test_add_or_activate_function_adds_search(self):
        """
        Test to ensure the add_or_activate_saved_search function adds a search
        when provided a user and an valid URL of a search that user does not
        have

        """
        count_user_searches = SavedSearch.objects.filter(user=self.user).count()
        self.assertEqual(count_user_searches, 0,
                         msg="Expected 0 searches for user, got %s! Searches"
                             " existed before test" % count_user_searches)
        add_or_activate_saved_search(self.user, 'http://www.my.jobs/')
        count_user_searches = SavedSearch.objects.filter(
            user=self.user).count()
        self.assertEqual(count_user_searches, 1,
                         msg="Expected 1 search, got %s! Search may not have"
                             "been created." % count_user_searches)

    def test_add_or_activate_function_activates_search(self):
        """
        Test to ensure the add_or_activate_saved_search function adds a search
        when provided a user and an valid URL of a search that user has and is
        inactive

        """
        new_ss = SavedSearchFactory(user=self.user, is_active=False)
        self.assertEqual(new_ss.is_active, False,
                         msg="New search was active. Factory did not set"
                             " it to inactive!")
        count_user_searches = SavedSearch.objects.filter(user=self.user).count()
        self.assertEqual(count_user_searches, 1,
                         msg="Expected 1 searches for user, got %s! Factory may"
                             " not have created search" % count_user_searches)
        saved_search = add_or_activate_saved_search(self.user, new_ss.url)
        ss_reload = SavedSearch.objects.get()
        self.assertEqual(new_ss, ss_reload,
                         msg="There was a problem reloading saved search from"
                             "the database. Original and reload do not match!")
        self.assertEqual(ss_reload.is_active, True,
                         msg="Reloaded search was inactive! Function did not"
                             " activate it!")

    def test_add_or_activate_function_invalid_url(self):
        """
        Test to ensure the add_or_activate_saved_search function raises
        the proper exception if an invalid url is provided

        """
        count_user_searches = SavedSearch.objects.filter(user=self.user).count()
        self.assertEqual(count_user_searches, 0,
                         msg="Expected 0 searches for user, got %s! Searches"
                             " existed before test" % count_user_searches)
        with self.assertRaises(ValueError, msg="ValueError not raised despite "
                                               "invalid url provided!"):
            saved_search = add_or_activate_saved_search(self.user,
                                                        'http://www.google.com/')
        count_user_searches = SavedSearch.objects.filter(user=self.user).count()
        self.assertEqual(count_user_searches, 0,
                         msg="Expected 0 searches, got %s! Search may have"
                             " been created." % count_user_searches)

    def test_add_or_activate_function_no_url(self):
        """
        Test to ensure the add_or_activate_saved_search function raises
        proper exception if no url is provided

        """
        count_user_searches = SavedSearch.objects.filter( user=self.user).count()
        self.assertEqual(count_user_searches, 0,
                         msg="Expected 0 searches for user, got %s! Searches"
                             " existed before test" % count_user_searches)

        with self.assertRaises(ValueError, msg="ValueError not raised despite "
                                               "invalid url provided!"):
            saved_search = add_or_activate_saved_search(self.user, '')

        count_user_searches = SavedSearch.objects.filter(user=self.user).count()
        self.assertEqual(count_user_searches, 0,
                         msg="Expected 0 searches, got %s! Search may have"
                             " been created." % count_user_searches)

    def test_request_function_retrieves_post_value(self):
        """
        Test to ensure that get_value_from_request retrieves a value when
        given a key in the POST values

        """
        rf = RequestFactory()
        post_request = rf.post('/saved-search/api/secure-saved-search',
                               {'hello':'kitty'})
        kitty = get_value_from_request(post_request, 'hello')
        self.assertEqual(kitty, 'kitty', msg="Expected kitty, got %s!"
                                             "Post value was not "
                                             "retrieved." % kitty)


    def test_request_function_retrieves_get_value(self):
        """
        Test to ensure that get_value_from_request retrieves a value when
        given a key in the GET values

        """
        rf = RequestFactory()
        get_request = rf.get('/saved-search/api/secure-saved-search',
                               {'hello':'kitty'})
        kitty = get_value_from_request(get_request, 'hello')
        self.assertEqual(kitty, 'kitty', msg="Expected kitty, got %s!"
                                             "Get value was not "
                                             "retrieved." % kitty)

    def test_request_function_retrieves_body_value(self):
        """
        Test to ensure that get_value_from_request retrieves a value when
        given a key in the body values (JSON formatted)

        """
        rf = RequestFactory()
        post_data = json.dumps({'hello':'kitty'})
        post_request = rf.post('/saved-search/api/secure-saved-search',
                               post_data,
                               content_type='application/json')
        self.assertEqual(post_data, post_request.body,
                         msg="Expected %s, got %s! Post body did "
                             "not match provided data, request"
                             "was malformed!" % (post_data, post_request.body))
        kitty = get_value_from_request(post_request, 'hello')
        self.assertEqual(kitty, 'kitty', msg="Expected kitty, got %s!"
                                             "Post value was not "
                                             "retrieved." % kitty)

    def test_request_function_returns_none_if_key_doesnt_exist(self):
        """
        Test to ensure that get_value_from_request retrieves a key isn't in
        body, POST or GET

        """
        rf = RequestFactory()
        get_request = rf.get('/saved-search/api/secure-saved-search',
                               {'goodbye':'kitty'})
        kitty = get_value_from_request(get_request, 'hello')
        self.assertIsNone(kitty, msg="Expected None, got %s! A value was"
                                     "retrieved." % kitty)

    def test_return_user_if_exists_and_is_logged_in(self):
        """
        Verifies that if the email provided belongs to the authenticated user,
        that user's account is returned from user_creation_retrieval

        """
        user_account, created = user_creation_retrieval(self.user,
                                                        self.user.email)
        self.assertFalse(created)
        self.assertEqual(self.user, user_account,
                         msg="User retrieved did not match authenticated"
                             " user.")

    def test_return_user_if_email_not_taken(self):
        """
        Verifies that if an unused email is provided, a user is created for
        that user and it is returned by user_creation_retrieval

        """
        user_account, created = user_creation_retrieval(self.user,
                                                        "notsame@email.com")
        self.assertTrue(created)
        self.assertNotEqual(self.user, user_account,
                         msg="Original user was retrieved. Should have created"
                             " a new user.")

    def test_raise_error_if_email_is_already_taken(self):
        """
        Verifies that if the email provided belongs to a user that is not
        signed in, an error is raised from user_creation_retrieval

        """
        UserFactory(email="anotheruser@email.com")
        with self.assertRaises(ValueError, msg="ValueError should have raised!"
                                               " Email provided was in use."):
           user_creation_retrieval(self.user, "anotheruser@email.com")

    def test_user_retrieved_parameters_required(self):
        """
        Verifies that user_creation_retrieval only works if both auth user and
        email are provided to user_creation_retrieval

        """
        with self.assertRaises(ValueError,
                               msg="Error not thrown when email empty"):
            user_creation_retrieval(self.user, "")

        with self.assertRaises(ValueError,
                               msg="Error not thrown when user is none"):
            user_creation_retrieval(None, "test@email.com")


class SecureSavedSearchAPITestCase(MyJobsBase):
    """
    Test cases for the main API functions of the secure saved search API
    (currently used by secure blocks saved search widget)

    """

    def setUp(self):
        super(SecureSavedSearchAPITestCase, self).setUp()
        self.domain = settings.SITE.domain
        self.child_url = 'http://wwww.my.jobs/'
        self.secure_ss_url = reverse('secure_saved_search')

    def test_api_works_with_authenticated_user(self):
        """
        Verifies that the secure saved searched API works properly with
        authenticated users when a valid, unclaimed email is provided

        """
        request_data = {'email':self.user.email,
                        'url': self.child_url}
        response = make_cors_request(self.client,
                                     self.secure_ss_url,
                                     json.dumps(request_data),
                                     http_origin="http://%s" % self.domain)
        response_msg = json.loads(response.content)
        self.assertFalse(response_msg['error'],
                         msg="Expected empty string, got %s! API returned "
                             "error" % response_msg['error'])
        self.assertTrue(response_msg['search_activated'])

    def test_api_returns_error_if_email_is_taken(self):
        """
        Verifies that the secure saved searched API returns an error if the
        provided email is taken by another user

        """
        taken_email = 'takenemail@email.com'
        UserFactory(email=taken_email)
        request_data = {'email':taken_email,
                        'url': self.child_url}
        response = make_cors_request(self.client,
                                     self.secure_ss_url,
                                     json.dumps(request_data),
                                     http_origin="http://%s" % self.domain)
        response_msg = json.loads(response.content)
        self.assertTrue(response_msg['error'],
                         msg="Expected an error but none raised! API returned"
                             ": %s" % response_msg['error'])
        self.assertFalse(response_msg['search_activated'])

    def test_api_works_with_unauthenticated_user(self):
        """
        Verifies that the secure saved searched API works properly with
        unauthenticated users when a valid, unclaimed email is provided

        """
        self.client.logout()
        request_data = {'email':'a_new_email@email.com',
                        'url': self.child_url}
        response = make_cors_request(self.client,
                                     self.secure_ss_url,
                                     json.dumps(request_data),
                                     http_origin="http://%s" % self.domain)

        self.assertEqual(response.status_code, 200)
        response_msg = json.loads(response.content)
        self.assertTrue(response_msg['user_created'],
                         msg="Expected user to be created, but it was not")
        self.assertTrue(response_msg['search_activated'],
                         msg="Expected search to be activated, but it was not")


    def test_api_error_if_no_email_provided(self):
        """
        Verifies that the secure saved searched API returns an error when
        an unauthenticated user does not provide an email

        """
        request_data = {'email':'',
                        'url': self.child_url}
        response = make_cors_request(self.client,
                                     self.secure_ss_url,
                                     json.dumps(request_data),
                                     http_origin="http://%s" % self.domain)
        response_msg = json.loads(response.content)
        self.assertTrue(response_msg['error'],
                         msg="Expected an error, got %s! API returned"
                             ": " % response_msg['error'])
        self.assertFalse(response_msg['search_activated'])

    def test_api_error_if_no_url_provided(self):
        """
        Verifies that the secure saved searched API returns an error if a
        url is not provided.

        """
        request_data = {'email':'an_email@example.com',
                        'url': ''}
        response = make_cors_request(self.client,
                                     self.secure_ss_url,
                                     json.dumps(request_data),
                                     http_origin="http://%s" % self.domain)
        response_msg = json.loads(response.content)
        self.assertTrue(response_msg['error'],
                         msg="Expected an error, got %s! API returned"
                             ": " % response_msg['error'])
        self.assertFalse(response_msg['search_activated'])

    def test_api_works_with_jsonp(self):
        """
        All of the other tests use CORS, this test is to verify that JSONP
        is also supported

        """
        request_data = {'callback':'callmemaybe',
                        'email':'an_email@example.com',
                        'url': self.child_url}
        response = make_jsonp_request(self.client,
                                      self.secure_ss_url,
                                      request_data,
                                      http_referer="http://%s" % self.domain)
        # Direct string compare for what will be returned. Return should
        # always remain the same. Avoiding more complex string parsing.
        cmpr = ('callmemaybe({"user_created": true, "search_activated": true,'
                ' "error": ""})')
        self.assertEqual(response.content, cmpr,
                         msg="Invalid return from API call! Expected %s,"
                             "got %s" % (cmpr, response.content))
