import hashlib
import logging
from slugify import slugify
from urlparse import urlparse

from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.contenttypes.models import ContentType
from django.core import cache
from django.core.cache import InvalidCacheBackendError
from django.core.urlresolvers import reverse
from django.db import models
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import redirect
from django.template import Context, Template, RequestContext
from django.template.loaders.filesystem import Loader
from django.utils.safestring import mark_safe

from myblocks import context_tools
from myblocks.context_tools import get_site_config
from myblocks.helpers import success_url
from myjobs.helpers import expire_login
from myjobs.models import User
from mysearches.models import SavedSearch
from redirect.helpers import redirect_if_new
from registration.forms import CustomAuthForm, RegistrationForm
from seo import helpers
from universal.accessibility import DOCTYPE_CHOICES, LANGUAGE_CODES_CHOICES

logger = logging.getLogger(__name__)


# Attempt to use a secondary cache for blocks. This
# allows us to monitor and clear the block cache apart
# from session and page caching.
try:
    blocks_cache = cache.get_cache('blocks')
except InvalidCacheBackendError:
    blocks_cache = cache.get_cache('default')


def templatetag_library():
    """
    Supplies any templatetags necessary for page rendering.

    """
    templatetags = (['{% load seo_extras %}', '{% load i18n %}',
                    '{% load highlight %}', '{% load humanize %}', ])
    return mark_safe(' '.join(templatetags))


def raw_base_head(obj):
    """
    Gets the base head template for an object if one exists.

    :param obj: A myblocks object.
    :return: If the object has a base_head attribute, a string
             containing the base_head template. Otherwise a blank string.
    """
    if obj.base_head:
        loader = Loader()
        return loader.load_template_source(obj.base_head)[0]
    return ''


def raw_base_template(obj):
    """
    Gets the base body template for an object.

    :param obj: A myblocks object with a valid base_template.
    :return: The base_template as a string.
    """
    loader = Loader()
    return loader.load_template_source(obj.base_template)[0]


class Block(models.Model):
    """
    Base class for all individual block objects. Stores information for
    rendering the block.

    """
    base_template = None
    base_head = None

    content_type = models.ForeignKey(ContentType, editable=False)
    element_id = models.CharField(max_length=255, null=True)
    name = models.CharField(max_length=255)
    offset = models.PositiveIntegerField()
    span = models.PositiveIntegerField()
    template = models.TextField()
    head = models.TextField(blank=True)

    updated = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.name

    def _get_real_type(self):
        return ContentType.objects.get_for_model(type(self))

    def bootstrap_classes(self):
        offset = "col-md-offset-%s" % self.offset if self.offset else ''
        span = "col-md-%s" % self.span if self.span else ''
        return " ".join([offset, span])

    def block_size(self):
        return self.offset + self.span

    @context_tools.Memoized
    def cast(self):
        """
        Casts the block to the appropriate subclass.

        """
        return self.content_type.get_object_for_this_type(pk=self.pk)

    def context(self, request, **kwargs):
        """
        Provides the context required to render a block. In most
        cases this should be overriden in the subclass.

        """
        return {}

    def get_template(self):
        """
        Provides the final template for a block.

        """
        return '<div class="block-%s %s">%s</div>' % (self.id,
                                                      self.bootstrap_classes(),
                                                      self.template)

    def render_for_ajax(raw_self, request, params):
        """
        render the block template to be returned as a response to ajax call
        :param raw_self: self before being cast to proper subclass
        :param request: ajax request
        :param params: keyword parameters
        :return: template rendered for ajax

        """
        self = raw_self.cast()
        context = self.context(request, **params)
        full_template = templatetag_library() + self.template
        template = Template(full_template)
        rendered_template = template.render(RequestContext(request, context))
        return rendered_template

    def required_js(self):
        """
        Provides any javascript required by a block. In most cases
        this will be overriden by the subclass.

        """
        return []

    def get_cookies(self, request, **kwargs):
        """
        Retrieve information for setting cookies for block, if exists. To be
        overwritten by child class

        """
        return {}

    def save(self, *args, **kwargs):
        if not self.id:
            # Set content_type so the object can later be cast back to
            # its subclass.
            self.content_type = self._get_real_type()
        super(Block, self).save(*args, **kwargs)


