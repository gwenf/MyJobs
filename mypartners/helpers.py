from collections import namedtuple
from datetime import datetime, time
import json
import os
from urlparse import urlparse, parse_qsl, urlunparse
from urllib import urlencode

from django.db.models import Min, Max, Q, Model
from django.core.serializers.json import DjangoJSONEncoder
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django.utils.text import get_text_list, force_unicode, force_text
from django.utils.timezone import now
from django.utils.translation import ugettext
from lxml import html
from lxml.cssselect import CSSSelector
import requests

from universal import states
from universal.helpers import (get_domain, get_company, get_company_or_404,
                               get_int_or_none, send_email)
from mypartners.models import (Contact, ContactLogEntry, CONTACT_TYPE_CHOICES,
                               CHANGE, Location, Partner, PartnerLibrary, Tag)
from mypartners.widgets import MultipleFileField


def prm_worthy(request):
    """
    Makes sure the User is worthy enough to use PRM.

    """
    company = get_company(request)
    if company is None:
        raise Http404

    partner_id = get_int_or_none(request.REQUEST.get('partner'))
    partner = get_object_or_404(company.partner_set, id=partner_id)

    return company, partner, request.user


def add_extra_params(url, extra_urls):
    """
    Adds extra parameters to a url

    Inputs:
    :url: Url that parameters will be added to
    :extra_urls: Extra parameters to be added

    Outputs:
    :url: Input url with parameters added
    """
    extra_urls = extra_urls.lstrip('?&')
    new_queries = dict(parse_qsl(extra_urls, keep_blank_values=True))

    # By default, extra parameters besides vs are discarded by the redirect
    # server. We can get around this by adding &z=1 to the url, which enables
    # custom query parameter overrides.
    new_queries['z'] = '1'

    parts = list(urlparse(url))
    query = dict(parse_qsl(parts[4], keep_blank_values=True))
    query.update(new_queries)
    parts[4] = urlencode(query)
    return urlunparse(parts)


def add_extra_params_to_jobs(items, extra_urls):
    """
    Adds extra parameters to all jobs in a list

    Inputs:
    :items: List of jobs to which extra parameters should be added
    :extra_urls: Extra parameters to be added

    Modifies:
    :items: List is mutable and is modified in-place
    """
    for item in items:
        item['link'] = add_extra_params(item['link'], extra_urls)


def log_change(obj, form, user, partner, contact_identifier,
               action_type=CHANGE, change_msg=None, successful=None):
    """
    Creates a ContactLogEntry for obj.

    inputs:
    :obj: The object a log entry is being created for
    :form: The form the log entry is being created from. This is optional,
        but without it a valuable change message can't be created, so either
        one will need to be passed to the function or there won't be a change
        message for this log entry.
    :user: The user who caused the change. Can be null, but shouldn't be unless
        in most cases.
    :partner: The partner this object applies to. Should never be null.
    :contact_identifier: Some meaningful piece of information (e.g. name,
        email, phone number) that identifies the person being contacted.
    :action_type: The action being taken. Available types are in
        mypartners.models.
    :change_msg: A short description of the changes made. If one isn't
                 provided, the change_msg will attempt to be created from the
                 form.

    """
    if not change_msg:
        change_msg = get_change_message(form) if action_type == CHANGE else ''
    delta = get_form_delta(form) if action_type == CHANGE else {}
    delta = json.dumps(delta, cls=DjangoJSONEncoder)

    ContactLogEntry.objects.create(
        action_flag=action_type,
        change_message=change_msg,
        contact_identifier=contact_identifier,
        content_type=ContentType.objects.get_for_model(obj),
        delta=delta,
        object_id=obj.pk,
        object_repr=force_text(obj)[:200],
        partner=partner,
        user=user,
        successful=successful,
    )


def get_form_delta(form):
    """
    Determines the changes made by a newly submitted form. Provided delta
    values should be at least semi-human readable.

    :param form: The form that is being checked for changes.
    :return: A dictionary of changes. The format is:
                {
                    form_field_name: {
                        'initial': The starting value,
                        'new':  The updated value,
                    }
                }

    """
    delta = {}

    for field in form.changed_data:
        initial = form.initial.get(field, form.fields[field].initial)
        new = form.cleaned_data.get(field)

        if isinstance(form.fields[field], MultipleFileField):
            initial = [fd.name for fd in initial or [] if fd]
            new = [fd.name for fd in new or [] if fd]

        if initial or new:
            # do not return complete models for foreign keys, only PK
            def convert_object(x):
                return x.pk if isinstance(x, Model) else x
            delta[field] = {'initial': convert_object(initial), 'new': convert_object(new)}

    return delta


