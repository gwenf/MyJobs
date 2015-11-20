import csv
import json
import operator
from datetime import datetime
from collections import Counter, OrderedDict
from itertools import groupby

from django.conf import settings
from django.contrib.auth.decorators import user_passes_test
from django.core import mail
from django.db.models import Q
from django.http import Http404, HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response


from universal.helpers import (get_company, get_domain, get_int_or_none,
                               sequence_to_dict)
from mydashboard.helpers import (saved_searches, filter_by_microsite,
                                 filter_by_date, apply_facets_and_filters,
                                 parse_facets, remove_param_from_url,
                                 get_company_microsites, analytics,
                                 get_analytics_counts, filter_by_domain)
from seo.models import Company, CompanyUser
from myjobs.models import User
from myprofile.models import PrimaryNameProfileUnitManager, ProfileUnits
from mysearches.models import SavedSearch
from solr.helpers import Solr, dict_to_object

from endless_pagination.decorators import page_template
from urlparse import urlparse
from lxml import etree


@page_template("mydashboard/dashboard_activity.html")
@user_passes_test(lambda u: User.objects.is_group_member(u, 'Employer'))
def dashboard(request, template="mydashboard/mydashboard.html",
              extra_context=None):
    """
    Returns a list of candidates who created a saved search for one of the
    microsites within the company microsite list or with the company name like
    jobs.jobs/company_name/careers for example between the given (optional)
    dates

    Inputs:
    :company:               company.id that is associated with request.user

    Returns:
    :render_to_response:    renders template with context dict

    """
    if hasattr(mail, 'outbox'):
        solr = settings.TEST_SOLR_INSTANCE
    else:
        solr = settings.SOLR

    company = get_company(request)
    if not company:
        raise Http404

    user_solr = Solr(solr['current'])
    facet_solr = Solr(solr['current'])

    # Add join only if we're using facets, not if we're simply searching.
    query_params = {'search', 'company'}
    if not query_params.issuperset({q_key for q_key in request.GET.keys()
                                    if q_key not in ['querystring_key',
                                                     'date_end', 'date_start',
                                                     'page']}):
        user_solr = user_solr.add_join(from_field='ProfileUnits_user_id',
                                       to_field='User_id')
    facet_solr = facet_solr.add_join(from_field='User_id',
                                     to_field='ProfileUnits_user_id')
    facet_solr = facet_solr.rows_to_fetch(0)

    authorized_microsites, buids = get_company_microsites(company)

    # roles are only enabled during development
    if settings.ROLES_ENABLED:
        admins = User.objects.filter(roles__company=company)
    else:
        admins = User.objects.filter(company=company)

    admins = admins.exclude(pk=request.user.pk)
    requested_microsite = request.REQUEST.get('microsite', '')
    requested_date_button = request.REQUEST.get('date_button', False)
    candidates_page = request.REQUEST.get('page', 1)

    # the url value for 'All' in the select box is company name
    # which then gets replaced with all microsite urls for that company
    site_name = ''
    if requested_microsite != '':
        active_microsites = authorized_microsites.filter(
            domain__startswith=requested_microsite)
        user_solr, facet_solr = filter_by_domain(requested_microsite,
                                                 user_solr, facet_solr)
    else:
        active_microsites = authorized_microsites
        site_name = company.name
    if not site_name:
        try:
            site_name = active_microsites[0]
        except IndexError:
            site_name = ''
    active_microsites = set(active_microsites)

    rng, date_start, date_end, date_display = filter_by_date(request)
    user_solr = user_solr.add_filter_query(rng)
    facet_solr = facet_solr.add_query(rng)

    if request.GET.get('search', False):
        user_solr = user_solr.add_query("%s" % request.GET['search'])
        facet_solr = facet_solr.add_query("%s" % request.GET['search'])

    user_solr, facet_solr = filter_by_microsite(company, user_solr, facet_solr)

    (user_solr, facet_solr, filters) = apply_facets_and_filters(
        request, user_solr, facet_solr)

    solr_results = user_solr.rows_to_fetch(100).search()

    # List of dashboard widgets to display.
    dashboard_widgets = ["home_views", "search_views", "job_views",
                         "apply_clicks", "candidates", "search",
                         "applied_filters", "filters"]

    # Date button highlighting
    if 'today' in request.REQUEST:
        requested_date_button = 'today'
    elif 'seven_days' in request.REQUEST:
        requested_date_button = 'seven_days'
    elif 'thirty_days' in request.REQUEST:
        requested_date_button = 'thirty_days'

    url = request.build_absolute_uri()
    facets = parse_facets(facet_solr.search(), request)

    context = {
        'admin_you': request.user,
        'applied_filters': filters,
        'candidates_page': candidates_page,
        'company_admins': admins,
        'company_id': company.id,
        'company_microsites': authorized_microsites,
        'company_name': company.name,
        'dashboard_widgets': dashboard_widgets,
        'date_button': requested_date_button,
        'date_display': date_display,
        'date_end': date_end,
        'date_start': date_start,
        'date_submit_url': url,
        'facets': facets,
        'site_name': site_name,
        'view_name': 'Company Dashboard',
    }

    results = solr_results.docs

    facet_var_map = {
        'home': 'home',
        'listing': 'job_view',
        'results': 'search',
        'redirect': 'apply',
    }
    analytics_solr = Solr(solr['current']).add_facet_field(
        'page_category')
    if requested_microsite:
        analytics_solr = analytics_solr.add_query('domain:%s' %
                                                  requested_microsite)
    else:
        analytics_solr = analytics_solr.add_query('company_id:%d' % company.pk)

    rng = filter_by_date(request, field='view_date')[0]
    analytics_solr = analytics_solr.add_filter_query(rng)

    all_results = analytics_solr.rows_to_fetch(0).search()
    analytics_facets = all_results.facets.get('facet_fields', {}).get(
        'page_category', [])
    facet_dict = sequence_to_dict(analytics_facets)
    for key in facet_dict.keys():
        context_key = 'total_%s' % facet_var_map.get(key, '')
        context[context_key] = facet_dict[key]

    analytics_solr = analytics_solr.add_filter_query('User_id:[* TO *]')
    analytics_solr = analytics_solr.add_facet_field('domain')

    auth_results = analytics_solr.search()
    analytics_facet_list = auth_results.facets.get(
        'facet_fields', {}).get('domain', [])

    analytics_facets = sequence_to_dict(analytics_facet_list)
    analytics_facets = [domain for domain in analytics_facets.items()
                        if domain[0] in active_microsites]

    results += auth_results.docs

    candidates = dict_to_object(results)

    domains = [get_domain(c.SavedSearch_feed) for c in candidates
               if hasattr(c, 'SavedSearch_feed')]
    search_facets = [(domain, domains.count(domain)) for domain in set(domains)]

    domain_facets = {}
    for domain, group in groupby(analytics_facets + search_facets,
                                 key=lambda x: x[0]):
        domain_facets[domain] = sum(item[1] for item in group)

    candidate_list = sorted(candidates,
                            key=lambda y: y.SavedSearch_created_on
                            if hasattr(y, 'SavedSearch_created_on')
                            else y.view_date,
                            reverse=True)

    context['domain_facets'] = domain_facets
    context['candidates'] = candidate_list
    context['total_candidates'] = len([x for x in groupby(
        candidate_list, key=lambda y: y.User_id)])

    if extra_context is not None:
        context.update(extra_context)
    return render_to_response(template, context,
                              context_instance=RequestContext(request))