class ApplyLinkBlock(Block):
    base_template = 'myblocks/blocks/applylink.html'

    def context(self, request, **kwargs):
        job_id = kwargs.get('job_id', '')
        return {
            'requested_job': context_tools.get_job(request, job_id),
        }


class BreadboxBlock(Block):
    base_template = 'myblocks/blocks/breadbox.html'

    def context(self, request, **kwargs):
        return {
            'breadbox': context_tools.get_breadbox(request)
        }


class ColumnBlock(Block):
    base_template = None

    blocks = models.ManyToManyField('Block', through='ColumnBlockOrder',
                                    related_name='included_blocks')

    @context_tools.Memoized
    def context(self, request, **kwargs):
        context = {}
        for block in self.blocks.all():
            context.update(block.cast().context(request, **kwargs))
        return context

    @context_tools.Memoized
    def get_template(self):
        """
        Combines all the templates for each block in the ColumnBlock
        in the order specified by the matching ColumnBlockOrder.
        Each block is wrapped in a row div.

        """

        blocks = []
        for block in self.blocks.all().order_by('columnblockorder__order'):
            blocks.append('<div class="row">%s</div>'
                          % block.cast().get_template())

        return '<div class="block-%s %s">%s</div>' % (self.id,
                                                      self.bootstrap_classes(),
                                                      ''.join(blocks))

    @context_tools.Memoized
    def required_js(self):
        """
        Combines and de-duplicates any javascript required by the
        blocks in the ColumnBlock.

        """
        js = []
        for block in self.blocks.all():
            js += block.cast().required_js()
        return list(set(js))


class ContentBlock(Block):
    base_template = 'myblocks/blocks/content.html'


class FacetBlurbBlock(Block):
    base_template = 'myblocks/blocks/facetblurb.html'

    def context(self, request, **kwargs):
        return {
            'facet_blurb_facet': context_tools.get_facet_blurb_facet(request)
        }


class JobDetailBlock(Block):
    base_template = 'myblocks/blocks/jobdetail.html'

    def context(self, request, **kwargs):
        job_id = kwargs.get('job_id', '')

        return {
            'site_commitments_string': context_tools.get_site_commitments_string(request),
            'requested_job': context_tools.get_job(request, job_id),
        }


class JobDetailBreadboxBlock(Block):
    base_template = 'myblocks/blocks/jobdetailbreadbox.html'

    def context(self, request, *args, **kwargs):
        job_id = kwargs.get('job_id', '')
        breadcrumbs = context_tools.get_job_detail_breadbox(request, job_id)
        return {
            'job_detail_breadcrumbs': breadcrumbs
        }


class JobDetailHeaderBlock(Block):
    base_template = 'myblocks/blocks/jobdetailheader.html'

    def context(self, request, **kwargs):
        job_id = kwargs.get('job_id', '')

        return {
            'requested_job': context_tools.get_job(request, job_id),
        }


class LoginBlock(Block):
    """
    Specialized block containing logic for use login functions

    """
    base_template = 'myblocks/blocks/login.html'

    def context(self, request, **kwargs):
        querystring = "?%s" % request.META.get('QUERY_STRING')
        if request.POST and self.submit_btn_name() in request.POST:
            # If data is being posted to this specific block, give the form
            # the opportunity to render any errors.
            return {
                'login_action': querystring,
                'login_form': CustomAuthForm(data=request.POST),
                'login_submit_btn_name': self.submit_btn_name()
            }
        return {
            'login_action': querystring,
            'login_form': CustomAuthForm(),
            'login_submit_btn_name': self.submit_btn_name()
        }

    def handle_post(self, request):
        """
        Logs a user in if it was a request to log a user in and
        the login attempt was successful.

        """
        # Confirm that the requst is a post, and that this form is
        # the intended recipient of the posted data.
        if not request.POST or self.submit_btn_name() not in request.POST:
            return None

        form = CustomAuthForm(data=request.POST)
        if form.is_valid():
            # Log in the user and redirect based on the success_url rules.
            expire_login(request, form.get_user())

            response = HttpResponseRedirect(success_url(request))
            response.set_cookie('myguid', form.get_user().user_guid,
                                expires=365*24*60*60, domain='.my.jobs')
            return response
        return None

    def submit_btn_name(self):
        return 'login-%s' % self.id


