from django.conf.urls import patterns, url, include
from django.views.generic import RedirectView

from impersonate.views import stop_impersonate

from myjobs.views import About, Privacy, Terms


accountpatterns = patterns('myjobs.views',
                           url(r'^edit/$',
                               'edit_account',
                               name='edit_account'),
                           url(r'^delete$',
                               'delete_account',
                               name='delete_account'),
                           url(r'^disable$',
                               'disable_account',
                               name='disable_account'),
                           url(r'^$',
                               RedirectView.as_view(url='/account/edit/')),)

impersonate_patterns = patterns(
    'myjobs.views',
    url(r'^impersonate/(?P<uid>\d+)/$', 'impersonate',
        name='impersonate-start'),
    url(r'^impersonate/stop/$', stop_impersonate, name='impersonate-stop'),
    url(r'^impersonate/(?P<access_id>\d+)/approve/$', 'process_access_request',
        {'accepted': True}, name='impersonate-approve'),
    url(r'^impersonate/(?P<access_id>\d+)/reject/$', 'process_access_request',
        {'accepted': False}, name='impersonate-reject'),
    url(r'^impersonate/(?P<uid>\d+)/request/$', 'request_account_access',
        name='request-account-access'),
)

urlpatterns = patterns(
    'myjobs.views',

    url(r'^$', 'home', name='home'),
    url(r'^login$',
        RedirectView.as_view(url='/')),
    # Url is duplicated so that we can also easily refer to it as the
    # login url. This might mess with things if you try to resolve a url
    # and use url_name, since it could be either home or login.
    url(r'^$', 'home', name='login'),

    url(r'^about/$', About.as_view(), name='about'),
    url(r'^privacy/$', Privacy.as_view(), name='privacy'),
    url(r'^terms/$', Terms.as_view(), name='terms'),
    url(r'^contact/$', 'contact', name='contact'),
    url(r'^contact-faq', 'contact_faq', name='contact_faq'),
    url(r'^batch$', 'batch_message_digest', name='batch_message_digest'),
    url(r'^unsubscribe/$', 'unsubscribe_all', name='unsubscribe_all'),
    url(r'^account/', include(accountpatterns)),
    url(r'^send/$', 'continue_sending_mail', name='continue_sending_mail'),
    url(r'^cas/$', 'cas', name='cas'),
    url(r'^topbar/$', 'topbar', name='topbar'),

    url(r'^manage-users/$',
        'manage_users',
        name='manage_users'),
    url(r'^manage-users/api/roles/$',
        'api_get_roles',
        name='api_get_roles'),
    # TODO: Remove once roles page converted
    url(r'^manage-users/api/roles/all/$',
        'api_get_all_roles',
        name='api_get_all_roles'),
    url(r'^manage-users/api/roles/(?P<role_id>[0-9]+)/$',
        'api_get_specific_role',
        name='api_get_specific_role'),
    url(r'^manage-users/api/roles/create/$',
        'api_create_role', name='api_create_role'),
    url(r'^manage-users/api/roles/edit/(?P<role_id>[0-9]+)/$',
        'api_edit_role', name='api_edit_role'),
    url(r'^manage-users/api/roles/delete/(?P<role_id>[0-9]+)/$',
        'api_delete_role',
        name='api_delete_role'),
    url(r'^manage-users/api/users/$',
        'api_get_users',
        name='api_get_users'),
    url(r'^manage-users/api/users/(?P<user_id>[0-9]+)/$',
        'api_edit_user',
        name='api_edit_user'),
    url(r'^manage-users/api/users/add/$',
        'api_add_user',
        name='api_add_user'),
    url(r'^manage-users/api/users/remove/(?P<user_id>[0-9]+)/$',
        'api_remove_user',
        name='api_remove_user'),
    url(r'^manage-users/api/activities/$',
        'api_get_activities',
        name='api_get_activities'),
    url(r'^request-company-access/$',
        'request_company_access', name='request_company_access'),
)

urlpatterns += impersonate_patterns
