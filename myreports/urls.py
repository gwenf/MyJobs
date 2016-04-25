from django.conf.urls import patterns, url
from myreports.views import ReportView

urlpatterns = patterns(
    'myreports.views',
    url(r'^view/overview$', 'overview', name='overview'),
    url(r'^view/archive$', 'report_archive', name='report_archive'),
    url(r'view/(?P<app>\w+)/(?P<model>\w+)$', ReportView.as_view(),
        name='reports'),
    url(r'^ajax/regenerate', 'regenerate', name='regenerate'),
    url(r'^ajax/(?P<app>\w+)/(?P<model>\w+)$',
        'view_records',
        name='view_records'),
    url(r'^view/dynamicdownload$', 'download_dynamic_report',
        name='download_dynamic_report'),
    url(r'download$', 'download_report', name='download_report'),
    url(r'view/downloads$', 'downloads', name='downloads'),
    url(r'^view/dynamicoverview/$', 'dynamicoverview', name='dynamicoverview'),
    url(r'^api/select_data_type_api$', 'select_data_type_api',
        name='select_data_type_api'),
    url(r'^api/export_options_api$', 'export_options_api',
        name='export_options_api'),
    url(r'^api/filters$', 'filters_api', name='filters_api'),
    url(r'^api/list_reports$', 'list_dynamic_reports',
        name='list_dynamic_reports'),
    url(r'^api/run_report$', 'run_dynamic_report', name='run_dynamic_report'),
    url(r'^api/help$', 'help_api', name='help_api'),
    url(r'^api/default_report_name$', 'get_default_report_name',
        name='get_default_report_name'),
    url(r'^api/old_report_preview$', 'old_report_preview',
        name='old_report_preview')
)