class MoreButtonBlock(Block):
    base_template = 'myblocks/blocks/morebutton.html'

    def context(self, request, **kwargs):
        return {
            'arranged_jobs': context_tools.get_arranged_jobs(request),
            'data_type': '',
            'num_default_jobs': len(context_tools.get_default_jobs(request)),
            'num_featured_jobs': len(context_tools.get_featured_jobs(request)),
            'site_config': context_tools.get_site_config(request),
        }

    def required_js(self):
        return ['%spager.164-21.js' % settings.STATIC_URL]


class RegistrationBlock(Block):
    base_template = 'myblocks/blocks/registration.html'

    def context(self, request, **kwargs):
        querystring = "?%s" % request.META.get('QUERY_STRING')
        if request.POST and self.submit_btn_name() in request.POST:
            # If data is being posted to this specific block, give the form
            # the opportunity to render any errors.
            return {
                'registration_action': querystring,
                'query_string': querystring,
                'registration_form': RegistrationForm(request.POST,
                                                      auto_id=False),
                'registration_submit_btn_name': self.submit_btn_name(),
            }
        return {
            'registration_action': querystring,
            'registration_form': RegistrationForm(),
            'registration_submit_btn_name': self.submit_btn_name(),
        }

    def handle_post(self, request):
        """
        Registers a user if it was a request to register a user
        and the registration form was correctly completed.

        """
        # Confirm that the requst is a post, and that this form is
        # the intended recipient of the posted data.
        if not request.POST or self.submit_btn_name() not in request.POST:
            return None
        form = RegistrationForm(request.POST, auto_id=False)
        if form.is_valid():
            # Create a user, log them in, and redirect based on the
            # success_url rules.
            user, created = User.objects.create_user(request=request,
                                                     send_email=True,
                                                     **form.cleaned_data)
            user_cache = authenticate(
                username=form.cleaned_data['email'],
                password=form.cleaned_data['password1'])
            expire_login(request, user_cache)

            response = HttpResponseRedirect(success_url(request))
            response.set_cookie('myguid', user.user_guid, expires=365*24*60*60,
                                domain='.my.jobs')
            return response
        return None

    def submit_btn_name(self):
        return 'registration-%s' % self.id


class SecureBlock(Block):
    """
    Custom abstract base class for secure blocks retrieved through ajax.
    Required JS are bundled into the template

    """

    def context(self, request, **kwargs):
        """
        Setup context of secure block by appending any kwargs to context
        dict.

        :param request:
        :param kwargs: jQuery Data attributes provided from calling site
        :return: kwargs dict to serve as context dictionary

        """
        return kwargs

    def render_for_ajax(self, request, params):
        """
        Render template then append all required js tags (if applicable)

        """
        rendered_template = super(SecureBlock,
                                  self).render_for_ajax(request,
                                                        params)
        static_string = '<script src="%s"></script>'
        required_js = [static_string % js for js in self.required_js()]
        return '%s %s' % (rendered_template, ''.join(required_js))

    class Meta:
        abstract = True