@user_passes_test(lambda u: User.objects.is_group_member(u, 'Employer'))
def candidate_information(request):
    """
    Sends user info, primary name, and searches to candidate_information.html.
    Gathers the employer's (request.user) companies and microsites and puts
    the microsites' domains in a list for further checking and logic,
    see helpers.py.

    """
    user_id = get_int_or_none(request.REQUEST.get('user'))
    company = get_company(request)

    if not user_id or not company:
        raise Http404

    # user gets pulled out from id
    try:
        candidate = User.objects.get(id=user_id)
    except User.DoesNotExist:
        raise Http404

    if not candidate.opt_in_employers:
        raise Http404

    urls = saved_searches(request.user, company, candidate)
    actions = analytics(request.user, company, candidate)
    actions = get_analytics_counts(actions)

    if not urls and not actions:
        raise Http404

    manager = PrimaryNameProfileUnitManager(order=['employmenthistory',
                                                   'education',
                                                   'militaryservice'])
    models = manager.displayed_units(candidate.profileunits_set.all())

    primary_name = getattr(manager, 'primary_name', 'Name not given')

    coming_from = {'path': 'view'}

    searches = candidate.savedsearch_set.all()
    searches = [search for search in searches
                if get_domain(search.feed).lower() in urls]

    modified_url = remove_param_from_url(request.build_absolute_uri(), 'user')
    query_string = "?%s" % urlparse(modified_url).query

    data_dict = {
        'user_info': models,
        'company_id': company.pk,
        'primary_name': primary_name,
        'the_user': candidate,
        'searches': searches,
        'coming_from': coming_from,
        'query_string': query_string,
        'actions': actions,
    }

    return render_to_response('mydashboard/candidate_information.html',
                              data_dict, RequestContext(request))


