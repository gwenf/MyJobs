from django.conf.urls import patterns, url
from django.views.generic import RedirectView

urlpatterns = patterns('mypartners.views',
    url(r'^$', RedirectView.as_view(url='/prm/view/')),
    url(r'^api/nonuseroutreach/inbox/list$', 'api_get_nuo_inbox_list', name='api_get_nuo_inbox_list'),
    url(r'^api/nonuseroutreach/records/list$', 'api_get_nuo_records_list', name='api_get_nuo_records_list'),
    url(r'^api/nonuseroutreach/records/record', 'api_get_individual_nuo_record', name='api_get_individual_nuo_record'),
    url(r'^api/nonuseroutreach/records/convert', 'api_convert_outreach_record', name='api_convert_outreach_record'),
    url(r'^api/nonuseroutreach/inbox/add', 'api_add_nuo_inbox',
        name='api_add_nuo_inbox'),
    url(r'^api/nonuseroutreach/inbox/delete', 'api_delete_nuo_inbox',
        name='api_delete_nuo_inbox'),
    url(r'^api/nonuseroutreach/inbox/update', 'api_update_nuo_inbox',
        name='api_update_nuo_inbox'),
    url(r'^view/$', 'prm', name='prm'),
    url(r'^view$', 'prm', name='prm'),
    url(r'^view/partner-library/add/$', 'create_partner_from_library',
        name="create_partner_from_library"),
    url(r'^view/partner-library/', 'partner_library', name="partner_library"),
    url(r'^view/overview$', 'prm_overview', name='partner_overview'),
    url(r'^view/tagging$', 'partner_tagging', name='partner_tagging'),
    url(r'^view/tagging/add$', 'add_tags', name='add_tags'),
    url(r'^view/tagging/edit$', 'edit_partner_tag', name='edit_partner_tag'),
    url(r'^view/tagging/delete$', 'delete_partner_tag', name='delete_partner_tag'),
    url(r'^view/records$', 'prm_records', name='partner_records'),
    url(r'^view/records/get-tags', 'tag_names', name="tag_names"),
    url(r'^view/records/get-tag-color', 'tag_color', name="tag_color"),
    url(r'^view/records/edit$', 'prm_edit_records', name='partner_edit_record'),
    url(r'^view/records/retrieve_records', 'partner_get_records',
        name="partner_get_records"),
    url(r'^view/records/retrieve_referrals', 'partner_get_referrals',
        name="partner_get_referrals"),
    url(r'^view/records/details$', 'prm_view_records', name='record_view'),
    url(r'^view/records/update$', 'get_records', name='get_records'),
    url(r'^view/records/contact_info$', 'get_contact_information',
        name='get_contact_information'),
    url(r'^view/searches$', 'prm_saved_searches', name='partner_searches'),
    url(r'^view/searches/edit$', 'prm_edit_saved_search',
        name='partner_edit_search'),
    url(r'^view/searches/verify-contact/$', 'verify_contact',
        name='verify_contact'),
    url(r'^view/searches/save', 'partner_savedsearch_save',
        name='partner_savedsearch_save'),
    url(r'^view/searches/feed', 'partner_view_full_feed',
        name='partner_view_full_feed'),
    url(r'^view/save$', 'save_init_partner_form',
        name='save_init_partner_form'),
    url(r'^view/details$', 'partner_details', name='partner_details'),
    url(r'^view/edit$', 'edit_item', name='create_partner'),
    url(r'^view/details/edit$', 'edit_item', name='edit_contact'),
    url(r'^view/details/save$', 'save_item', name='save_item'),
    url(r'^view/details/delete$', 'delete_prm_item', name='delete_prm_item'),
    url(r'^view/locations/edit$', 'edit_location', name='edit_location'),
    url(r'^view/locations/delete$', 'delete_location', name='delete_location'),
    url(r'^view/reports/details$', 'partner_main_reports', name='report_view'),
    url(r'^view/reports/details/records/', 'prm_records',
        name='prm_report_records'),
    url(r'^view/nonuseroutreach/$', 'nuo_main', name='nuo_main'),
    url(r'^email$', 'process_email', name='process_email'),
    url(r'^download/', 'get_uploaded_file', name='get_uploaded_file'),
    url(r'^export/', 'prm_export', name='prm_export'),
)
