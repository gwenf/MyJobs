from collections import OrderedDict
from datetime import datetime
import json

from django.core.files.base import ContentFile
from django.db.models.loading import get_model
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.utils.decorators import method_decorator
from django.views.generic import View
from django.views.decorators.http import require_http_methods

from myreports.helpers import humanize, serialize, sort_records
from myjobs.decorators import requires
from myreports.models import (
    Report, ReportPresentation, DynamicReport, ReportTypeDataTypes,
    ConfigurationColumn)
from myreports.presentation import presentation_drivers
from myreports.presentation.disposition import get_content_disposition
from postajob import location_data
from universal.helpers import get_company_or_404
from universal.api_validation import ApiValidator
from universal.decorators import restrict_to_staff

from myreports.datasources import ds_json_drivers

from cStringIO import StringIO


@require_http_methods(['GET'])
@requires('read partner', 'read contact', 'read communication record')
def overview(request):
    """The Reports app landing page."""
    company = get_company_or_404(request)

    # used to remember version of reporting user last visited
    reporting_cookie = ('reporting_version', 'classic')

    success = 'success' in request.POST
    reports = Report.objects.filter(owner=company).order_by("-created_on")
    report_count = reports.count()
    past_reports = reports[:10]
    states = OrderedDict(
        sorted((v, k) for k, v in location_data.states.inv.iteritems()))

    ctx = {
        "company": company,
        "success": success,
        "states": json.dumps(states),
        "past_reports": past_reports,
        "report_count": report_count
    }

    if request.is_ajax():
        response = HttpResponse()
        response.set_cookie(*reporting_cookie)
        html = render_to_response('myreports/includes/report_overview.html',
                                  ctx, RequestContext(request)).content
        response.content = html
        return response

    response = HttpResponse()
    html = render_to_response('myreports/reports.html', ctx,
                              RequestContext(request))
    response.content = html
    response.set_cookie(*reporting_cookie)
    return response


@requires('read partner', 'read contact', 'read communication record')
def report_archive(request):
    """Archive of previously run reports."""
    if request.is_ajax():
        company = get_company_or_404(request)
        reports = Report.objects.filter(owner=company).order_by("-created_on")

        ctx = {
            "reports": reports
        }

        response = HttpResponse()
        html = render_to_response('myreports/includes/report-archive.html',
                                  ctx, RequestContext(request))
        response.content = html.content

        return response


@requires('read partner', 'read contact', 'read communication record')
def view_records(request, app="mypartners", model="contactrecord"):
    """
    Returns records as JSON.

    Inputs:
        :request: Request object to inspect for search parameters.
        :app: Application to query.
        :model: Model to query.

    Query String Parameters:
        :filters: A JSON string representing th exact query to be run.
        :values: The fields to include in the output.
        :order_by: The field to order the results by. Prefix with a '-' to
                   indiciate descending order.

    Output:
       A JSON response containing the records queried for.
    """
    if request.is_ajax() and request.method == 'POST':
        company = get_company_or_404(request)
        filters = request.POST.get("filters")
        values = request.POST.getlist("values")
        order_by = request.POST.get("order_by", None)

        records = get_model(app, model).objects.from_search(
            company, filters)

        if values:
            if not hasattr(values, '__iter__'):
                values = [values]

            records = records.values(*values)

        if order_by:
            if not hasattr(order_by, '__iter__'):
                order_by = [order_by]

            records = records.order_by(*order_by)

        ctx = serialize('json', records, values=values)

        response = HttpResponse(
            ctx, content_type='application/json; charset=utf-8')

        return response
    else:
        raise Http404("This view is only reachable via an AJAX GET request.")