@user_passes_test(lambda u: User.objects.is_group_member(u, 'Employer'))
def export_candidates(request):
    """
    This function will be handling which export type to execute.
    Only function accessible through url.
    """
    export_type = request.GET['ex-t']
    try:
        if export_type == 'csv':
            candidates = filter_candidates(request)
            response = export_csv(request, candidates)
        elif export_type == 'xml' or export_type == 'json':
            candidates = filter_candidates(request)
            response = export_hr(request, candidates, export_type)
    except Exception, e:
        raise Http404
    return response


def filter_candidates(request):
    """
    Some default filtering for company/microsite. This function will
    be changing with solr docs update and filtering addition.
    """
    candidates = []
    company_id = request.REQUEST.get('company')
    try:
        company = Company.objects.get(id=company_id)
    except Company.DoesNotExist:
        raise Http404

    authorized_microsites, buids = get_company_microsites(company)

    requested_microsite = request.REQUEST.get('microsite', company.name)
    # the url value for 'All' in the select box is company name
    # which then gets replaced with all microsite urls for that company
    site_name = ''
    if requested_microsite != company.name:
        if requested_microsite.find('//') == -1:
            requested_microsite = '//' + requested_microsite
        active_microsites = authorized_microsites.filter(
            domain__contains=requested_microsite)

    else:
        active_microsites = authorized_microsites
        site_name = company.name

    if not site_name:
        try:
            site_name = active_microsites[0]
        except IndexError:
            site_name = ''

    q_list = [Q(url__contains=ms) for ms in active_microsites]

    # All searches saved on the employer's company microsites
    candidate_searches = SavedSearch.objects.select_related('user')

    # Specific microsite searches saved between two dates
    candidate_searches = candidate_searches.filter(reduce(
        operator.or_, q_list)).exclude(
            user__opt_in_employers=False).order_by('-created_on')
    for search in candidate_searches:
        candidates.append(search.user)
    return list(set(candidates))