def get_change_message(form):
    """
    Creates a list of changes made from a form.

    """
    change_message = []
    if not form:
        return ''

    if form.changed_data:
        change_message = (ugettext('Changed %s.') %
                          get_text_list(form.changed_data, ugettext('and')))
    return change_message or ugettext('No fields changed.')


def get_attachment_link(partner_id, attachment_id, attachment_name):
    """
    Creates a link (html included) to a PRMAttachment.

    """
    url = '/prm/download?partner=%s&id=%s' % (partner_id, attachment_id)

    link = "<a href='{url}' target='_blank'>{attachment_name}</a>"
    return mark_safe(link.format(url=url, attachment_name=attachment_name))


def retrieve_fields(model):
    fields = [field for field in model._meta.get_all_field_names()
              if unicode(field) not in [u'id', u'prmattachment']]
    return fields


def contact_record_val_to_str(value):
    """
    Translates a field value from a contact record into a human-readable
    string.  Dates are formatted "ShortMonth Day, Year Hour:Minute AMorPM"
    Times are formatted "XX Hours XX Minutes" If the value matches a contact
    type choice it's translated to the verbose form.
    """
    value = (value.strftime('%b %d, %Y %I:%M %p') if type(value)
             is datetime else value.strftime('%H hours %M minutes')
             if type(value) is time else force_unicode(value))

    contact_types = dict(CONTACT_TYPE_CHOICES)
    if value in contact_types:
        value = contact_types[value]

    return value


def get_records_from_request(request):
    """
    Filters a list of records on partner, date_time, contact.name, and
    contact_type based on the request

    outputs:
    The date range filtered on, A string "X Day(s)" representing the
    date filtered on, and the filtered records.
    """
    sort_types = {
        'name': 'contact__name', 'date': 'date_time', None: 'date_time'}
    _, partner, _ = prm_worthy(request)
    # extract reelvant values from the request object
    contact, contact_type, admin, range_start, range_end, sort_by, desc = [
        request.REQUEST.get(field) for field in [
            'contact', 'contact_type', 'admin', 'date_start', 'date_end',
            'sort_by', 'desc']]

    tags = [tag.strip()
            for tag in request.REQUEST.get('tags', '').split(',') if tag]
    keywords = [keyword.strip() for keyword in request.REQUEST.get(
        'keywords', '').split(',') if keyword]

    if not sort_by and not desc:
        sort_by = 'date'
        desc = '-'
    else:
        desc = '-' if desc else ''

    if range_start:
        range_start = datetime.strptime(range_start, '%m/%d/%Y').date()

    if range_end:
        range_end = datetime.strptime(range_end, '%m/%d/%Y').date()

    records = partner.get_contact_records(
        contact_name=contact, record_type=contact_type, created_by=admin,
        order_by=desc + sort_types[sort_by], date_start=range_start,
        date_end=range_end, tags=tags, keywords=keywords)

    if range_start or range_end:
        days = ((range_end or now().date()) -
                (range_start or now().date())).days
        date_str = '%i Day%s' % (days, '' if days == 1 else 's')
    else:
        date_str = 'View All'

    return (range_start, range_end), date_str, records


def send_contact_record_email_response(created_records, created_contacts,
                                       attachment_failures, unmatched_contacts,
                                       error, to_email):
    ctx = {
        'created_records': created_records,
        'created_contacts': created_contacts,
        'error': error,
        'unmatched_contacts': unmatched_contacts,
        'attachment_failures': attachment_failures,
    }

    message = render_to_string('mypartners/email/email_response.html',
                               ctx)
    headers = {
        'X-SMTPAPI': '{"category": "Communication Record %s"}' % (
            'Failure' if error is not None else 'Success')
    }

    send_email(message, email_type=settings.CREATE_CONTACT_RECORD,
               recipients=[to_email], headers=headers)


def find_partner_from_email(partner_list, email):
    """
    Finds a possible partner based on the email domain.

    inputs:
    :partner_list: The partner list to compare the email against.
    :email: The email address the domain is needed for.

    outputs:
    A matching partner if there is one, otherwise None.

    """
    if not email or '@' not in email or not partner_list:
        return None
    email_domain = email.split('@')[-1]

    for partner in partner_list:
        url = get_domain(partner.uri)
        # Pass through get_domain() to strip subdomains
        email_domain = get_domain(email_domain)

        if email_domain and url and email_domain.lower() == url.lower():
            return partner

    return None


