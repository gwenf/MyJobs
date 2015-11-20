# -*- coding: utf-8 -*-# -*- coding: utf-8 -*-
import HTMLParser
import base64
import datetime
import json
import re
from urllib import unquote
import urlparse
import uuid

from jira.client import JIRA
import markdown
from testfixtures import Replacer

from django.conf import settings
from django.contrib.sites.models import Site
from django.core import mail
from django.core.cache import cache
from django.core.urlresolvers import reverse, NoReverseMatch
from django.test.client import Client, RequestFactory
from django.utils import timezone
from django.utils.http import urlquote_plus

from myjobs.tests.factories import UserFactory
from redirect.actions import sourcecodetag
from redirect.models import (DestinationManipulation, ExcludedViewSource,
                             CompanyEmail)
from redirect.tests.factories import (RedirectFactory, RedirectArchiveFactory,
                                      CanonicalMicrositeFactory,
                                      DestinationManipulationFactory,
                                      CustomExcludedViewSourceFactory,
                                      ViewSourceFactory, ViewSourceGroupFactory)
from redirect.tests.setup import RedirectBase
from redirect.views import home
from seo.tests.factories import SeoSiteFactory, SeoSiteRedirectFactory

GUID_RE = re.compile(r'([{\-}])')

JOB = {
    'guid': '2' * 32,
    'buid': 0,
    'title': 'Underwater Basket Weaver',
    'description':
    '''Qualifications:
    10+ years prior experience weaving baskets underwater
    BS/MS Underwater Basket Weaving preferable
    ''',
    'html_description':
        '''<b>Qualifications:</b><br />
        <ul><li>10+ years prior experience weaving baskets underwater</li>
        <li>BS/MS Underwater Basket Weaving preferable</li></ul>
        ''',
    'reqid': 'ubw101'
}


def mock_search(self, q=None, kwargs=None):
    """
    Helper method that mocks a solr search result
    """
    class Result(object):
        def __init__(self, job):
            self.docs = job
            self.hits = len(job)

    job = []
    if q is not None:
        q = q.split(':')
        if q[0] == 'guid' and q[1] == JOB['guid']:
            job = [JOB]

    return Result(job)


def clean_guid(guid):
    return GUID_RE.sub('', guid).upper()