def export_csv(request, candidates, models_excluded=[], fields_excluded=[]):
    """
    Exports comma-separated values file. Function is seperated into two parts:
    creation of the header, creating user data.

    Header creation uses a tuple and a Counter to determine the max amount
    of each module type (education, employmenthistory, etc). Then the header
    is created in the format of [model]_[field_name]_[count] excluding models
    and or fields in either lists (models_excluded and fields_excluded). The
    header is always the first line in the csv.

    User data creation iterates through the list of profileunits. The
    profileunits are ordered_by user so when the user changes it prints the
    past user's row and makes a new row for the current user.

    Inputs:
    :candidates:        A set list of Users
    :models_excluded:   List of strings that represents profileunits
                        content_type model names
    :fields_excluded:   List of strings that would target specific fields

    Outputs:
    :response:          Sends a .csv file to the user.
    """

    response = HttpResponse(content_type='text/csv')
    time = datetime.now().strftime('%m%d%Y')
    company_id = request.REQUEST.get('company')
    try:
        company = Company.objects.get(id=company_id)
    except Company.DoesNotExist:
        raise Http404
    response['Content-Disposition'] = ('attachment; filename=' +
                                       company.name+"_DE_"+time+'.csv')
    writer = csv.writer(response)
    models = [model for model in
              ProfileUnits.__subclasses__() if model._meta.module_name
              not in models_excluded]
    model_names = [model._meta.module_name for model in models]
    users_units = ProfileUnits.objects.filter(
        user__in=candidates).select_related('user', 'user__id', 'profileunits',
                                            'content_type__model',
                                            *model_names).order_by('user')
    # Creating header for CSV
    headers = ["primary_email"]
    tup = [(x.user.id, x.content_type.name) for x in users_units]
    tup_counter = Counter(tup)
    final_count = {}
    tup_most_common = tup_counter.most_common()
    for model_name in model_names:
        for counted_model in tup_most_common:
            if (counted_model[0][1].replace(" ", "") == unicode(model_name)
                    and counted_model[0][1].replace(" ", "")
                    not in final_count):
                final_count[model_name] = counted_model[1]
    for model in models:
        module_count = 0
        current_count = 1
        if model._meta.module_name in final_count:
            module_count = final_count[model._meta.module_name]
        while current_count <= module_count:
            models_with_fields = []
            fields = retrieve_fields(model)
            for field in fields:
                if field not in fields_excluded:
                    ufield = model._meta.module_name + "_" + field + "_" + str(
                        current_count)
                else:
                    continue
                if ufield:
                    models_with_fields.append(ufield)
            headers.extend(models_with_fields)
            current_count += 1
    writer.writerow(headers)

    # Making user info rows
    user_fields = []
    temp_user = None
    for unit in users_units:
        user = unit.user
        num = 0
        if user == temp_user:
            continued = True
        else:
            continued = False
            temp_user = user
            del_user_num = candidates.index(temp_user)
            del(candidates[del_user_num])

        if not continued:
            if user_fields:
                writer.writerow(user_fields)
            user_fields = [user.email]
        # Filling in user_fields with default data
        while num > len(headers)-1:
            if not len(user_fields) == len(headers):
                user_fields.append('""')
                num += 1
            else:
                break

        instance = getattr(unit, unit.content_type.name.replace(" ", ""))
        fields = retrieve_fields(instance)

        for field in fields:
            value = getattr(instance, field, u'')
            value = unicode(value).encode('utf8')
            # Find where to put value in user_fields
            n = 1
            position = headers.index(
                unit.content_type.name.replace(" ", "") + "_" + field + "_" +
                str(n))
            while not user_fields[position] == '""':
                n += 1
                position = headers.index(
                    unit.content_type.name.replace(" ", "") + "_" + field +
                    "_" + str(n))
            user_fields[position] = '"%s"' % value.replace('\r\n', '')

        if unit is list(users_units)[-1]:
            writer.writerow(user_fields)

    # Everyone that didn't get included from the above code, doesn't have
    # profileunits. Fill in user_fields with default value.
    for user in candidates:
        user_fields = [user.email]
        for header in headers[1:]:
            user_fields.append('""')
        writer.writerow(user_fields)

    return response