class ToolsWidgetBlock(SecureBlock):
    """
    This widget is used to display account and navigation related links via
    the secure blocks API. It is based on the topbar functionality, but will
    represent a more flexible and customizable approach.

    """
    # temporarily use the current topbar template
    base_template = 'includes/topbar.html'

    def context(self, request, **kwargs):
        """
        Add additional context variables to those passed in from the ajax call.

        """
        context = super(ToolsWidgetBlock, self).context(request, **kwargs)
        user = request.user if request.user.is_authenticated() else None

        if not user:
            # Ensure that old myguid cookies can be handled correctly
            guid = request.COOKIES.get('myguid', '').replace('-', '')
            try:
                user = User.objects.get(user_guid=guid)
            except User.DoesNotExist:
               pass

        caller = self.get_caller_info(request, **kwargs)
        microsite_name = kwargs.get('site_name', caller)
        context['user'] = user
        context['current_microsite_name'] = microsite_name
        context['current_microsite_url'] = caller
        return context

    def get_caller_info(self, request, **kwargs):
        """
        Get site info for caller site

        """
        caller = None
        if request.META.get('HTTP_ORIGIN'):
            caller = request.META.get('HTTP_ORIGIN')
        elif request.META.get('HTTP_REFERER'):
            parsed_url =  urlparse(request.META.get('HTTP_REFERER'))
            caller = "%s://%s" % (parsed_url.scheme, parsed_url.netloc)
        return caller

    def get_cookies(self, request, **kwargs):
        """
        Set cookies for last microsite and lastmicrositename

        """
        cookies = []
        caller = self.get_caller_info(request, **kwargs)
        if caller:
            max_age = 30 * 24 * 60 * 60
            last_name = kwargs.get('site_name', caller)
            cookies.append({'key':'lastmicrosite',
                            'value':caller,
                            'max_age':max_age,
                            'domain':'.my.jobs'})
            cookies.append({'key':'lastmicrositename',
                            'value':last_name,
                            'max_age':max_age,
                            'domain':'.my.jobs'})
        return cookies


class SavedSearchWidgetBlock(SecureBlock):
    """
    What is rendered is based heavily on whether or not the
    user is signed in to an account. Block renders as a customizable saved
    search module.

    """
    base_template = 'myblocks/blocks/secure_blocks/savedsearch.html'

    def context(self, request, **kwargs):
        """
        Add additional context variables to those passed in from the ajax call.
        User object and search object added, if available

        """
        context = super(SavedSearchWidgetBlock, self).context(request, **kwargs)
        saved_search_url = request.META.get('HTTP_REFERER', None)
        search = None
        user = request.user if request.user.is_authenticated() else None

        if user and saved_search_url:
            search = (SavedSearch.objects
                      .filter(user=user,
                              url=saved_search_url)
                      .first())

        context.update({
            'user': user,
            'search': search,
        })
        return context

    def required_js(self):
        """
        Return a list of all required javascript in URL format

        """
        return ['%ssecure-blocks/sb-saved-search.js' % settings.STATIC_URL]


class SavedSearchesListWidgetBlock(SecureBlock):
    """
    Widget for displaying users 5 most recent saved searches. If there are
    more than five, a link back to the saved search page is provided.

    """
    base_template = 'myblocks/blocks/secure_blocks/savedsearchlist.html'

    def context(self, request, **kwargs):
        saved_searches_url = request.build_absolute_uri(reverse('saved_search_main'))
        user = request.user if request.user.is_authenticated() else None
        saved_searches = SavedSearch.objects.none()
        if user:
            saved_searches = (SavedSearch.objects
                              .filter(user=user)
                              .order_by('-created_on'))

        return {
            'user':  user,
            'saved_searches': saved_searches,
            'saved_searches_view_url': saved_searches_url
        }


class SearchBoxBlock(Block):
    base_template = 'myblocks/blocks/searchbox.html'

    def context(self, request, **kwargs):
        return {
            'location_term': context_tools.get_location_term(request, **kwargs),
            'moc_term': context_tools.get_moc_term(request),
            'moc_id_term': context_tools.get_moc_id_term(request),
            'search_url': context_tools.get_search_url(request),
            'site_config': context_tools.get_site_config(request),
            'title_term': context_tools.get_title_term(request),
            'total_jobs_count': context_tools.get_total_jobs_count(request),
        }


class SearchFilterBlock(Block):
    base_template = 'myblocks/blocks/searchfilter.html'

    def context(self, request, **kwargs):
        return {
            'widgets': context_tools.get_widgets(request)
        }

    def required_js(self):
        return ['%spager.163-24.js' % settings.STATIC_URL]