class ViewSourceViewTests(RedirectBase):
    def setUp(self):
        super(ViewSourceViewTests, self).setUp()
        self.client = Client()
        self.redirect = RedirectFactory()
        self.microsite = CanonicalMicrositeFactory()
        self.manipulation = DestinationManipulationFactory()
        self.redirect_guid = clean_guid(self.redirect.guid)

        self.factory = RequestFactory()

    def tearDown(self):
        """
        The cache is not cleared between tests. We need to do it manually.
        """
        super(ViewSourceViewTests, self).tearDown()
        cache.clear()

    def test_get_with_bad_vsid(self):
        """
        If no view source id is provided or the given view source id does not
        resolve to a DestinationManipulation instance, default to 0
        """
        for vsid in ['', '1']:
            response = self.client.get(reverse('home',
                                               args=[self.redirect_guid,
                                                     vsid]))

            test_url = '%s%s/job/?vs=%s' % \
                (self.microsite.canonical_microsite_url,
                 self.redirect_guid,
                 vsid or '0')

            self.assertEqual(response['Location'], test_url)

    def test_with_action_type_2(self):
        """
        Sometimes a DestinationManipulation object exists with an action_type
        of 2 but a corresponding object with an action_type of 1 does not
        exist. If one of these is encountered, we should not run the
        manipulation twice.
        """
        self.manipulation.action_type = '2'
        self.manipulation.action = 'sourcecodetag'
        self.manipulation.value_1 = '?src=foo'
        self.manipulation.view_source = 10
        self.redirect.url = 'http://www.directemployers.org'
        self.manipulation.save()
        self.redirect.save()

        with self.assertRaises(DestinationManipulation.DoesNotExist):
            DestinationManipulation.objects.get(
                buid=self.manipulation.buid,
                view_source=self.manipulation.view_source,
                action_type=1)

        response = self.client.get(
            reverse('home',
                    args=[self.redirect_guid,
                          self.manipulation.view_source]))

        self.assertEqual(response.status_code, 301)
        self.assertEqual(response['Location'],
                         self.redirect.url + self.manipulation.value_1)

    def test_get_with_malformed_guid(self):
        """
        Navigating to a url with a malformed guid or a guid that contains
        non-hex characters should display a 404 page
        """
        for guid in [self.redirect_guid[:16],
                     'g' * 32]:
            with self.assertRaises(NoReverseMatch):
                self.client.get(reverse('home', args=[guid]))

    def test_job_does_not_exist(self):
        """
        Nonexistent jobs should display a 404 page.
        """
        response = self.client.get(reverse('home', args=['1' * 32]))
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, 'redirect/404.html')
        self.assertTrue('There was an error accessing this job'
                        in response.content)
        self.assertTrue('google-analytics' in response.content)

    def test_open_graph_redirect(self):
        """
        Check social bot open graph response
        """
        response = self.client.get(
            reverse('home', args=[self.redirect_guid,
                                  self.manipulation.view_source]),
            HTTP_USER_AGENT='facebookexternalhit')
        self.assertContains(response, 'My.jobs - Programmer - DirectEmployers')
        self.assertTemplateUsed(response, 'redirect/opengraph.html')
        self.assertTrue('google-analytics' not in response.content)

    def test_twitter_card(self):
        response = self.client.get(
            reverse('home', args=[self.redirect_guid,
                                  self.manipulation.view_source]),
            HTTP_USER_AGENT='TwitterBot')
        self.assertTemplateUsed(response, 'redirect/twitter.html')
        self.assertTrue('twitter:image:src' in response.content)

    def test_sourcecodetag_redirect(self):
        """
        Check view that manipulates a url with the sourcecodetag action
        creates the correct redirect url which will have a sourcecode tag on
        the end
        examples: &Codes=DE-DEA, &src=JB-11380, &src=indeed_test
        """
        response = self.client.get(
            reverse('home', args=[self.redirect_guid,
                                  self.manipulation.view_source]))
        test_url = '%s?%s' % (self.redirect.url,
                              self.manipulation.value_1[1:])
        self.assertEqual(response['Location'], test_url)

    def test_microsite_redirect(self):
        """
        Ensure that requests for a given GUID + view source redirect to a
        microsite given two criteria:
        - The view source is not an excluded view source
        - The buid that owns the job has a microsite enabled.
        """
        self.manipulation.action = 'sourcecodetag'
        self.manipulation.value_1 = '?src=foo'
        self.manipulation.view_source = 0
        self.manipulation.save()

        response = self.client.get(
            reverse('home', args=[self.redirect_guid,
                                  self.manipulation.view_source]))
        test_url = '%s%s/job/?vs=%s' % (self.microsite.canonical_microsite_url,
                                        self.redirect_guid,
                                        self.manipulation.view_source)
        self.assertEqual(response['Location'], test_url)

    def test_amptoamp_redirect(self):
        """
        Check method that manipulates a url with the amptoamp action
        """
        self.manipulation.action = 'amptoamp'
        self.manipulation.value_1 = 'http://ad.doubleclick.net/clk;2526;8138?'
        self.manipulation.value_2 = '&functionName=viewFromLink&locale=en-us'
        self.manipulation.save()

        self.redirect.url = 'jobsearch.lilly.com/ddddddd/job/&8888888&vs=43'
        self.redirect.save()

        response = self.client.get(
            reverse('home', args=[self.redirect_guid,
                                  self.manipulation.view_source]))
        url = self.redirect.url.split('&')
        test_url = '%s%s%s' % \
            (self.manipulation.value_1, url[1], self.manipulation.value_2)
        self.assertEqual(response['Location'], test_url)

    def test_urlswap_redirect(self):
        """
        Check method that manipulates a url with the cframe action
        """
        self.manipulation.action = 'urlswap'
        self.manipulation.value_1 = 'https://careers.nscorp.com/?sap-client=100'
        self.manipulation.save()

        response = self.client.get(
            reverse('home', args=[self.redirect_guid,
                                  self.manipulation.view_source]))
        test_url = self.manipulation.value_1
        self.assertEqual(response['Location'], test_url)

    def test_cframe_redirect(self):
        """
        Check method that manipulates a url with the cframe action
        """
        self.manipulation.action = 'cframe'
        self.manipulation.value_1 = 'fedex.asp'
        self.manipulation.save()

        response = self.client.get(
            reverse('home', args=[self.redirect_guid,
                                  self.manipulation.view_source]))
        url = urlquote_plus(self.redirect.url, safe='')
        url = url.replace('.', '%2E')
        url = url.replace('-', '%2D')
        url = url.replace('_', '%5F')
        url = '%s?url=%s' % (self.manipulation.value_1, url)
        test_url = 'http://directemployers.us.jobs/companyframe/' + url
        self.assertEqual(response['Location'], test_url)

    def test_anchorredirectissue_redirect(self):
        """
        Check method that manipulates a url with the anchorredirectissue action
        """
        self.manipulation.action = 'anchorredirectissue'
        self.manipulation.value_1 = '&deaanchor='
        self.manipulation.save()

        self.redirect.url = 'directemployers.org/#directemployers#105/'
        self.redirect.save()

        response = self.client.get(
            reverse('home', args=[self.redirect_guid,
                                  self.manipulation.view_source]))
        url = self.redirect.url.split('#')
        test_url = 'http://testserver/' + url[0] + self.manipulation.value_1
        self.assertEqual(response['Location'], test_url)

    def test_replacethenadd_redirect(self):
        """
        Check method that manipulates a url with the replacethenadd action
        """
        self.manipulation.action = 'replacethenadd'
        self.manipulation.value_1 = 'jobdetail.ftl!!!!jobapply.ftl'
        self.manipulation.value_2 = '&src=CWS-12480'
        self.manipulation.save()

        self.redirect.url = 'directemployers.org/'
        self.redirect.save()

        response = self.client.get(
            reverse('home', args=[self.redirect_guid,
                                  self.manipulation.view_source]))
        old, new = self.manipulation.value_1.split('!!!!')
        test_url = 'http://testserver/%s%s' % \
            (self.redirect.url, self.manipulation.value_2.replace('&', '?'))
        self.assertEqual(response['Location'], test_url)

    def test_replacethenaddpre_redirect(self):
        """
        Check method that manipulates a url with the replacethenaddpre action
        """
        self.manipulation.action = 'replacethenaddpre'
        self.manipulation.value_1 = '?ss=paid!!!!?apstr=src%3DJB-10600'
        self.manipulation.value_2 = 'http://ad.doubleclick.net/clk;2613;950;s?'
        self.manipulation.save()

    def test_sourcecodeinsertion_redirect(self):
        """
        Check method that manipulates a url with the sourcecodeinsertion action
        """
        self.manipulation.action = 'sourcecodeinsertion'
        self.manipulation.value_1 = '&src=de'
        self.manipulation.save()

        self.redirect.url = 'directemployers.org/#directemployers/'
        self.redirect.save()

        response = self.client.get(
            reverse('home', args=[self.redirect_guid,
                                  self.manipulation.view_source]))
        url = self.redirect.url.split('#')
        test_url = 'http://testserver/' + ('%s#' %
                                           self.manipulation.value_1).join(url)
        self.assertEqual(response['Location'], test_url)

    def test_sourceurlwrapappend_redirect(self):
        """
        Check method that manipulates a url with the sourceurlwrapappend action
        """
        self.manipulation.action = 'sourceurlwrapappend'
        self.manipulation.value_1 = 'http://bs.serving-sys.com/server.bs?u=$$'
        self.manipulation.value_2 = '$$'
        self.manipulation.save()

        response = self.client.get(
            reverse('home', args=[self.redirect_guid,
                                  self.manipulation.view_source]))
        url = urlquote_plus(self.redirect.url, safe='')
        url = url.replace('.', '%2E')
        url = url.replace('-', '%2D')
        url = url.replace('_', '%5F')
        test_url = self.manipulation.value_1 + url + self.manipulation.value_2
        self.assertEqual(response['Location'], test_url)

    def test_sourceurlwrapunencodedappend_redirect(self):
        """
        Check method that manipulates a url with the
        sourceurlwrapunencodedappend action
        """
        self.manipulation.action = 'sourceurlwrapunencodedappend'
        self.manipulation.value_1 = 'http://ad.doubleclick.net/clk;2593;886;r?'
        self.manipulation.value_2 = '&SID=97'
        self.manipulation.save()

        response = self.client.get(
            reverse('home', args=[self.redirect_guid,
                                  self.manipulation.view_source]))
        #content = json.loads(response.content)
        url = self.manipulation.value_1 + self.redirect.url
        test_url = url + self.manipulation.value_2
        self.assertEqual(response['Location'], test_url)

    def test_sourceurlwrapunencoded_redirect(self):
        """
        Check method that manipulates a url with the sourceurlwrapunencoded
        action
        """
        self.manipulation.action = 'sourceurlwrapunencoded'
        self.manipulation.value_1 = 'http://ad.doubleclick.net/clk;346;154;h?'
        self.manipulation.save()

        response = self.client.get(
            reverse('home', args=[self.redirect_guid,
                                  self.manipulation.view_source]))
        test_url = self.manipulation.value_1 + self.redirect.url
        self.assertEqual(response['Location'], test_url)

    def test_sourceurlwrap_redirect(self):
        """
        Check method that manipulates a url with the sourceurlwrap action
        """
        self.manipulation.action = 'sourceurlwrap'
        self.manipulation.value_1 = 'http://bs.serving-sys.com/?cn=t&rtu=$$'
        self.manipulation.save()

        response = self.client.get(
            reverse('home', args=[self.redirect_guid,
                                  self.manipulation.view_source]))
        url = urlquote_plus(self.redirect.url, safe='')
        url = url.replace('.', '%2E')
        url = url.replace('-', '%2D')
        url = url.replace('_', '%5F')
        test_url = self.manipulation.value_1 + url
        self.assertEqual(response['Location'], test_url)

    def test_switchlastinstance_redirect(self):
        """
        Check method that manipulates a url with the switchlastinstance action
        """
        self.manipulation.action = 'switchlastinstance'
        self.manipulation.value_1 = '/job'
        self.manipulation.value_2 = '/login'
        self.manipulation.save()

        self.redirect.url = 'directemployers.org/job'
        self.redirect.save()

        response = self.client.get(
            reverse('home', args=[self.redirect_guid,
                                  self.manipulation.view_source]))
        old = self.manipulation.value_1
        new = self.manipulation.value_2
        test_url = 'http://testserver/' + new.join(
            self.redirect.url.rsplit(old, 1))
        self.assertEqual(response['Location'], test_url)

    def test_switchlastthenadd_redirect(self):
        """
        Check method that manipulates a url with the switchlastthenadd action
        """
        self.manipulation.action = 'switchlastthenadd'
        self.manipulation.value_1 = '/job!!!!/login'
        self.manipulation.value_2 = '?iis=CareerSiteSEO'
        self.manipulation.save()

        self.redirect.url = 'directemployers.org/job'
        self.redirect.save()

        response = self.client.get(
            reverse('home', args=[self.redirect_guid,
                                  self.manipulation.view_source]))
        old, new = self.manipulation.value_1.split('!!!!')
        new_url = new.join(self.redirect.url.rsplit(old, 1))
        test_url = 'http://testserver/' + new_url + self.manipulation.value_2
        self.assertEqual(response['Location'], test_url)

    def test_state_job(self):
        self.redirect.buid = 1228
        self.redirect.url = 'http://us.jobs/viewjobs.asp?jobid=1234'
        self.redirect.job_location = 'NY-Rochester'
        self.manipulation.delete()
        self.redirect.save()
        response = self.client.get(
            reverse('home', args=[self.redirect_guid,
                                  self.manipulation.view_source]))
        self.assertTrue(self.redirect.url.replace('us.jobs', 'newyork.us.jobs')
                        in response['Location'])

    def test_expired_job(self):
        self.redirect.expired_date = datetime.datetime.now(tz=timezone.utc)
        self.redirect.save()

        response = self.client.get(
            reverse('home', args=[self.redirect_guid,
                                  self.manipulation.view_source]))
        self.assertEqual(response.status_code, 410)
        self.assertTemplateUsed(response, 'redirect/expired.html')

        content = re.sub('\s+', ' ', response.content)
        self.assertTrue('View all jobs for<br /> <b>%s</b>' %
                        self.redirect.company_name in
                        content)

        count = content.count('class="drill-search"')
        self.assertEqual(count, 3,
                         'Expected three search links, found %s' % count)
        self.assertTrue(self.redirect.url in response.content)
        self.assertTrue('google-analytics' in response.content)

    def test_expired_job_with_unicode(self):
        self.redirect.expired_date = datetime.datetime.now(tz=timezone.utc)
        self.redirect.job_title = u'это юникода'
        self.redirect.save()

        response = self.client.get(reverse('home',
                                           args=[self.redirect_guid]))
        self.assertTrue(response.status_code, 404)

    def test_cookie_domains(self):
        # The value for host is unimportant - if this code does not end up
        # being served on r.my.jobs, it's okay. We're just testing that we
        # properly retrieve the root domain from what is provided.
        for host in ['jcnlx.com', 'my.jobs', 'r.my.jobs']:
            request = self.factory.get(
                reverse('home', args=[self.redirect_guid,
                                      self.manipulation.view_source]),
                HTTP_HOST=host)
            response = home(request, self.redirect_guid,
                            self.manipulation.view_source)

            cookie = response.cookies['aguid']
            if 'my.jobs' in host:
                expected_domain = '.my.jobs'
            else:
                expected_domain = '.jcnlx.com'
            self.assertIn(('domain', expected_domain), cookie.items())
            uuid.UUID(unquote(cookie.value))

    def test_apply_click(self):
        self.apply_manipulation = DestinationManipulationFactory(
            view_source=1234)

        response = self.client.get(reverse('home',
                                           args=[self.redirect_guid]) +
                                   '?vs=%s' %
                                   self.apply_manipulation.view_source)
        self.assertEqual(response.status_code, 301)

        test_url = '%s?%s' % (self.redirect.url,
                              self.apply_manipulation.value_1[1:])

        self.assertEqual(response['Location'], test_url)

    def test_bad_vs_query(self):
        self.apply_manipulation = DestinationManipulationFactory(
            view_source=1234)

        response = self.client.get(reverse('home',
                                           args=[self.redirect_guid]) +
                                   '?vs=%sbad_vs' %
                                   self.apply_manipulation.view_source)

        self.assertTrue(response['Location'].endswith(self.redirect.url))

    def test_source_code_collision(self):
        """
        Test that we never duplicate source codes in the event of a collision

        Tests five circumstances:
        - The source code is the last entry in the query
        - The source code is somewhere in the middle
        - The source code is the first query
        - The source code is the only query
        - The new source code has a blank value
        """
        url = 'http://directemployers.jobs?%ssrc=de%s'
        for part in [('foo=bar&', ''),  # last
                     ('foo=bar&', '&code=de'),  # middle
                     ('', '&foo=bar'),  # first
                     ('', '')]:  # only
            self.redirect.url = url % part
            self.redirect.save()
            self.manipulation.value_1 = '&src=JB-DE'
            self.manipulation.save()

            response = self.client.get(
                reverse('home',
                        args=[self.redirect_guid,
                              self.manipulation.view_source]))

            self.assertTrue('src=de' not in response['Location'])
            self.assertTrue('src=JB-DE' in response['Location'])

        # New source code is blank
        self.manipulation.value_1 = '?src='
        self.manipulation.save()
        response = self.client.get(
            reverse('home',
                    args=[self.redirect_guid,
                          self.manipulation.view_source]))
        self.assertEqual(response['Location'],
                         self.redirect.url.replace('de', ''))

    def test_source_codes_ignore_case(self):
        """
        Source codes should be matched case-insensitively between what is
        already applied to a url and what we are adding. If a matching source
        code is already in place, its value should be replaced with the new
        value. If no matching source code is found, we should append the
        new one and keep its case.
        """
        old_url = self.redirect.url
        parameters = ['src', 'SRC']
        for url_param in parameters:
            self.redirect.url = '%s?%s=code' % (old_url, url_param)
            self.redirect.save()

            for manipulation_param in parameters:
                self.manipulation.value_1 = '?%s=foo' % manipulation_param
                self.manipulation.save()

                response = self.client.get(
                    reverse('home',
                            args=[self.redirect_guid,
                                  self.manipulation.view_source]))
                self.assertEqual(response['Location'],
                                 self.redirect.url.replace('code', 'foo'))

    def test_source_code_with_encoded_parameters(self):
        """
        Sometimes the value that we're adding has %-encoded values already;
        Ensure that we don't accidentally unencode or double-encode those
        values (ie %20->%2520)
        """
        self.manipulation.value_1 = '&src=with%20space'
        self.manipulation.save()

        response = self.client.get(
            reverse('home',
                    args=[self.redirect_guid,
                          self.manipulation.view_source]))

        # We ensure that there is never a & without a preceding ? - that is
        # unlikely, however
        self.assertTrue('?' + self.manipulation.value_1[1:] in
                        response['Location'])

    def test_invalid_sourcecodetag_redirect(self):
        """
        In the event that the desired source code is not present in the
        database somehow, performing a sourcecodetag redirect should result
        in that source code not being added to the final url
        """
        self.manipulation.value_1 = ''
        self.manipulation.save()

        response = self.client.get(
            reverse('home',
                    args=[self.redirect_guid,
                          self.manipulation.view_source]))

        self.assertTrue(response['Location'].endswith(self.redirect.url))

    def test_myjobs_redirects(self):
        paths = ['/terms', '/search?location=Indianapolis']
        for path in paths:
            response = self.client.get(path, follow=True)
            self.assertEqual(response.status_code, 301)
            self.assertTrue(response['Location'].startswith(
                'http://www.my.jobs'))

    def test_debug_parameter(self):
        response = self.client.get(reverse('home',
                                           args=[self.redirect_guid,
                                                 self.manipulation.view_source,
                                                 '+']))
        self.assertTrue(self.redirect.guid in response.content)
        self.assertTrue(self.redirect.url in response.content)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('google-analytics' in response.content)

    def test_redirect_on_new_job(self):
        """
        Ensure that are not done if a job was added
        within the last 30 minutes
        """
        # Make the redirect and manipulation objects look like real data
        self.redirect.new_date = datetime.datetime.now(tz=timezone.utc)
        self.redirect.url = 'http://www.directemployers.org'
        self.redirect.save()
        self.manipulation.action = 'sourcecodetag'
        self.manipulation.value_1 = '?src=foo'
        self.manipulation.view_source = 0
        self.manipulation.save()

        response = self.client.get(reverse('home',
                                           args=[self.redirect_guid]))

        # The job would normally redirect to a microsite, but it should not
        # in this instance
        self.assertFalse(response['Location'].startswith(
            self.microsite.canonical_microsite_url))
        # ... while the result of doing a sourcecodeswitch does.
        self.assertTrue(self.manipulation.value_1 in response['Location'])

        # If a job is 30 minutes old or older, the microsite result is used
        # as expected.
        self.redirect.new_date -= datetime.timedelta(minutes=30)
        self.redirect.save()
        response = self.client.get(reverse('home',
                                           args=[self.redirect_guid]))
        test_url = '%s%s/job/?vs=%s' % (self.microsite.canonical_microsite_url,
                                        self.redirect_guid,
                                        self.manipulation.view_source)
        self.assertEqual(response['Location'], test_url)

    def test_percent_encoded_url_params(self):
        """
        Ensure that query parameters retain their encoding when adding new
        parameters.
        """
        self.redirect.url = 'example.com?%c3%81=%20%3d,%2b'
        self.redirect.save()
        response = self.client.get(
            reverse('home',
                    args=[self.redirect_guid,
                          self.manipulation.view_source]))
        self.assertTrue('%c3%81=%20%3d,%2b' in response['Location'].lower())

    def test_cache_gets_set_on_view(self):
        """
        Viewing any page when the cache is empty should populate a list of
        excluded view sources
        """
        cache_key = settings.EXCLUDED_VIEW_SOURCE_CACHE_KEY
        cache.delete(cache_key)

        self.assertFalse(cache.get(cache_key))

        self.client.get(reverse('home',
                                args=[self.redirect_guid]))

        self.assertTrue(cache.get(cache_key))

    def test_cache_gets_cleared_on_save(self):
        """
        Saving an ExpiredViewSource object should remove the list of
        excluded view sources, which will be replaced on the next request
        """
        cache_key = settings.EXCLUDED_VIEW_SOURCE_CACHE_KEY
        self.client.get(reverse('home',
                                args=[self.redirect_guid]))

        new_evs = ExcludedViewSource.objects.all().order_by('-view_source')[0]
        new_evs = new_evs.view_source + 1

        self.assertFalse(new_evs in cache.get(cache_key))

        ExcludedViewSource(view_source=new_evs).save()

        self.assertFalse(cache.get(cache_key))

        self.client.get(reverse('home',
                                args=[self.redirect_guid]))

        self.assertTrue(new_evs in cache.get(cache_key))

    def test_custom_microsite_exclusion(self):
        custom_exclusion = CustomExcludedViewSourceFactory()

        response = self.client.get(
            reverse('home',
                    args=[self.redirect_guid,
                          custom_exclusion.view_source]))
        self.assertTrue((custom_exclusion.buid,
                         custom_exclusion.view_source) in
                        settings.CUSTOM_EXCLUSIONS)
        self.assertFalse(response['Location'].startswith(
            self.microsite.canonical_microsite_url))

    def test_custom_parameters(self):
        CustomExcludedViewSourceFactory(
            view_source=self.manipulation.view_source)
        response = self.client.get(
            reverse('home',
                    args=[self.redirect_guid,
                          self.manipulation.view_source]) + '?z=1&foo=bar')
        for part in [self.redirect.url,
                     'foo=bar',
                     self.manipulation.value_1[1:]]:
            self.assertTrue(part in response['Location'])

    def test_custom_parameters_on_microsite(self):
        self.manipulation.view_source = 0
        self.manipulation.save()
        response = self.client.get(
            reverse('home',
                    args=[self.redirect_guid]) + '?z=1&foo=bar')
        test_url = '%s%s/job/?vs=%s&z=1&foo=bar' % \
                   (self.microsite.canonical_microsite_url,
                    self.redirect_guid,
                    self.manipulation.view_source)
        self.assertEqual(response['Location'], test_url)

        response = self.client.get(
            reverse('home',
                    args=[self.redirect_guid]) + '?vs=0&z=1&foo=bar')
        test_url = '%s?%s&foo=bar' % (self.redirect.url,
                                      self.manipulation.value_1[1:])
        self.assertEqual(response['Location'], test_url)

    def test_custom_parameters_on_doubleclick(self):
        self.manipulation.action = 'doubleclickwrap'
        self.manipulation.value_1 = 'http://ad.doubleclick.net/clk;2613;950;s?'
        self.manipulation.save()

        response = self.client.get(
            reverse('home',
                    args=[self.redirect_guid,
                          self.manipulation.view_source]) + '?z=1&foo=bar')
        test_url = '%s%s?foo=bar' % (self.manipulation.value_1,
                                     self.redirect.url)
        self.assertEqual(response['Location'], test_url)

    def test_custom_parameters_on_feed_redirect(self):
        site = Site.objects.create(domain='google.com',
                                   name='Google')
        response = self.client.get(
            reverse('home',
                    args=[self.redirect_guid,
                          '20']) + '?z=1&foo=bar&my.jobs.site.id=%d' % site.pk)
        parts = urlparse.urlparse(response['Location'])
        self.assertEqual(parts.netloc, site.domain)

        query = urlparse.parse_qs(parts.query)
        for param in {'z': ['1'], 'foo': ['bar'],
                      'vs': ['20']}.items():
            self.assertEqual(query[param[0]], param[1])

        # When redirecting from a feed and using custom parameters, we create
        # the potential for a redirect loop. Ensure that isn't happening.
        self.assertRaises(KeyError, lambda: query['my.jobs.site.id'])

    def test_source_codes_with_hit_key(self):
        self.manipulation.action = 'replacethenadd'
        self.manipulation.value_1 = '/job!!!!/apply'
        self.manipulation.value_2 = '&src=foo'
        self.manipulation.save()

        self.redirect.url = 'http://www.directemployers.org/job#hit-key'
        self.redirect.save()

        expected = '/apply?src=bar#hit-key'
        response = self.client.get(
            reverse('home',
                    args=[self.redirect_guid,
                          self.manipulation.view_source]) + '?z=1&src=bar')
        self.assertTrue(response['Location'].endswith(expected))

    def test_bad_query_value(self):
        """
        A few replacethenadd instances were found that had blank values
        for the "add" portion. They have been fixed, but we should ensure that
        this doesn't 500 in the event that more are added.
        """
        self.manipulation.action = 'replacethenadd'
        self.manipulation.value_1 = '/jobdetail.ftl!!!!/jobapply.ftl'
        self.manipulation.value_2 = ''
        self.manipulation.save()

        self.redirect.url = 'http://directemployers.org/jobdetail.ftl'
        self.redirect.save()

        response = self.client.get(
            reverse('home',
                    args=[self.redirect_guid,
                          self.manipulation.view_source]))
        self.assertTrue(response['Location'].endswith('/jobapply.ftl'))
        self.assertFalse('/jobdetail.ftl' in response['Location'])

    def test_syndication_redirect_site_exists(self):
        """
        Ensures that we appropriately redirect to the proper microsite if we are
        provided one that differs from what is defined for a given BUID.
        """
        site = Site.objects.create(domain='google.com',
                                   name='Google')
        response = self.client.get(
            reverse('home',
                    args=[self.redirect_guid,
                          self.manipulation.view_source]) +
            '?my.jobs.site.id=%s' % site.pk)

        expected = 'http://%s/%s/job/?vs=%s' % (site.domain, self.redirect_guid,
                                                self.manipulation.view_source)
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response['Location'], expected)

    def test_syndication_redirect_no_site(self):
        """
        If my.jobs.site.id is provided but does not reference a site, do
        manipulations as if it was not provided.
        """
        site = Site.objects.create(domain='google.com',
                                   name='Google')
        response = self.client.get(
            reverse('home',
                    args=[self.redirect_guid,
                          self.manipulation.view_source]) +
            '?my.jobs.site.id=%s' % (site.pk + 1))

        self.assertEqual(response.status_code, 301)
        self.assertEqual(response['Location'], sourcecodetag(self.redirect,
                                                             self.manipulation))

    def test_msccn_redirect(self):
        response = self.client.get(
            reverse('home',
                    args=[self.redirect_guid,
                          '1604']))
        expected = 'http://us.jobs/msccn-referral.asp?gi=%s%s&cp=%s' % (
            self.redirect_guid, '1604', self.redirect.company_name)
        self.assertEqual(response['Location'], expected)

    def test_default_google_analytics(self):
        vs = ViewSourceFactory(include_ga_params=True)
        group = ViewSourceGroupFactory(view_sources=[vs])

        response = self.client.get(
            reverse('home',
                    args=[self.redirect_guid,
                          vs.view_source_id]))
        expected = 'http://www.my.jobs/{guid}/job/?vs={vs}' \
                   '&utm_source={source}-DE&utm_medium={group}' \
                   '&utm_campaign={source}'.format(
                       guid=self.redirect_guid, vs=vs.view_source_id,
                       source=vs.name, group=group.name).replace(' ', '%20')

        self.assertEqual(expected, response['Location'])

    def test_syndication_redirect_with_analytics(self):
        """
        Analytics parameters should be added to syndication redirects.
        """
        vs = ViewSourceFactory(include_ga_params=True)
        group = ViewSourceGroupFactory(view_sources=[vs])
        site = Site.objects.create(domain='google.com', name='google')
        response = self.client.get(
            reverse('home',
                    args=[self.redirect_guid,
                          vs.view_source_id]) +
            '?my.jobs.site.id=%s' % site.pk)
        location = unquote(response['Location'])
        self.assertTrue(location.startswith('http://%s' % site.domain))
        for query in ['&utm_source=%s-DE' % vs.name,
                      '&utm_medium=%s' % group.name,
                      '&utm_campaign=%s' % vs.name]:
            self.assertTrue(query in location)

    def test_syndication_redirect_with_analytics_and_override(self):
        """
        Syndication redirects should include any source code overrides that
        have been added.
        """
        vs = ViewSourceFactory(include_ga_params=True,
                               view_source_id=self.manipulation.view_source)
        group = ViewSourceGroupFactory(view_sources=[vs])
        site = Site.objects.create(domain='google.com', name='google')
        response = self.client.get(
            reverse('home',
                    args=[self.redirect_guid,
                          vs.view_source_id]) +
            '?my.jobs.site.id=%s&z=1&utm_source=test' % site.pk)
        location = unquote(response['Location'])
        self.assertTrue(location.startswith('http://%s' % site.domain))
        for query in ['&utm_source=test',
                      '&utm_medium=%s' % group.name,
                      '&utm_campaign=%s' % vs.name,
                      '&z=1']:
            self.assertTrue(query in location)