def get_library_partners(url, params=None):
    """
    Returns a generator that yields `CompliancePartner` objects, which can then
    be added to the PartnerLibrary table in the database. At the moment, this
    function assumes data to be in a table that mimicks the output of the
    "Export to Excel" button used at wwww.dol-esa.gov/errd/directory.jsp.

    Inputs:
    :url: The post url (str) used to generate the data.
    :params: POST data (dict) passed to the :url:

    Outputs:
    A generator of `CompliancePartner` objects, whose attributes map directly
    with the excel table.
    """

    if os.path.isfile(url):
        tree = html.parse(url)
    else:
        params = params or {}
        response = requests.post(url, params=params)
        tree = html.fromstring(response.text)

    # convert column headers to valid Python identifiers, and rename duplicates
    cols = []
    for header in CSSSelector("p ~ table th")(tree):
        col = header.text.lower()
        if col in cols:
            cols.append(col[:2])
        else:
            cols.append(col.replace(" ", "_"))

    CompliancePartner = namedtuple("CompliancePartner", cols)
    for row in CSSSelector("p ~ table tr")(tree):
        fields = dict((cols[i], (td.text or "").strip()) for i, td in
                      enumerate(CSSSelector("td")(row)))

        # convert column headers to valid Python identifiers
        for column, value in fields.items():
            if value in [u"\xa0", None]:
                fields[column] = ""
            elif value == "Y":
                fields[column] = True
            elif value == "N":
                fields[column] = False

            # coerce these to bools if they are empty strings
            if column in ["minority", "female", "disabled", "veteran",
                          "disabled_veteran", "exec_om", "first_om",
                          "professional", "technician", "sales",
                          "admin_support", "craft", "operative", "labor",
                          "service"]:
                fields[column] = bool(value)

        if len(fields) > 1:
            yield CompliancePartner(**fields)


def filter_partners(request, partner_library=False):
    """
    Advanced partner filtering.

    If True, the partner_library parameter will determine whether or not the
    OFCCP Partner Library should be filtered for results instead of the current
    company's manually created partners.

    The following request parameters may be used to manipulate the results:

        keywords
            A comma-separated string of keywords which are checked against the
            partner name, contact name and URI.
        city
            The city in which the partner is located.
        state
            The state in which the partner is located.

    When partner_library is True, the following parameter is also available:

        special_interest
            An array of special interest groups to which the partner belongs.
            Possible values are 'minority', 'female', 'disabled', 'veteran',
            and 'disabled_veteran'.

    In addition to filtering, the following sort parameters may be passed:

        desc
            Any truthy string passed along here will indicate to this function
            that the result list should be sorted descending.
        sort_by
            Determines which column is used to sort the results. Officially,
            only 'location'-- which sorts by city and state-- and name -- which
            sorts by partner name -- are allowed.
    """
    company = get_company_or_404(request)

    sort_order = "-" if request.REQUEST.get("desc", False) else ""
    sort_by = sort_order + request.REQUEST.get('sort_by', 'name')
    city = request.REQUEST.get('city', '').strip()
    state = request.REQUEST.get('state', '').strip()
    tags = [tag.strip()
            for tag in request.REQUEST.get('tags', '').split(',') if tag]
    keywords = [keyword.strip() for keyword in request.REQUEST.get(
        'keywords', '').split(',') if keyword]

    if partner_library:
        special_interest = [
            si if si != "disability" else "disabled"
            for si in request.REQUEST.getlist('special_interest')]

        library_ids = Partner.objects.filter(owner=company).exclude(
            library__isnull=True).values_list('library', flat=True)
        # hide partners that the user has already added
        partners = PartnerLibrary.objects.exclude(id__in=library_ids)
        contact_city = 'city'
        contact_state = 'st'

        unspecified = Q()
        interests = Q()
        order_by = ['is_veteran', 'is_female', 'is_minority', 'is_disabled',
                    'is_disabled_veteran']

        if "unspecified" in special_interest:
            special_interest.remove("unspecified")
            unspecified = Q(is_veteran=False, is_female=False,
                            is_minority=False, is_disabled=False,
                            is_disabled_veteran=False)

        for interest in special_interest:
            interests &= Q(**{"is_%s" % interest.replace(' ', '_'): True})

        query = Q(interests | unspecified)
    else:
        start_date = request.REQUEST.get('start_date')
        end_date = request.REQUEST.get('end_date')

        partners = Partner.objects.prefetch_related('contact_set')
        contact_city = 'contact__locations__city'
        contact_state = 'contact__locations__state'
        sort_by.replace('city', 'contact__locations__city')
        order_by = []

        query = Q(owner=company.id)

        # If both start and end date are passed, we should filter, creating
        # reasonable bounds for either one if they are missing. Otherwise, we
        # don't filter by either.
        if any([start_date, end_date]):
            start_date = datetime.strptime(
                start_date or '11/30/1899', '%m/%d/%Y')
            end_date = datetime.strptime(
                end_date or datetime.now().strftime('%m/%d/%Y'), '%m/%d/%Y')
            end_date = end_date.replace(hour=23, minute=59, second=59)
            query &= Q(contactrecord__date_time__range=[start_date, end_date])

    for keyword in keywords:
        query &= (Q(name__icontains=keyword) | Q(uri__icontains=keyword) |
                  Q(contact__name__icontains=keyword,
                    contact__archived_on__isnull=True) |
                  (Q(email__icontains=keyword) if partner_library else
                   Q(contact__email__icontains=keyword,
                     contact__archived_on__isnull=True)))

    if city:
        if partner_library:
            query &= Q(**{'%s__icontains' % contact_city: city})
        else:
            query &= Q(**{'%s__icontains' % contact_city: city,
                          'contact__archived_on__isnull': True})

    if state:

        state_query = Q()
        if partner_library:
            for synonym in states.synonyms[state.strip().lower()]:
                state_query |= Q(**{'%s__iexact' % contact_state: synonym})
        else:
            for synonym in states.synonyms[state.strip().lower()]:
                state_query |= Q(**{'%s__iexact' % contact_state: synonym,
                                    'contact__archived_on__isnull': True})

        query &= state_query

    partners = partners.distinct().filter(query)

    # filter by tags
    for tag in tags:
        partners = partners.filter(Q(tags__name__icontains=tag) |
                                   Q(contact__tags__name__icontains=tag))

    if "location" in sort_by:
        if partner_library:
            # no foreign keys, so we can do the "right" thing
            partners = partners.extra(select={
                'no_city': "LENGTH(state) = 0",
                'no_state': "LENGTH(city) = 0"}).order_by(
                    *['%s%s' % (sort_order, column)
                      for column in ['state', 'city', 'no_state', 'no_city']])
        else:
            null_locations = (Q(contact__locations__state='',
                                contact__archived_on__isnull=True) |
                              Q(contact__locations__isnull=True,
                                contact__archived_on__isnull=True))

            with_locations = partners.exclude(
                null_locations).order_by(
                    '%scontact__locations__state' % sort_order,
                    '%scontact__locations__city' % sort_order,
                    '%sname' % sort_order)

            without_locations = partners.filter(
                null_locations).order_by('%sname' % sort_order)

            partners = list(with_locations) + list(without_locations)

    elif "activity" in sort_by:
        if sort_order:
            partners = partners.annotate(
                earliest_activity=Min('contactrecord__date_time')).order_by(
                    '-earliest_activity')
        else:
            partners = partners.annotate(
                latest_activity=Max('contactrecord__date_time')).order_by(
                    'latest_activity')
    else:
        partners = partners.order_by(*[sort_by] + order_by)

    return list(partners)