class SearchResultBlock(Block):
    base_template = 'myblocks/blocks/searchresult.html'
    base_head = 'myblocks/head/searchresult.html'

    def context(self, request, **kwargs):
        return {
            'arranged_jobs': context_tools.get_arranged_jobs(request),
            'data_type': '',
            'default_jobs': context_tools.get_default_jobs(request),
            'featured_jobs': context_tools.get_featured_jobs(request),
            'location_term': context_tools.get_location_term(request),
            'moc_term': context_tools.get_moc_term(request),
            'query_string': context_tools.get_query_string(request),
            'results_heading': context_tools.get_results_heading(request),
            'site_commitments_string': context_tools.get_site_commitments_string(request),
            'site_config': context_tools.get_site_config(request),
            'site_tags': settings.SITE_TAGS,
            'title_term': context_tools.get_title_term(request),
        }

    def render_for_ajax(self, request, **kwargs):
        """
        Gets the template for a SearchResultBlock and renders it.
        Results are cached in the blocks_cache using render_cache_prefix
        as the cache key.

        """
        key = self.render_cache_prefix(request)
        rendered_template = blocks_cache.get(key)
        if rendered_template:
            return rendered_template
        context = self.context(request, **kwargs)
        template = Template("%s %s" % (templatetag_library(), self.template))
        rendered_template = template.render(RequestContext(request, context))
        blocks_cache.set(key, rendered_template, settings.MINUTES_TO_CACHE*60)
        return rendered_template

    def render_cache_prefix(self, request):
        """
        Combines the current domain, the SearchResultBlock, the current path,
        the current query string, the current site configuration,
        and all business units for the current site into a
        single string and then hashes it.

        This can be used as a cache key for a Page. It will be change any
        time any block, row, page, or configuration is updated.

        """
        domain = None
        if request.user.is_authenticated() and request.user.is_staff:
            domain = request.REQUEST.get('domain')
        if domain is None:
            domain = request.get_host()

        block = '%s::%s' % (self.pk, self.updated)
        path = request.path
        query_string = context_tools.get_query_string(request)
        config = context_tools.get_site_config(request)
        config = '%s::%s' % (config.pk, config.revision)
        buids = [str(buid) for buid in getattr(settings, 'SITE_BUIDS', [])]
        buids = '#'.join(buids)
        key = '###'.join([block, path, query_string, config,
                          buids, domain]).encode('utf-8')
        return hashlib.sha1(key).hexdigest()


class SearchResultHeaderBlock(Block):
    base_template = 'myblocks/blocks/searchresultsheader.html'

    def context(self, request, **kwargs):
        return {
            'arranged_jobs': context_tools.get_arranged_jobs(request),
            'results_heading': context_tools.get_results_heading(request),
            'default_jobs': context_tools.get_default_jobs(request),
            'featured_jobs': context_tools.get_featured_jobs(request),
            'location_term': context_tools.get_location_term(request),
            'moc_term': context_tools.get_moc_term(request),
            'query_string': context_tools.get_query_string(request),
            'title_term': context_tools.get_title_term(request),
        }


class ShareBlock(Block):
    base_template = 'myblocks/blocks/share.html'


class VeteranSearchBox(Block):
    base_template = 'myblocks/blocks/veteransearchbox.html'

    def context(self, request, **kwargs):
        return {
            'location_term': context_tools.get_location_term(request, **kwargs),
            'moc_term': context_tools.get_moc_term(request),
            'moc_id_term': context_tools.get_moc_id_term(request),
            'search_url': context_tools.get_search_url(request),
            'site_config': context_tools.get_site_config(request),
            'title_term': context_tools.get_title_term(request),
            'total_jobs_count': context_tools.get_total_jobs_count(request),
        }


class Row(models.Model):
    blocks = models.ManyToManyField('Block', through='BlockOrder')

    updated = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return ', '.join([block.name for block in self.blocks.all()])

    @staticmethod
    def bootstrap_classes():
        return "row"

    @context_tools.Memoized
    def context(self, request, **kwargs):
        context = {}
        for block in self.blocks.all():
            context.update(block.cast().context(request, **kwargs))
        return context

    @context_tools.Memoized
    def get_template(self):
        """
        Combines all the templates for each block in the Row
        in the order specified by the matching BlockOrder.
        The combined templates are then wrapped in a row div.

        """
        blocks = [block.cast().get_template()
                  for block in self.blocks.all().order_by('blockorder__order')]

        return '<div class="row">%s</div>' % ''.join(blocks)

    @context_tools.Memoized
    def required_js(self):
        """
        Combines and de-duplicates any javascript required by the
        blocks in the Row.

        """
        js = []
        for block in self.blocks.all():
            js += block.cast().required_js()
        return list(set(js))