class EmailForwardTests(RedirectBase):
    def setUp(self):
        super(EmailForwardTests, self).setUp()
        self.redirect_guid = JOB['guid']
        self.redirect = RedirectFactory(buid=JOB['buid'],
                                        guid='{%s}' %
                                             uuid.UUID(self.redirect_guid))

        self.password = 'secret'
        self.user = UserFactory(email='accounts@my.jobs')
        self.user.set_password(self.password)
        self.user.save()

        self.contact = CompanyEmail.objects.create(
            buid=self.redirect.buid,
            email=self.user.email)

        self.email = self.user.email.replace('@', '%40')
        self.auth = {
            'bad': [
                '',
                'Basic %s' % base64.b64encode('bad%40email:wrong_pass')],
            'good':
                'Basic %s' % base64.b64encode('%s:%s' % (self.user.email.\
                                                         replace('@', '%40'),
                                                         self.password))}
        self.post_dict = {'to': 'to@example.com',
                          'from': 'from@example.com',
                          'text': 'Questions about stuff',
                          'html': '<b>Questions about stuff</b>',
                          'subject': 'Bad Email',
                          'attachments': 0}

        self.r = Replacer()
        self.r.replace('pysolr.Solr.search', mock_search)

    def tearDown(self):
        super(EmailForwardTests, self).tearDown()
        self.r.restore()

    def submit_email(self, use_data=True):
        """
        Helper method for submitting parsed emails. Ensures that the request
        returns a status of 200.

        Inputs:
        :use_data: Should we include post data; Default: True

        Outputs:
        :response: HttpResponse from email redirect view
        """
        auth = self.auth.get('good')
        kwargs = {'HTTP_AUTHORIZATION': auth}
        if use_data:
            kwargs['data'] = self.post_dict
        response = self.client.post(reverse('email_redirect'),
                                    **kwargs)
        self.assertEqual(response.status_code, 200)

        return response

    def assert_guid_email_responses_are_correct(self,
                                                redirect,
                                                job=None):
        """
        Helper method for validating parsed guid@my.jobs emails.

        Inputs:
        :redirect: Redirect instance to use if a job is old
        :job: Solr result for a new job
        """
        email = mail.outbox.pop(0)
        self.assertEqual(email.from_email,
                         settings.DEFAULT_FROM_EMAIL)
        self.assertEqual(email.to, [self.post_dict['from']])
        self.assertEqual(email.subject, self.post_dict['subject'])

        # Emails turn lots of characters into HTML entities. Results from
        # Solr and the database do not. Unescape the email body so we can
        # compare the two.
        parser = HTMLParser.HTMLParser()
        body = parser.unescape(email.body)
        if job is not None:
            self.assertTrue(markdown.markdown(job['description']) in body)
        else:
            self.assertTrue(redirect.job_title in body)

    def test_jira_login(self):
        jira = JIRA(options=settings.options,
                    basic_auth=settings.my_agent_auth)
        self.assertIsNotNone(jira)

    def test_bad_authorization(self):
        for auth in self.auth.get('bad'):
            kwargs = {}
            if auth:
                # auth_value has a value, so we can pass an HTTP_AUTHORIZATION
                #    header
                kwargs['HTTP_AUTHORIZATION'] = auth
            response = self.client.post(reverse('email_redirect'),
                                        **kwargs)
            self.assertTrue(response.status_code, 403)

    def test_good_authorization(self):
        self.submit_email(use_data=False)

    def test_bad_email(self):
        self.submit_email()

        self.assertEqual(len(mail.outbox), 0)

    def test_bad_guid_email(self):
        """
        Sending a compliance email to a nonexistant job results in an error
        response.
        """
        self.post_dict['to'] = '%s@my.jobs' % ('1'*32)
        self.post_dict['text'] = 'This address is not in the database'

        self.submit_email()

        email = mail.outbox.pop()
        self.assertEqual(email.subject, 'Email forward failure')
        self.assertTrue('There is no job associated with this address'
                        in email.body)

    def test_good_guid_email_new_job(self):
        """
        When info is requested for a new job, we can grab its doc from solr.
        This lets us provide the job's ReqID and description instead of just
        a title.
        """
        self.post_dict['to'] = ['%s@my.jobs' % self.redirect_guid]
        self.post_dict['subject'] = 'Email forward success'

        self.submit_email()
        self.assert_guid_email_responses_are_correct(self.redirect, JOB)
        email = mail.outbox.pop()
        # email.alternatives is a list of sets as follows:
        # [('html body', 'text/html')]
        alternatives = dict((part[1], part[0]) for part in email.alternatives)
        self.assertTrue(JOB['html_description'] in alternatives['text/html'])
        self.assertTrue(email.subject.startswith('[ReqID: %s]' % JOB['reqid']))

    def test_good_guid_email_new_job_no_user(self):
        """
        If no entry exists in the CompanyEmail table for a given buid, we
        tell the user that everything was successful to prevent leakage of info.
        """
        self.contact.delete()

        self.post_dict['to'] = ['%s@my.jobs' % self.redirect_guid]
        self.post_dict['subject'] = 'Email forward success'

        self.submit_email()
        self.assert_guid_email_responses_are_correct(self.redirect, JOB)

    def test_guid_email_with_cc(self):
        """
        The ideal path for GUID emails sends two emails per request, one to
        the original sender to denote that we received the request and one
        to the job owner. If anyone has been CC'd, we should also CC them on
        the company contact email but not the acknowledgement of receipt.
        """
        self.post_dict['to'] = ['%s@my.jobs' % self.redirect_guid]
        self.post_dict['subject'] = 'Email forward success'
        self.post_dict['cc'] = ['comprep@company.org']
        self.submit_email()

        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(mail.outbox[0].to, [self.post_dict['from']])
        self.assertNotEqual(mail.outbox[0].cc, self.post_dict['cc'])

        self.assertEqual(mail.outbox[1].to, [self.contact.email])
        self.assertEqual(mail.outbox[1].cc, self.post_dict['cc'])

    def test_good_guid_email_old_job(self):
        """
        Requesting info for an expired job is functional but we don't keep all
        info on a job around forever. Thus we can only provide basic information
        on the job in question.
        """
        guid = '1'*32
        redirect = RedirectFactory(guid='{%s}' % uuid.UUID(guid),
                                   buid=self.redirect.buid,
                                   uid=1)
        self.post_dict['to'] = ['%s@my.jobs' % guid]
        self.post_dict['subject'] = 'Email forward success'

        self.submit_email()
        self.assert_guid_email_responses_are_correct(redirect)

        email = mail.outbox.pop()
        self.assertTrue('This job (%s) has expired.' % (
            redirect.job_title, ) in email.body)
        self.assertTrue(email.subject.startswith('[ReqID: Expired]'))

    def test_good_guid_email_old_job_no_user(self):
        self.contact.delete()

        guid = '1'*32
        redirect = RedirectFactory(guid='{%s}' % uuid.UUID(guid),
                                   buid=self.redirect.buid,
                                   uid=1)
        self.post_dict['to'] = ['%s@my.jobs' % guid]
        self.post_dict['subject'] = 'Email forward success'

        self.submit_email()
        self.assert_guid_email_responses_are_correct(redirect)

    def test_email_with_name(self):
        self.post_dict['to'] = 'User <%s@my.jobs>' % self.redirect_guid
        self.post_dict['subject'] = 'Email forward success'

        self.submit_email()

        email = mail.outbox.pop()

    def test_no_emails(self):
        self.post_dict.pop('to')

        self.submit_email()

        self.assertEqual(len(mail.outbox), 0)

    def test_too_many_emails(self):
        self.post_dict['to'] = 'test@example.com, foo@mail.my.jobs'

        self.submit_email()

        self.assertEqual(len(mail.outbox), 0)

    def test_prm_email(self):
        """
        If prm@my.jobs is included as a recipient, we repost this email to
        My.jobs. This is a straight post, which we don't want to do in a
        testing environment. If we receive a 200 status code and no emails
        were sent, this was reasonably likely to have completed successfully.
        """
        prm_list = ['prm@my.jobs', 'PRM@MY.JOBS']

        for email in prm_list:
            # SendGrid adds prm@my.jobs to the 'envelope' JSON string
            # if it appears as a BCC
            self.post_dict['envelope'] = '{"to":["%s"]}' % email

            response = self.submit_email()
            self.assertEqual(response.content, 'reposted')
            self.assertEqual(len(mail.outbox), 0)

        del self.post_dict['envelope']

        for email in prm_list:
            self.post_dict['to'] = email

            response = self.submit_email()
            self.assertEqual(response.content, 'reposted')
            self.assertEqual(len(mail.outbox), 0)