def new_partner_from_library(request):
    company = get_company_or_404(request)

    try:
        library_id = int(request.REQUEST.get('library_id') or 0)
    except ValueError:
        raise Http404
    library = get_object_or_404(PartnerLibrary, pk=library_id)

    tags = []
    for interest, color in [('disabled_veteran', '659274'),
                            ('female', '4BB1CF'),
                            ('minority', 'FAA732'),
                            ('veteran', '5EB94E')]:

        if getattr(library, 'is_%s' % interest):
            tag, _ = Tag.objects.get_or_create(
                company=company, name=interest.replace('_', ' ').title(),
                defaults={'hex_color': color})
            tags.append(tag)

    if library.is_disabled:
        # rename the tag on the front end
        tag, _ = Tag.objects.get_or_create(
            company=company, name="Disability",
            defaults={'hex_color': '808A9A'})
        tags.append(tag)

    partner = Partner.objects.create(
        name=library.name,
        uri=library.uri,
        owner=company,
        library=library,
        data_source=library.data_source)
    partner.tags = tags

    state = request.GET.get("state", library.st)
    location = Location.objects.create(
        address_line_one=library.street1,
        address_line_two=library.street2,
        city=library.city,
        state=state,
        country_code="USA",
        postal_code=library.zip_code)

    contact = Contact.objects.create(
        partner=partner,
        library=library,
        name=library.contact_name or "Not Available",
        email=library.email,
        phone=library.phone,
        notes=("This contact was generated from content in the "
               "OFCCP directory."))

    contact.locations.add(location)
    contact.tags = tags
    contact.save()

    partner.primary_contact = contact
    partner.save()

    return partner


def tag_get_or_create(company_id, data):
    tags = []
    for tag in data:
        obj, _ = Tag.objects.get_or_create(
            company_id=company_id, name__iexact=tag, defaults={"name": tag})
        tags.append(obj.id)

    return tags