class Page(models.Model):
    """
    Blocks webpage container. Comprised of rows of blocks to form a highly
    customizable webpage.

    """
    base_template = 'myblocks/myblocks_base.html'
    base_head = 'myblocks/head/page.html'
    templatetag_library = templatetag_library()

    AJAX_JOBS = 'ajax_jobs'
    ERROR_404 = '404'
    HOME_PAGE = 'home_page'
    JOB_DETAIL = 'job_detail'
    SEARCH_RESULTS = 'search_results'
    LOGIN = 'login'
    NO_RESULTS = 'no_results'

    PRODUCTION = 'production'
    STAGING = 'staging'

    page_type_choices = (
        (ERROR_404, '404'),
        (HOME_PAGE, 'Home Page'),
        (JOB_DETAIL, 'Job Detail Page'),
        (SEARCH_RESULTS, 'Job Search Results Page'),
        (LOGIN, 'Login Page'),
        (NO_RESULTS, 'No Results Found'),
    )
    page_status_choices = (
        (STAGING, 'Staging'),
        (PRODUCTION, 'Production'),
    )

    page_type = models.CharField(choices=page_type_choices, max_length=255)
    name = models.CharField(max_length=255)

    rows = models.ManyToManyField('Row', through='RowOrder')
    sites = models.ManyToManyField('seo.SeoSite')
    status = models.CharField(choices=page_status_choices, max_length=255,
                              default='production')

    head = models.TextField(blank=True)

    updated = models.DateTimeField(auto_now=True)

    add_blank = lambda choices: (('', 'Inherit from Configuration'),) + choices

    doc_type = models.CharField(max_length=255, blank=True,
                                choices=add_blank(DOCTYPE_CHOICES),
                                default='')
    language_code = models.CharField(max_length=16, blank=True,
                                     choices=add_blank(LANGUAGE_CODES_CHOICES),
                                     default='')

    def __unicode__(self):
        return self.name

    @context_tools.Memoized
    def all_blocks(self):
        """
        Gets a list of every unique block included in a page.

        """
        query = (models.Q(row__page=self) |
                 models.Q(columnblockorder__column_block__row__page=self))
        return [block.cast() for block in Block.objects.filter(query).distinct()]

    def bootstrap_classes(self):
        return "col-md-12"

    def context(self, request, **kwargs):
        context = {}
        for block in self.all_blocks():
            context.update(block.context(request, **kwargs))

        site_config = get_site_config(request)

        context.update({'site_title': settings.SITE_TITLE,
                        'site_description': settings.SITE_DESCRIPTION,
                        'doctype': self.doc_type or site_config.doc_type,
                        'language_code': (self.language_code
                                          or site_config.language_code)})

        return context

    def get_body(self):
        rows = []
        for row in self.rows.all().order_by('roworder__order'):
            rows.append(row.get_template())
        return ''.join(rows)

    @context_tools.Memoized
    def get_head(self):
        """
        Combines the page head with all of the heads for each
        individual block on the page.

        """
        blocks = self.all_blocks()

        # Combine the block head
        head = [block.head for block in blocks]

        additional_js = []

        # Combine, convert to script tags, and de-duplicate all of the
        # js required for each page.
        for block in self.all_blocks():
            additional_js += [self.to_js_tag(js) for js in block.required_js()]

        head += list(set(additional_js))

        # Apply Page.head last so that any CSS in Page.head overwrites
        # the block-level CSS.
        return ''.join(head) + self.head

    def get_template(self, request):
        filters = context_tools.get_filters(request)

        context = self.context(request)
        context.update({
            'body': mark_safe(self.get_body()),
            'google_analytics': context_tools.get_google_analytics(request),
            'head': mark_safe(self.get_head()),
            'max_filter_settings': settings.ROBOT_FILTER_LEVEL,
            'num_filters': len([k for (k, v) in filters.iteritems() if v]),
            'page': self,
            'STATIC_URL': settings.STATIC_URL,
        })
        template = Template(raw_base_template(self))
        return template.render(Context(context))

    def human_readable_page_type(self):
        """
        Converts the page_type into a human readable format for use
        in the admin.

        """
        page_type_choices_dict = dict(self.page_type_choices)
        return page_type_choices_dict.get(self.page_type, '')
    human_readable_page_type.short_description = 'Page Type'

    def human_readable_sites(self):
        """
        Converts sites into a list of matching domains for use in the
        admin.

        """
        return ', '.join(self.sites.values_list('domain', flat=True))
    human_readable_sites.short_description = 'Sites'

    def human_readable_status(self):
        """
        Converts status into a human readable format for use in the admin.
        """
        status_choices_dict = dict(self.page_status_choices)
        return status_choices_dict[self.status]
    human_readable_status.short_description = 'Status'

    def pixel_template(self):
        """
        Returns the template for the tracking pixel.

        """
        return mark_safe("""
            <img style="display: none;" border="0" height="1" width="1" alt="My.jobs"
            {% if the_job %}
                src="//my.jobs/pixel.gif?{{request|make_pixel_qs:the_job|safe}}"
            {% else %}
                src="//my.jobs/pixel.gif?{{request|make_pixel_qs|safe}}"
            {% endif %}
            />
        """)

    def render(self, request, **kwargs):
        """
        Gets the template for a Page and renders it. Results are cached
        in the blocks_cache using render_cache_prefix as the cache key.

        """
        key = self.render_cache_prefix(request)
        rendered_template = blocks_cache.get(key)
        if rendered_template:
            return rendered_template
        context = self.context(request, **kwargs)
        template = Template(self.get_template(request))
        rendered_template = template.render(RequestContext(request, context))
        blocks_cache.set(key, rendered_template, settings.MINUTES_TO_CACHE*60)
        return rendered_template

    def render_cache_prefix(self, request):
        """
        Combines the current domain, the page, the current path,
        the current query string, all of the blocks for a page, all
        of the rows for a page, the current site configuration,
        and all business units for the current site into a
        single string and then hashes it.

        This can be used as a cache key for a Page. It will be change any
        time any block, row, page, or configuration is updated.

        """
        domain = None
        if request.user.is_authenticated() and request.user.is_staff:
            domain = request.REQUEST.get('domain')
        if domain is None:
            domain = request.get_host()

        page = '%s::%s' % (self.pk, self.updated)
        path = request.path
        query_string = context_tools.get_query_string(request)
        blocks = self.all_blocks()
        blocks = ["%s::%s" % (block.id, str(block.updated)) for block in
                  blocks]
        blocks = '#'.join(blocks)
        rows = self.rows.all()
        rows = ["%s::%s" % (row.id, str(row.updated)) for row in rows]
        rows = '#'.join(rows)
        config = context_tools.get_site_config(request)
        config = '%s::%s' % (config.pk, config.revision)
        buids = [str(buid) for buid in getattr(settings, 'SITE_BUIDS', [])]
        buids = '#'.join(buids)
        key = '###'.join([page, path, query_string, config, blocks, rows,
                          buids, domain]).encode('utf-8')
        return hashlib.sha1(key).hexdigest()

    def to_js_tag(self, js_file):
        """
        :param js_file: The location of a javascript file as a string.
        :return: A script tag for js_file.
        """
        return '<script type="text/javascript" src="%s"></script>' % js_file

    def handle_job_detail_redirect(self, request, *args, **kwargs):
        """
        Used on job detail pages, this returns a redirect to the
        appropriate url if:

        1. There is no matching job (404).
        2. The matching job isn't actually available on the site
            because it belongs to a business unit or site package
            not associated with that site (Redirect to home page).
        3. It's missing slugs or the slugs are out of order
            Redirect to the page with slugs in the correct order).

        If there is no redirect, returns None.

        """
        job_id = kwargs.get('job_id', '')
        job = context_tools.get_job(request, job_id)

        if not job:
            if job_id:
                search_type = 'guid' if len(job_id) > 31 else 'uid'
                # The job was not in solr; find and redirect to its apply url
                # if it's a new job that hasn't been syndicated, otherwise
                # return a 404.
                do_redirect = redirect_if_new(**{search_type: job_id})
                if do_redirect:
                    return do_redirect
            raise Http404("myblocks.models.Page.handle_job_detail_redirect: "
                          "job does not exist")

        if settings.SITE_BUIDS and job.buid not in settings.SITE_BUIDS:
            on_this_site = set(settings.SITE_PACKAGES) & set(job.on_sites)
            if job.on_sites and not on_this_site:
                return redirect('home')

        title_slug = kwargs.get('title_slug', '').lower()
        location_slug = kwargs.get('location_slug', '').lower()
        job_location_slug = slugify(job.location).lower()

        if (title_slug == job.title_slug.lower() and
                location_slug == job_location_slug):
            return None

        feed = kwargs.get('feed', '')
        query = ""
        for k, v in request.GET.items():
            query = ("=".join([k, v]) if query == "" else
                     "&".join([query, "=".join([k, v])]))

        # The url wasn't quite the canonical form, so we redirect them
        # to the correct version based on the title and location of the
        # job with the passed in id.
        new_kwargs = {
            'location_slug': slugify(job.location),
            'title_slug': job.title_slug,
            'job_id': job.guid
        }
        redirect_url = reverse('job_detail_by_location_slug_title_slug_job_id',
                               kwargs=new_kwargs)

        # if the feed type is passed, add source params, otherwise only preserve
        # the initial query string.
        if feed:
            if query != "":
                query = "&%s" % query
            redirect_url += "?utm_source=%s&utm_medium=feed%s" % (feed, query)
        elif query:
            redirect_url += "?%s" % query
        return redirect(redirect_url, permanent=True)

    def handle_search_results_redirect(self, request):
        """
        Used on search result pages, this returns a redirect to the
        appropriate url if:

        1.  helpers.determine_redirect() supplies a redirect.
            The redirect rules that function uses are defined
            in the determine_redirect function.
        2.  There are no facet_counts (Redirect to home page).
        3.  There are no featured jobs, no default jobs, and
            no query term applied. This means there are either
            no jobs for the site or a series of filters that
            should not be able to be applied were applied
            (Redirects to home page).

        If there is no redirect, returns None.

        """

        filters = context_tools.get_filters(request)
        query_string = context_tools.get_query_string(request)

        redirect_url = helpers.determine_redirect(request, filters)
        if redirect_url:
            return redirect_url

        jobs_and_counts = context_tools.get_jobs_and_counts(request)
        default_jobs = jobs_and_counts[0]
        featured_jobs = jobs_and_counts[2]
        facet_counts = jobs_and_counts[4]
        if not facet_counts:
            return redirect("/")
        if (len(default_jobs) == 0 and len(featured_jobs) == 0
                and not query_string):
            return redirect("/")

        return

    def handle_redirect(self, request, *args, **kwargs):
        """
        Allows for each page type to handle the possibility of redirecting
        if necessary.

        """
        if self.page_type == self.JOB_DETAIL:
            return self.handle_job_detail_redirect(request, *args, **kwargs)
        if self.page_type == self.SEARCH_RESULTS:
            return self.handle_search_results_redirect(request)
        return None


class BlockOrder(models.Model):
    block = models.ForeignKey('Block')
    row = models.ForeignKey('Row')
    order = models.PositiveIntegerField()

    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('order', )


class ColumnBlockOrder(models.Model):
    block = models.ForeignKey('Block')
    column_block = models.ForeignKey('ColumnBlock',
                                     related_name='included_column_blocks')
    order = models.PositiveIntegerField()

    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('order', )


class RowOrder(models.Model):
    row = models.ForeignKey('Row')
    order = models.PositiveIntegerField()
    page = models.ForeignKey('Page')

    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('order', )

    def __unicode__(self):
        return "Row for page %s" % self.page.pk