class ReportView(View):
    """
    View for managing report objects.

    A GET request will fetch a report, where as a POST will generate a new
    report.
    """

    app = 'mypartners'
    model = 'contactrecord'

    @method_decorator(requires(
        'read partner', 'read contact', 'read communication record'))
    def dispatch(self, *args, **kwargs):
        return super(ReportView, self).dispatch(*args, **kwargs)

    def get(self, request, **kwargs):
        """
        Get a report by ID and return interesting numbers as a JSON
        response. The only expected query parameter is 'id'.

        Query String Parameters:
            :id: The id of the report to retrieve

        Outputs:
            Renders a json object with counts for email, calls, searches,
            meetings, applications, interviews, hires, communications,
            referrals, and contacts. All these are integers except for
            contacts, which is a list of objects, each of which has a name,
            email, referral count, and communications count.
        """

        report_id = request.GET.get('id', 0)
        report = get_object_or_404(Report, pk=report_id)

        if report.model == "contactrecord":
            records = report.queryset
            ctx = json.dumps({
                'emails': records.emails,
                'calls': records.calls,
                'searches': records.searches,
                'meetings': records.meetings,
                'applications': records.applications,
                'interviews': records.interviews,
                'hires': records.hires,
                'communications': records.communication_activity.count(),
                'referrals': records.referrals,
                'contacts': list(records.contacts)})
            status = 200
        elif report.results:
            ctx = report.json
            status = 200
        else:
            ctx = "Report %s has no results. Please regenerate." % report.name
            status = 503

        return HttpResponse(
            ctx,
            status=status,
            content_type='application/json; charset=utf-8')

    def post(self, request, app='mypartners', model='contactrecords'):
        """
        Create a report by querying on a specific model.

        The request's POST data is parsed for parameters to pass to the model's
        `from_search` method.

        Inputs:
            :app: The app to which the model belongs.
            :model: The model to query on

        Query String Parameters:
            :csrfmiddlewaretoken: Used to prevent Cross Site Request Forgery.
            :report_name: What to name the report. Spaces are converted to
                          underscores.
            :filters: A JSON string representing th exact query to be run.
            :values: Fields to include in report output.

        Outputs:
           An HttpResponse indicating success or failure of report creation.
        """

        company = get_company_or_404(request)
        name = request.POST.get('report_name', str(datetime.now()))
        filters = request.POST.get('filters', "{}")

        records = get_model(app, model).objects.from_search(
            company, filters)

        contents = serialize('json', records)
        results = ContentFile(contents)
        report, _ = Report.objects.get_or_create(
            name=name, created_by=request.user,
            owner=company, app=app, model=model,
            filters=filters)

        report.results.save('%s-%s.json' % (name, report.pk), results)

        return HttpResponse(name, content_type='text/plain')


@requires('read partner', 'read contact', 'read communication record')
def regenerate(request):
    """
    Regenerates a report.

    Useful if the report json file is no longer available on disk. If called
    and the report is already on disk, `Report.regenerate` does nothing.

    Query String Parameters:
        :id: ID of the report to regenerate.
    """

    if request.method == 'GET':
        report_id = request.GET.get('id', 0)
        report = get_object_or_404(
            get_model('myreports', 'report'), pk=report_id)

        report.regenerate()

        return HttpResponse("Report successfully regenerated",
                            content_type='text/csv')

    raise Http404(
        "This view is only reachable via a GET request.")


