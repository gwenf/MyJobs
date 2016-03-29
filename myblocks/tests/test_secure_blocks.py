import json

from django.core.urlresolvers import reverse


from seo.tests.setup import DirectSEOBase
from seo.tests.factories import SeoSiteFactory, UserFactory
from myjobs.tests.test_views import TestClient
from myblocks.models import SavedSearchWidgetBlock, ToolsWidgetBlock

class TestSecureBlocks(DirectSEOBase):
    """
    Tests that the secure blocks api view in various circumstances.
    """
    fixtures = ['login_page.json']

    def setUp(self):
        super(TestSecureBlocks, self).setUp()
        self.staff_user = UserFactory(is_staff=True)
        self.client = TestClient()
        self.client.login_user(self.staff_user)
        self.sb_url = reverse('secure_blocks')
        SeoSiteFactory(domain='jobs.example.com')

    def test_secure_blocks_empty(self):
        """Browser asks for no blocks."""
        resp = make_cors_request(self.client, self.sb_url, '{"blocks": {}}')
        self.assertEqual(200, resp.status_code)
        result = json.loads(resp.content)
        self.assertEqual({}, result,
                         msg="got %s! secure block returned block when none was"
                             " requested" % result)

    def test_secure_blocks_bad_parse(self):
        """Handle unparseable JSON."""
        resp = make_cors_request(self.client, self.sb_url, '@@@@@@@@@')
        self.assertEqual(400, resp.status_code,
                         msg="got %s! block request allowed unparseable json, check"
                             " secure block json parser" % resp.status_code)

    def test_secure_blocks_render(self):
        """Ask for a real block."""
        body = '{"blocks": {"my-jobs-logo-1": {}}}'
        resp = make_cors_request(self.client, self.sb_url, body)
        result = json.loads(resp.content)
        self.assertTrue('my-jobs-logo-1' in result,
                        msg="block request not found in response. check fixture, "
                            "secure blocks logic")

    def test_secure_blocks_bad_origin(self):
        """Check that secure blocks do not load from invalid origins"""
        body = '{"blocks": {"my-jobs-logo-1": {}}}'
        resp = make_cors_request(self.client, self.sb_url, body,
                               http_origin='http://notparent.com/')
        self.assertEqual(resp.status_code, 404,
                         msg="got %s! secure block call responded despite bad origin."
                             " check cross site verify logic" % resp.status_code)

    def test_saved_search_includes_required_js(self):
        """
        Ensure requests for saved search widget includes required js

        """
        savedsearch = (SavedSearchWidgetBlock
                       .objects
                       .get(element_id='test_saved_search'))
        body = '{"blocks": {"test_saved_search": {}}}'
        resp = make_cors_request(self.client, self.sb_url, body)
        self.assertEqual(resp.status_code, 200,
                         msg="Expected 200, got %s. User was not able to "
                             "retrieve blocks for test" % resp.status_code)
        for js in savedsearch.required_js():
            self.assertContains(resp, js,
                                msg_prefix="Did not find %s in response,"
                                           "missing required js" % js)

    def test_topbar_includes_cookies(self):
        body = '{"blocks": {"test_tools_widget": {}}}'
        resp = make_cors_request(self.client, self.sb_url, body)
        self.assertEqual(resp.status_code, 200,
                         msg="Expected 200, got %s. User was not able to "
                             "retrieve blocks for test" % resp.status_code)
        self.assertEqual(resp.cookies['lastmicrosite'].value,
                         'http://jobs.example.com')

def make_cors_request(client, url, json_data,
                      http_origin='http://jobs.example.com'):
    """
    Encapsulate details of getting through CSRF protection, etc. Make CORS
    request

    """
    return client.post(
        url, json_data,
        HTTP_HOST='jobs.example.com',
        HTTP_ORIGIN=http_origin,
        HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        content_type="application/json",
    )

def make_jsonp_request(client, url, json_data,
                       http_referer='http://jobs.example.com'):
    """
    Encapsulate details of getting through CSRF protection, etc. Make CORS
    request

    """
    return client.get(
        url, json_data,
        HTTP_HOST='jobs.example.com',
        content_type="application/javascript",
        HTTP_REFERER=http_referer
    )
