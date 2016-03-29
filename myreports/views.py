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

from myreports.helpers import humanize, serialize
from myjobs.decorators import requires
from myreports.models import (
    Report, ReportingType, ReportType, ReportPresentation, DynamicReport,
    DataType, ReportTypeDataTypes)
from myreports.presentation import presentation_drivers
from myreports.presentation.disposition import get_content_disposition
from postajob import location_data
from universal.helpers import get_company_or_404
from universal.decorators import restrict_to_staff

from myreports.datasources import ds_json_drivers

from cStringIO import StringIO


@requires('read partner', 'read contact', 'read communication record')
def overview(request):
    """The Reports app landing page."""
    company = get_company_or_404(request)

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
        html = render_to_response('myreports/includes/report_overview.html',
                                  ctx, RequestContext(request)).content
        response.content = html
        return response

    return render_to_response('myreports/reports.html', ctx,
                              RequestContext(request))


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


@restrict_to_staff()
@requires('read partner', 'read contact', 'read communication record')
@require_http_methods(['GET'])
def dynamicoverview(request):
    """The Dynamic Reports page."""
    return render_to_response('myreports/dynamicreports.html', {},
                              RequestContext(request))


@restrict_to_staff()
@requires('read partner', 'read contact', 'read communication record')
@require_http_methods(['POST'])
def reporting_types_api(request):
    """Get a list of reporting types for this user."""
    reporting_types = (ReportingType.objects
                       .active_for_user(request.user))

    def entry(reporting_type):
        return (str(reporting_type.id),
                {'name': reporting_type.reporting_type,
                 'description': reporting_type.description})

    data = {'reporting_type':

            dict(entry(rt) for rt in reporting_types)}
    return HttpResponse(content_type='application/json',
                        content=json.dumps(data))


@restrict_to_staff()
@requires('read partner', 'read contact', 'read communication record')
@require_http_methods(['POST'])
def report_types_api(request):
    """Get a list of report types

    reporting_type_id: reporting type id from earlier call
    """
    reporting_type_id = request.POST['reporting_type_id']
    report_types = (ReportType.objects
                    .active_for_reporting_type(reporting_type_id))

    def entry(report_type):
        return (str(report_type.id),
                {'name': report_type.report_type,
                 'description': report_type.description})

    data = {'report_type':
            dict(entry(rt) for rt in report_types)}
    return HttpResponse(content_type='application/json',
                        content=json.dumps(data))


@restrict_to_staff()
@requires('read partner', 'read contact', 'read communication record')
@require_http_methods(['POST'])
def data_types_api(request):
    """Get a list of data types

    report_type_id: report type id from earlier call
    """
    report_type_id = request.POST['report_type_id']
    data_types = (DataType.objects
                  .active_for_report_type(report_type_id))

    def entry(data_type):
        return (str(data_type.id),
                {'name': data_type.data_type,
                 'description': data_type.description})

    data = {'data_type':
            dict(entry(rt) for rt in data_types)}
    return HttpResponse(content_type='application/json',
                        content=json.dumps(data))


@restrict_to_staff()
@requires('read partner', 'read contact', 'read communication record')
@require_http_methods(['POST'])
def presentation_types_api(request):
    """Get a list of presentation types

    report_type_id: report type id from earlier call
    data_type_id: data type id from earlier call
    """
    report_type_id = request.POST['report_type_id']
    data_type_id = request.POST['data_type_id']
    rpdt = (ReportTypeDataTypes.objects
            .get(report_type_id=report_type_id,
                 data_type_id=data_type_id))
    rps = (ReportPresentation.objects
           .active_for_report_type_data_type(rpdt))

    def entry(rp):
        return (str(rp.id),
                {'name': rp.display_name})

    data = {'report_presentation':
            dict(entry(rp) for rp in rps)}
    return HttpResponse(content_type='application/json',
                        content=json.dumps(data))