@requires('read partner', 'read contact', 'read communication record')
def downloads(request):
    """ Renders a download customization screen.

        If the report has `values`, then the screen will render the checkboxes
        representing those fields as checked and all others as unchecked. The
        order of the rendered checklist follows these `values`, with all other
        checkboxes being ordered aphabetically.

        Query String Parameters:
            :id: ID of the report to show options for.
    """

    if request.is_ajax() and request.method == 'GET':
        report_id = request.GET.get('id', 0)
        report = get_object_or_404(
            get_model('myreports', 'report'), pk=report_id)

        common_blacklist = ['pk', 'approval_status', 'archived_on']
        blacklist = {
            'contactrecord': common_blacklist,
            'contact': common_blacklist + ['library', 'user'],
            'partner': common_blacklist + ['library', 'owner']}

        if report.python:
            fields = sorted([field for field in report.python[0].keys()
                             if field not in blacklist[report.model]])
        else:
            fields = []

        values = json.loads(report.values) or fields
        for field_list in [values, fields]:
            if 'contact_type' in field_list:
                index = field_list.index('contact_type')
                field_list[index] = 'communication_type'
        fields = values + [field for field in fields if field not in values]

        column_choice = ''
        sort_order = ''
        if report.order_by:
            if '-' in report.order_by:
                sort_order = '-'
                column_choice = report.order_by[1:]
            else:
                column_choice = report.order_by

        columns = OrderedDict()
        for field in fields:
            columns[' '.join(
                filter(bool, field.split('_'))).title()] = field in values

        ctx = {'columns': columns,
               'sort_order': sort_order,
               'column_choice': column_choice}

        return render_to_response('myreports/includes/report-download.html',
                                  ctx, RequestContext(request))
    else:
        raise Http404("This view is only reachable via an AJAX request")


@requires('read partner', 'read contact', 'read communication record')
def download_report(request):
    """
    Download report as CSV.

    Query String Parameters:
        :id: ID of the report to download
        :values: Fields to include in the resulting CSV, as well as the order
                 in which to include them.
        :order_by: The sort order for the resulting CSV.

    Outputs:
        The report with the specified options rendered as a CSV file.
    """

    report_id = request.GET.get('id', 0)
    values = request.GET.getlist('values', None)
    order_by = request.GET.get('order_by', None)

    report = get_object_or_404(
        get_model('myreports', 'report'), pk=report_id)

    if order_by:
        report.order_by = order_by
        report.save()

    if values:
        report.values = json.dumps(values)
        report.save()

    records = humanize(report.python)

    response = HttpResponse(content_type='text/csv')
    content_disposition = "attachment; filename=%s-%s.csv"
    response['Content-Disposition'] = content_disposition % (
        report.name.replace(' ', '_'), report.pk)

    response.write(serialize('csv', records, values=values, order_by=order_by))

    return response


@requires('read partner', 'read contact', 'read communication record')
@require_http_methods(['GET'])
def dynamicoverview(request):
    """The Dynamic Reports page."""
    company = get_company_or_404(request)
    ctx = {"company": company}
    response = HttpResponse()
    response.set_cookie('reporting_version', 'dynamic')
    html = render_to_response('myreports/dynamicreports.html', ctx,
                              RequestContext(request))
    response.content = html
    return response


@restrict_to_staff()
@requires('read partner', 'read contact', 'read communication record')
@require_http_methods(['POST'])
def select_data_type_api(request):
    """Help a user select a valid data_type to describe a report.

    The parameters represent current user selection and are optional.

    reporting_type: optional name of selected reporting type
    report_type: optional name of selected report type
    data_type: optional name of selected data type

    This api will make a best effort to fill in missing choices with valid
    defaults.

    returns:
        {
            reporting_types: list of valid reporting_type choices
            selected_reporting_type: suggested selected reporting type
            report_types: list of valid report_type choices
            selected_report_type: suggested selected report type
            data_types: list of valid data_type choices
            selected_data_type: suggested selected data type
        }
    """
    reporting_type = request.POST.get('reporting_type')
    report_type = request.POST.get('report_type')
    data_type = request.POST.get('data_type')

    choices = ReportTypeDataTypes.objects.build_choices(
        request.user, reporting_type, report_type, data_type)

    reporting_type_list = [
        {'value': rit.reporting_type, 'display': rit.description}
        for rit in choices['reporting_types']
    ]
    report_type_list = [
        {'value': rt.report_type, 'display': rt.description}
        for rt in choices['report_types']
    ]
    data_type_list = [
        {'value': dt.data_type, 'display': dt.description}
        for dt in choices['data_types']
    ]

    report_data = (
        ReportTypeDataTypes.objects.
        first_active_for_report_type_data_type(
            choices['selected_report_type'],
            choices['selected_data_type']))

    report_data_id = None
    if report_data:
        report_data_id = report_data.pk

    selected_reporting_type = None
    if choices['selected_reporting_type'] is not None:
        selected_reporting_type = (
            choices['selected_reporting_type'].reporting_type)

    selected_report_type = None
    if choices['selected_report_type'] is not None:
        selected_report_type = (
            choices['selected_report_type'].report_type)

    selected_data_type = None
    if choices['selected_data_type'] is not None:
        selected_data_type = (
            choices['selected_data_type'].data_type)

    data = {
        'reporting_types': reporting_type_list,
        'selected_reporting_type': selected_reporting_type,
        'report_types': report_type_list,
        'selected_report_type': selected_report_type,
        'data_types': data_type_list,
        'selected_data_type': selected_data_type,
        'report_data_id': report_data_id,
    }
    return HttpResponse(content_type='application/json',
                        content=json.dumps(data))