class UpdateBUIDTests(RedirectBase):
    def setUp(self):
        super(UpdateBUIDTests, self).setUp()
        self.key = settings.BUID_API_KEY
        self.cm = CanonicalMicrositeFactory(buid=1)
        self.dm = DestinationManipulationFactory(buid=1)

    def test_key(self):
        resp = self.client.get(reverse('update_buid'))
        self.assertEqual(resp.status_code, 401)

        bad_key = '12345'
        resp = self.client.get(reverse('update_buid') + '?key=%s' % bad_key)
        self.assertEqual(resp.status_code, 401)

        resp = self.client.get(reverse('update_buid') + '?key=%s' % self.key)
        self.assertEqual(resp.content,
                         '{"error": "Invalid format for old business unit"}')

    def test_no_new_buid(self):
        resp = self.client.get(reverse('update_buid') + '?key=%s&old_buid=%s' %
                               (self.key, self.cm.buid))
        self.assertEqual(resp.content,
                         '{"error": "Invalid format for new business unit"}')

    def test_existing_buid(self):
        resp = self.client.get(reverse('update_buid') +
                               '?key=%s&old_buid=%s&new_buid=%s' %
                               (self.key, self.cm.buid, self.cm.buid))
        self.assertEqual(resp.content,
                         '{"error": "New business unit already exists"}')

    def test_no_old_buid(self):
        resp = self.client.get(reverse('update_buid') + '?key=%s&new_buid=%s' %
                               (self.key, self.cm.buid + 1))
        self.assertEqual(resp.content,
                         '{"error": "Invalid format for old business unit"}')

    def test_new_buid(self):
        resp = self.client.get(reverse('update_buid') +
                               '?key=%s&old_buid=%s&new_buid=%s' %
                               (self.key, self.cm.buid, self.cm.buid + 1))
        content = json.loads(resp.content)
        self.assertEqual(content['new_bu'], self.cm.buid + 1)
        self.assertEqual(content['updated'], 2)