@restrict_to_staff()
@requires('read partner', 'read contact', 'read communication record')
@require_http_methods(['POST'])
def filters_api(request):
    """Get a list of filters for the UI.

    rp_id: Report Presentation ID

    response: See ContactsJsonDriver.encode_filter_interface()
    """
    request_data = request.POST
    rp_id = request_data['rp_id']
    report_pres = ReportPresentation.objects.get(id=rp_id)
    datasource = report_pres.report_data.report_type.datasource

    report_configuration = (report_pres.configuration.build_configuration())

    driver = ds_json_drivers[datasource]
    result = driver.encode_filter_interface(report_configuration)

    return HttpResponse(content_type='application/json',
                        content=json.dumps(result))


@requires('read partner', 'read contact', 'read communication record')
@require_http_methods(['POST'])
def help_api(request):
    """Get help for a partially filled out field.

    rp_id: Report Presentation ID
    filter: JSON string with user filter to use
    field: Name of field to get help for
    partial: Data entered so far

    response: [{'key': data, 'display': data to display}]
    """
    company = get_company_or_404(request)
    request_data = request.POST
    rp_id = request_data['rp_id']
    filter_spec = request_data['filter']
    field = request_data['field']
    partial = request_data['partial']

    report_pres = ReportPresentation.objects.get(id=rp_id)
    datasource = report_pres.report_data.report_type.datasource
    driver = ds_json_drivers[datasource]

    result = driver.help(company, filter_spec, field, partial)

    return HttpResponse(content_type="application/json",
                        content=json.dumps(result))


@requires('read partner', 'read contact', 'read communication record')
@require_http_methods(['POST'])
def run_dynamic_report(request):
    """Run a dynamic report.

    rp_id: Report Presentation ID
    name: name of report
    filter_spec: JSON string with user filter to use

    response: {'id': new dynamic report id}
    """
    company = get_company_or_404(request)
    rp_id = request.POST['rp_id']
    name = request.POST['name']
    filter_spec = request.POST.get('filter', '{}')
    report_pres = ReportPresentation.objects.get(id=rp_id)

    report = DynamicReport.objects.create(
        report_presentation=report_pres,
        filters=filter_spec,
        name=name,
        owner=company)

    report.regenerate()
    report.save()

    data = {'id': report.id}
    return HttpResponse(content_type='application/json',
                        content=json.dumps(data))


@restrict_to_staff()
@requires('read partner', 'read contact', 'read communication record')
@require_http_methods(['GET'])
def list_dynamic_reports(request):
    """Get a list of dynamic report runs for this user."""
    company = get_company_or_404(request)

    reports = (
        DynamicReport.objects
        .filter(owner=company)
        .order_by('-pk')[:10])

    data = [{'id': r.id, 'name': r.name}
            for r in reports]
    return HttpResponse(content_type='application/json',
                        content=json.dumps({'reports': data}))


@requires('read partner', 'read contact', 'read communication record')
@require_http_methods(['GET'])
def download_dynamic_report(request):
    """
    Download dynamic report as CSV.

    Query String Parameters:
        :id: ID of the report to download
        :values: Fields to include in the resulting CSV, as well as the order
                 in which to include them.
        :order_by: The sort order for the resulting CSV.

    Outputs:
        The report with the specified options rendered as a CSV file.
    """

    # SECURITY: check report_id vs company owner!!!
    report_id = request.GET.get('id', 0)
    values = request.GET.getlist('values', None)
    order_by = request.GET.get('order_by', None)

    report = get_object_or_404(DynamicReport, pk=report_id)
    report_configuration = (
            report.report_presentation
            .configuration.build_configuration())

    if order_by:
        report.order_by = order_by
        report.save()

    values = report_configuration.get_header()
    records = [report_configuration.format_record(r) for r in report.python]

    presentation_driver = (
        report.report_presentation.presentation_type.presentation_type)
    presentation = presentation_drivers[presentation_driver]
    response = HttpResponse(content_type=presentation.content_type)
    disposition = get_content_disposition(
        report.name,
        presentation.filename_extension)
    response['Content-Disposition'] = disposition

    output = StringIO()
    presentation.write_presentation(values, records, output)
    response.write(output.getvalue())

    return response