@restrict_to_staff()
@requires('read partner', 'read contact', 'read communication record')
@require_http_methods(['GET'])
def export_options_api(request):
    """Get options and defaults, etc. needed to drive a UI for downloads.

    Parameters:
        :report_id: Id of the report to download

    Outputs an object shaped like this:
        {
            'count': number of records in the report,
            'report_options': {
                'id': the report id,
                'formats': [
                    {
                        'value': format key,
                        'display': user visible title for format,
                    },
                ],
                'values': [
                    {
                        'value': key describing an available column,
                        'display': user visible title of column,
                    },
                ],
                'name': string containing the report name.
            },
        }
    """
    company = get_company_or_404(request)
    validator = ApiValidator()

    report_id = request.GET.get('report_id')
    if report_id is None:
        validator.note_field_error('report_id', 'Missing report id.')

    if validator.has_errors():
        return validator.build_error_response()

    report_list = list(DynamicReport.objects.filter(
        id=report_id, owner=company))
    if len(report_list) < 1:
        validator.note_field_error('report_id', 'Unknown report id.')

    if validator.has_errors():
        return validator.build_error_response()

    report = report_list[0]
    count = len(report.python)
    rps = (ReportPresentation.objects
           .active_for_report_type_data_type(report.report_data))

    cols = (
        ConfigurationColumn.objects
        .active_for_report_data(report.report_data)
        .order_by('order'))
    values = [
        {'value': c.column_name, 'display': c.alias or c.column_name}
        for c in cols
    ]

    data = {
        'count': count,
        'report_options': {
            'id': report.id,
            'formats': [
                {'value': rp.id, 'display': rp.display_name}
                for rp in rps
            ],
            'values': values,
            'name': report.name,
        },
    }
    return HttpResponse(content_type='application/json',
                        content=json.dumps(data))


@restrict_to_staff()
@requires('read partner', 'read contact', 'read communication record')
@require_http_methods(['POST'])
def filters_api(request):
    """Get a list of filters for the UI.

    report_data_id: Report Presentation ID

    response: See ContactsJsonDriver.encode_filter_interface()
    """
    company = get_company_or_404(request)
    request_data = request.POST
    report_data_id = request_data['report_data_id']
    report_data = ReportTypeDataTypes.objects.get(id=report_data_id)

    datasource = report_data.report_type.datasource

    report_configuration = report_data.configuration.build_configuration()

    driver = ds_json_drivers[datasource]
    data_type_name = report_data.data_type.data_type
    result = driver.encode_filter_interface(report_configuration)
    default_filter = driver.get_default_filter(data_type_name, company)
    result['default_filter'] = default_filter

    return HttpResponse(content_type='application/json',
                        content=driver.serialize_filterlike(result))