def export_hr(request, candidates, export_type, models_excluded=[]):
    """
    Generates HR-XML or HR-JSON, depending on export_type.

    """
    time = datetime.now().strftime('%m%d%Y')
    company_id = request.REQUEST.get('company')
    try:
        company = Company.objects.get(id=company_id)
    except Company.DoesNotExist:
        raise Http404

    models = [model for model in
              ProfileUnits.__subclasses__() if model._meta.module_name
              not in models_excluded]
    model_names = [model._meta.module_name for model in models]
    users_units = ProfileUnits.objects.filter(
        user__in=candidates).select_related('user', 'user__id', 'profileunits',
                                            'content_type__model', *model_names)

    # initial dict for grouped units
    gu = {}
    for k1, v1 in groupby(users_units, lambda x: x.user):
        pus = []
        for k2, v2 in groupby(v1, lambda x: x.content_type.name):
            pus.append((k2, list(v2)))

        pus = OrderedDict(pus)
        gu[k1] = pus

    if export_type == 'xml':
        root = etree.Element("candidates")
        for user, units in gu.items():
            new_candidate = etree.SubElement(root, "candidate")
            etree.SubElement(new_candidate, "email").text = user.email
            for unit in units.values():
                fields = []
                if len(unit) > 1:
                    name = unit[0].get_verbose().replace(" ", "")
                    if str(name).endswith('y'):
                        name = name[:-1] + "ies"
                    elif str(name).endswith('s'):
                        name += 'es'
                    else:
                        name += 's'
                    xunit = etree.SubElement(new_candidate, name)
                    for u in unit:
                        instance = getattr(
                            u, u.content_type.name.replace(" ", ""))
                        if not fields:
                            fields = retrieve_fields(instance)
                        more_units = etree.SubElement(
                            xunit, u.get_verbose().replace(" ", ""))
                        for field in fields:
                            value = unicode(getattr(instance, field))
                            etree.SubElement(more_units, field).text = value
                else:
                    xunit = etree.SubElement(
                        new_candidate, unit[0].get_verbose().replace(" ", ""))
                    instance = getattr(
                        unit[0], unit[0].content_type.name.replace(" ", ""))
                    fields = retrieve_fields(instance)
                    for field in fields:
                        value = unicode(getattr(instance, field))
                        etree.SubElement(xunit, field).text = value
        response = HttpResponse(etree.tostring(root, pretty_print=True),
                                content_type='application/force-download')
        response['Content-Disposition'] = 'attachment; filename=' + \
                                          company.name + "_DE_"+time+'.xml'
        return response
    elif export_type == 'json':
        full_json = {}
        user_info = {}
        for user, units in gu.items():
            units_info = {}
            for unit in units.values():
                fields = []
                if len(unit) > 1:
                    name = unit[0].get_verbose().replace(" ", "")
                    if str(name).endswith('y'):
                        name = name[:-1] + "ies"
                    else:
                        name += "s"
                    model_info = {}
                    n = 0
                    for model in unit:
                        model_name = model.get_verbose().replace(" ", "")
                        instance = getattr(
                            model, model.content_type.name.replace(" ", ""))
                        if not fields:
                            fields = retrieve_fields(instance)
                        field_info = {}
                        for field in fields:
                            value = unicode(getattr(instance, field))
                            field_info[field] = value
                        n += 1
                        model_info[model_name+str(n)] = field_info
                    units_info[name] = model_info
                else:
                    name = unit[0].get_verbose().replace(" ", "")
                    instance = getattr(
                        unit[0], unit[0].content_type.name.replace(" ", ""))
                    fields = retrieve_fields(instance)
                    field_info = {}
                    for field in fields:
                        value = unicode(getattr(instance, field))
                        field_info[field] = value
                    units_info[name] = field_info
            user_info[user.email] = units_info
        full_json['candidates'] = user_info
        response = HttpResponse(json.dumps(full_json, indent=4),
                                content_type='application/force-download')
        response['Content-Disposition'] = 'attachment; filename=' + \
                                          company.name + "_DE_"+time+'.json'
        return response


def retrieve_fields(instance):
    fields = [field for field in instance._meta.get_all_field_names()
              if unicode(field) not in [u'id', u'user', u'profileunits_ptr',
                                        u'date_created', u'date_updated',
                                        u'content_type']]
    return fields
