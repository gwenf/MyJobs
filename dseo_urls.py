from django.conf.urls import include, patterns, url
from django.contrib import admin
from django.db.models.loading import cache as model_cache
from django.views.generic import RedirectView

from myjobs.urls import impersonate_patterns
from seo.views.search_views import (BusinessUnitAdminFilter, SeoSiteAdminFilter,
                                    Dseo404)
from seo.views.settings_views import secure_redirect
from registration import views as registration_views
from ajax_select import urls as ajax_select_urls

# This is a bit of code pulled from a Django TRAC ticket describing a problem
# I was seeing when working with the inline model forms:
# https://code.djangoproject.com/ticket/10405#comment:11

# Without this, on pages that aren't serving job-related content, e.g. sitemap,
# stylesheet, etc. pages, we'd see an error like:
# AttributeError: 'str' object has no attribute '_default_manager'

# The Trac ticket linked above recommended including this bit of code, and also
# included a comprehensive explanation. When/if this particular issue gets
# resolved we can safely remove this conditional.
if not model_cache.loaded:
    model_cache.get_models()

from tastypie.api import Api
from seo.api import resources

v1_api = Api(api_name="v1")
v1_api.register(resources.SeoSiteResource())
v1_api.register(resources.ATSResource())
v1_api.register(resources.GroupResource())
v1_api.register(resources.ViewSourceResource())
v1_api.register(resources.BusinessUnitResource())
v1_api.register(resources.GoogleAnalyticsResource())
v1_api.register(resources.GoogleAnalyticsCampaignResource())
v1_api.register(resources.SpecialCommitmentResource())
v1_api.register(resources.CustomFacetResource())
v1_api.register(resources.ConfigurationResource())
v1_api.register(resources.FeaturedCompanyResource())
v1_api.register(resources.CompanyResource())
v1_api.register(resources.BillboardImageResource())
v1_api.register(resources.BillboardHotspotResource())
v1_api.register(resources.MocResource())
v1_api.register(resources.MocDetailResource())
v1_api.register(resources.OnetResource())
v1_api.register(resources.JobSearchResource())
v1_api.register(resources.JobResource())

admin.autodiscover()
handler404 = Dseo404.as_view()
handler500 = 'seo.views.search_views.dseo_500'


# API endpoints
urlpatterns = patterns('',
    url('^api/', include(v1_api.urls))
)

# Custom Admin URLs
urlpatterns += patterns('seo.views.search_views',
    url(r'^admin/groupsites/$', 'get_group_sites'),
    url(r'^admin/grouprelationships/$', 'get_group_relationships'),
)

urlpatterns += patterns('',
    url(r'^ajax_select/', include(ajax_select_urls)),
    url(r'^admin/', include(admin.site.urls)),
    url('', include('seo.urls.search_urls', app_name='seo')),
    url('settings/', include('seo.urls.settings_urls')),
    url('^mocmaps/', include('moc_coding.urls', app_name='moc_coding')),
    url(r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': '/'},
        name='auth_logout'),
    url(r'^posting/', include('postajob.urls', app_name='postajob')),
)


urlpatterns += patterns(
    '',
    # Filtering urls
    url(r'^ajax/data/filter/business_units/$',
        BusinessUnitAdminFilter.as_view(),
        name='buid_admin_fsm'),
    url(r'^ajax/data/filter/sites/$', SeoSiteAdminFilter.as_view(),
        name='site_admin_fsm')
)


urlpatterns += patterns(
    '',
    url(r'^account/$',
        RedirectView.as_view(url='https://secure.my.jobs/account/edit')),
    url(r'^candidates/$',
        RedirectView.as_view(url='https://secure.my.jobs/candidates/view')),
    url(r'^profile/$',
        RedirectView.as_view(url='https://secure.my.jobs/profile/view')),
    url(r'^savedsearch/$',
        RedirectView.as_view(url='https://secure.my.jobs/saved-search/view')),
    url(r'^accounts/', include('registration.urls')),
)

for page in ['about', 'privacy', 'contact', 'contact-faq', 'terms']:
    urlpatterns += patterns(
        '',
        url(r'^{page}/'.format(page=page), secure_redirect, {'page': page},
            name=page.replace('-', '_'))
    )

urlpatterns += patterns(
    'myjobs.views',
    url(r'^account/edit/$', 'edit_account', name='edit_account'),
    url(r'^account/delete$', 'delete_account', name='delete_account'),
    url(r'^account/disable$', 'disable_account', name='disable_account'),
)

urlpatterns += patterns(
    'registration.views',
    url(r'^login', registration_views.DseoLogin.as_view(), name='login'),
)

# This feature does not exist...
urlpatterns += patterns(
    '',
    url(r'^message/', include('mymessages.urls'))
)

urlpatterns += patterns(
    'myblocks.views',
    url(r'^secure-blocks/$', 'secure_blocks', name='secure_blocks'),
)

urlpatterns += impersonate_patterns

urlpatterns += patterns(
    '',
    url(r'^blog/', include('myblogs.urls')),
)