@requires('read partner', 'read contact', 'read communication record')
@require_http_methods(['POST'])
def help_api(request):
    """Get help for a partially filled out field.

    report_data_id: Report Data ID
    filter: JSON string with user filter to use
    field: Name of field to get help for
    partial: Data entered so far

    response: [{'value': data, 'display': data to display}]
    """
    company = get_company_or_404(request)
    request_data = request.POST
    report_data_id = request_data['report_data_id']
    filter_spec = request_data['filter']
    field = request_data['field']
    partial = request_data['partial']

    report_data = ReportTypeDataTypes.objects.get(id=report_data_id)
    datasource = report_data.report_type.datasource
    driver = ds_json_drivers[datasource]

    result = driver.help(company, filter_spec, field, partial)

    return HttpResponse(content_type="application/json",
                        content=json.dumps(result))


@requires('read partner', 'read contact', 'read communication record')
@require_http_methods(['POST'])
def run_dynamic_report(request):
    """Run a dynamic report.

    report_data_id: Report Presentation ID
    name: name of report
    filter_spec: JSON string with user filter to use

    response: {'id': new dynamic report id}
    """
    validator = ApiValidator()
    company = get_company_or_404(request)
    report_data_id = request.POST['report_data_id']
    name = request.POST.get('name', '')
    if not name:
        validator.note_field_error("name", "Report name must not be empty.")
    filter_spec = request.POST.get('filter', '{}')
    report_data = ReportTypeDataTypes.objects.get(id=report_data_id)

    if validator.has_errors():
        return validator.build_error_response()

    report = DynamicReport.objects.create(
        report_data=report_data,
        filters=filter_spec,
        name=name,
        owner=company)

    report.regenerate()

    data = {'id': report.id}
    return HttpResponse(content_type='application/json',
                        content=json.dumps(data))


@restrict_to_staff()
@requires('read partner', 'read contact', 'read communication record')
@require_http_methods(['GET'])
def list_dynamic_reports(request):
    """Get a list of dynamic report runs for this user."""
    company = get_company_or_404(request)

    # report_data == NULL should not happen in production data
    # Checking for it here to catch a situtation that happened due to a
    # migration before the first release.
    reports = (
        DynamicReport.objects
        .filter(owner=company, report_data__isnull=False)
        .order_by('-pk'))

    data = [{
        'id': r.id,
        'name': r.name,
        # report_type is only needed here for old_report_preview
        'report_type': r.report_data.report_type.report_type,
    } for r in reports]
    return HttpResponse(content_type='application/json',
                        content=json.dumps({'reports': data}))


@restrict_to_staff()
@requires('read partner', 'read contact', 'read communication record')
@require_http_methods(['GET'])
def get_dynamic_report_info(request):
    company = get_company_or_404(request)
    validator = ApiValidator()
    report_id = request.GET.get('report_id')
    if report_id is None:
        validator.note_field_error('report_id', 'Missing report id.')

    if validator.has_errors():
        return validator.build_error_response()

    report_list = list(DynamicReport.objects.filter(id=report_id))
    if len(report_list) < 1:
        validator.note_field_error('report_id', 'Unknown report id.')

    if validator.has_errors():
        return validator.build_error_response()

    report = report_list[0]

    # Guessing here. Many to many makes this ambiguous.
    reporting_type = (
        report.report_data.report_type.reportingtype_set.all()[0]
        .reporting_type)
    report_type = (
        report.report_data.report_type.report_type)
    data_type = (
        report.report_data.data_type.data_type)

    driver = ds_json_drivers[report.report_data.report_type.datasource]
    adorned_filter = driver.adorn_filter(company, report.filters)

    response = {
        'report_details': {
            'id': report.pk,
            'report_data_id': report.report_data.pk,
            'reporting_type': reporting_type,
            'report_type': report_type,
            'data_type': data_type,
            'name': report.name,
            'filter': adorned_filter,
        }
    }
    return HttpResponse(content_type='application/json',
                        content=driver.serialize_filterlike(response))