class RedirectViewTests(RedirectBase):
    def test_get_redirect(self):
        redirect = RedirectFactory(guid='{%s}' % uuid.uuid4())
        expired_redirect = RedirectArchiveFactory(guid='{%s}' % uuid.uuid4())

        # Follow a redirect in the Redirect table.
        guid = clean_guid(redirect.guid)
        response = self.client.get(reverse('home', args=[guid]), follow=True)
        self.assertEqual(response.status_code, 301)

        # Follow a redirect in the RedirectArchive table.
        guid = clean_guid(expired_redirect.guid)
        response = self.client.get(reverse('home', args=[guid]), follow=True)
        self.assertEqual(response.status_code, 410)

        # Don't follow a bad redirect.
        response = self.client.get(reverse('home', args=['1'*32]), follow=True)
        self.assertEqual(response.status_code, 404)

    def test_unnecessary_middleware_isnt_used(self):
        """
        At one point, we were using the same middleware as seo. This caused
        issues as SiteRedirectMiddleware does a 301 redirect that we don't
        need. Ensure this doesn't happen.
        """
        site = SeoSiteFactory(domain='www.my.jobs')
        guid = uuid.uuid4()
        redirect = RedirectFactory(guid='{%s}' % guid)
        guid = guid.hex
        ssr = SeoSiteRedirectFactory(seosite=site, redirect_url='my.jobs')

        path = reverse('home', args=[guid, '', '+'])
        response = self.client.get(path,
                                   HTTP_HOST='my.jobs', follow=True)
        self.assertEqual(response['Location'],
                         'http://my.jobs' + path.replace('%2B', '+'))
        self.assertEqual(response.status_code, 301)