@requires('read partner', 'read contact', 'read communication record')
@require_http_methods(['GET'])
def download_dynamic_report(request):
    """
    Download dynamic report in some format.

    Query String Parameters:
        :id: ID of the report to export
        :values: Fields to include in the data, as well as the order
                 in which to include them.
        :order_by: The the field to sort the records by
        :direction: 'ascending' or 'decescending', for sort order
        :report_presentation_id: id of report presentation to use for file
                                 format.

    Outputs:
        The report with the specified options rendered in the desired format.
    """

    company = get_company_or_404(request)
    report_id = request.GET.get('id', 0)
    values = request.GET.getlist('values')
    order_by = request.GET.get('order_by')
    order_direction = request.GET.get('direction', 'ascending')
    report_presentation_id = request.GET.get('report_presentation_id')

    report = get_object_or_404(
        DynamicReport.objects.filter(owner=company), pk=report_id)
    report_presentation = (
        ReportPresentation.objects.get(id=report_presentation_id))
    config = report.report_data.configuration
    report_configuration = config.build_configuration()

    if order_by:
        report.order_by = order_by
        report.save()

    if len(values) == 0:
        values = report_configuration.get_header()

    records = [
        report_configuration.format_record(r, values)
        for r in report.python
    ]

    sorted_records = records
    if order_by:
        reverse = False
        if order_direction == 'descending':
            reverse = True
        sorted_records = sort_records(records, order_by, reverse)

    presentation_driver = (
        report_presentation.presentation_type.presentation_type)
    presentation = presentation_drivers[presentation_driver]
    response = HttpResponse(content_type=presentation.content_type)
    disposition = get_content_disposition(
        report.name,
        presentation.filename_extension)
    response['Content-Disposition'] = disposition

    output = StringIO()
    values = [
        c.alias for value in values for c in report_configuration.columns
        if c.column == value
    ]
    presentation.write_presentation(values, sorted_records, output)
    response.write(output.getvalue())

    return response


@requires('read partner', 'read contact', 'read communication record')
@require_http_methods(['POST'])
def get_default_report_name(request):
    validator = ApiValidator()
    # We don't actually need this but it seems like it will be important
    # if we ever start picking meaningful names.
    report_data_id = request.POST.get('report_data_id')
    if not report_data_id:
        validator.note_field_error(
            "report_data_id",
            "Report data id must not be empty.")

    if validator.has_errors():
        return validator.build_error_response()

    data = {'name': str(datetime.now())}
    return HttpResponse(content_type='application/json',
                        content=json.dumps(data))


@requires('read partner', 'read contact', 'read communication record')
@require_http_methods(['GET'])
def old_report_preview(request):
    company = get_company_or_404(request)
    report_id = request.GET.get('id', 0)
    report = get_object_or_404(DynamicReport, pk=report_id)
    report_type = report.report_data.report_type.report_type

    if report_type == 'communication-records':
        driver = ds_json_drivers['comm_records']
        ds_filter = driver.build_filter(report.filters)
        records = driver.ds.filtered_query_set(company, ds_filter)

        ctx = {
            'emails': records.emails,
            'calls': records.calls,
            'searches': records.searches,
            'meetings': records.meetings,
            'applications': records.applications,
            'interviews': records.interviews,
            'hires': records.hires,
            'communications': records.communication_activity.count(),
            'referrals': records.referrals,
            'contacts': list(records.contacts),
        }
        return HttpResponse(content_type='application/json',
                            content=json.dumps(ctx))
    elif report_type in ['contacts', 'partners']:
        return HttpResponse(content_type='application/json',
                            content=report.json)


@requires('read partner', 'read contact', 'read communication record')
@require_http_methods(['POST'])
def refresh_report(request):
    company = get_company_or_404(request)
    report_id = request.POST['report_id']
    report = get_object_or_404(DynamicReport, owner=company, pk=report_id)
    report.regenerate()
    return HttpResponse(content_type='application/json',
                        content='{}')
