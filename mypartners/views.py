import csv
from datetime import datetime, timedelta
import json
from lxml import etree

from collections import OrderedDict
from django.conf import settings
from django.contrib.admin.models import DELETION
from django.contrib.auth.decorators import user_passes_test
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage
from django.core.urlresolvers import reverse
from django.db.models import Count
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse

from myjobs.models import User
from mydashboard.models import Company
from mysearches.models import SavedSearch, PartnerSavedSearch
from mysearches.helpers import url_sort_options, parse_feed
from mysearches.forms import PartnerSavedSearchForm
from mypartners.forms import (PartnerForm, ContactForm, PartnerInitialForm,
                              NewPartnerForm, ContactRecordForm)
from mypartners.models import (Partner, Contact, ContactRecord, PRMAttachment,
                               ContactLogEntry, CONTACT_TYPE_CHOICES,
                               DELETION)
from mypartners.helpers import (prm_worthy, add_extra_params,
                                add_extra_params_to_jobs, log_change,
                                get_searches_for_partner, get_logs_for_partner,
                                get_contact_records_for_partner,
                                contact_record_val_to_str, retrieve_fields,
                                get_records_from_request)

@user_passes_test(lambda u: User.objects.is_group_member(u, 'Employer'))
def prm(request):
    """
    Partner Relationship Manager

    """
    company_id = request.REQUEST.get('company')
    form = request.REQUEST.get('form')
    user = request.user

    if company_id is None:
        try:
            company = Company.objects.filter(admins=request.user)[0]
        except Company.DoesNotExist:
            raise Http404
    else:
        company = get_object_or_404(Company, id=company_id)

    user = request.user
    if not user in company.admins.all():
        raise Http404

    form = request.REQUEST.get('form')
    if not company.partner_set.all():
        has_partners = False
        if not form:
            partner_form = PartnerInitialForm()
        partners = []
    else:
        try:
            partners = Partner.objects.filter(owner=company.id)
        except Partner.DoesNotExist:
            raise Http404
        has_partners = True
        partner_form = None

    ctx = {'has_partners': True if partners else False,
           'partners': partners,
           'form': partner_form or form,
           'company': company,
           'user': user,
           'partner_ct': ContentType.objects.get_for_model(Partner).id,
           'view_name': 'PRM'}

    return render_to_response('mypartners/prm.html', ctx,
                              RequestContext(request))


@user_passes_test(lambda u: User.objects.is_group_member(u, 'Employer'))
def partner_details(request):
    company, partner, user = prm_worthy(request)

    form = PartnerForm(instance=partner, auto_id=False)

    contacts = Contact.objects.filter(partner=partner)
    contact_ct_id = ContentType.objects.get_for_model(Contact).id
    partner_ct_id = ContentType.objects.get_for_model(Partner).id

    ctx = {'company': company,
           'form': form,
           'contacts': contacts,
           'partner': partner,
           'contact_ct': contact_ct_id,
           'partner_ct': partner_ct_id,
           'view_name': 'PRM'}
    return render_to_response('mypartners/partner_details.html', ctx,
                              RequestContext(request))


@user_passes_test(lambda u: User.objects.is_group_member(u, 'Employer'))
def edit_item(request):
    """
    Form page that is what makes new and edits partners/contacts.

    """
    company_id = request.REQUEST.get('company')

    company = get_object_or_404(Company, id=company_id)

    user = request.user
    if not user in company.admins.all():
        raise Http404

    # If the user is trying to create a new Partner they won't have a
    # partner_id. A Contact however does, it also comes from a different URL.
    if request.path != reverse('create_partner'):
        try:
            partner_id = int(request.REQUEST.get('partner'))
        except TypeError:
            raise Http404
        partner = get_object_or_404(company.partner_set.all(), id=partner_id)
    else:
        partner = None

    try:
        content_id = int(request.REQUEST.get('ct'))
    except TypeError:
        raise Http404
    item_id = request.REQUEST.get('id') or None

    if content_id == ContentType.objects.get_for_model(Partner).id:
        if not item_id:
            form = NewPartnerForm()
    elif content_id == ContentType.objects.get_for_model(Contact).id:
        if not item_id:
            form = ContactForm()
        else:
            try:
                item = Contact.objects.get(partner=partner, pk=item_id)
            except:
                raise Http404
            form = ContactForm(instance=item, auto_id=False)
    else:
        raise Http404

    ctx = {'form': form,
           'partner': partner,
           'company': company,
           'contact': item_id,
           'content_id': content_id,
           'view_name': 'PRM'}

    return render_to_response('mypartners/edit_item.html', ctx,
                              RequestContext(request))


@user_passes_test(lambda u: User.objects.is_group_member(u, 'Employer'))
def save_init_partner_form(request):
    if 'partnername' in request.POST:
        form = NewPartnerForm(user=request.user, data=request.POST)
    else:
        form = PartnerInitialForm(user=request.user, data=request.POST)
    if form.is_valid():
        form.save(request.user)
        return HttpResponse(status=200)
    else:
        return HttpResponse(json.dumps(form.errors))


@user_passes_test(lambda u: User.objects.is_group_member(u, 'Employer'))
def save_item(request):
    """
    Generic save for Partner and Contact Forms.

    """
    company_id = request.REQUEST.get('company')

    company = get_object_or_404(Company, id=company_id)

    content_id = int(request.REQUEST.get('ct'))

    if content_id == ContentType.objects.get_for_model(Contact).id:
        item_id = request.REQUEST.get('id') or None
        try:
            partner_id = int(request.REQUEST.get('partner'))
        except TypeError:
            raise Http404

        partner = get_object_or_404(company.partner_set.all(), id=partner_id)

        if item_id:
            try:
                item = Contact.objects.get(partner=partner, pk=item_id)
            except:
                raise Http404
            else:
                form = ContactForm(instance=item, auto_id=False,
                                   data=request.POST)
                if form.is_valid():
                    form.save(request.user)
                    return HttpResponse(status=200)
                else:
                    return HttpResponse(json.dumps(form.errors))
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save(request.user, partner)
            return HttpResponse(status=200)
        else:
            return HttpResponse(json.dumps(form.errors))

    if content_id == ContentType.objects.get_for_model(Partner).id:
        try:
            partner_id = int(request.REQUEST.get('partner'))
        except TypeError:
            raise Http404

        partner = get_object_or_404(company.partner_set.all(), id=partner_id)
        form = PartnerForm(instance=partner, auto_id=False, data=request.POST)
        if form.is_valid():
            form.save(request.user)
            return HttpResponse(status=200)
        else:
            return HttpResponse(json.dumps(form.errors))


@user_passes_test(lambda u: User.objects.is_group_member(u, 'Employer'))
def delete_prm_item(request):
    """
    Deletes Partners and Contacts

    """
    company_id = request.REQUEST.get('company')

    company = get_object_or_404(Company, id=company_id)

    partner_id = request.REQUEST.get('partner')
    if partner_id:
        partner_id = int(partner_id)
    item_id = request.REQUEST.get('id')
    if item_id:
        contact_id = int(item_id)
    content_id = request.REQUEST.get('ct')
    if content_id:
        content_id = int(content_id)

    if content_id == ContentType.objects.get_for_model(Contact).id:
        partner = get_object_or_404(Partner, id=partner_id, owner=company)
        contact = get_object_or_404(Contact, id=contact_id)
        log_change(contact, None, request.user, partner, contact.name,
                   action_type=DELETION)
        contact.delete()
        return HttpResponseRedirect(reverse('partner_details')+'?company=' +
                                    str(company_id)+'&partner=' +
                                    str(partner_id))
    elif content_id == ContentType.objects.get_for_model(Partner).id:
        partner = get_object_or_404(Partner, id=partner_id, owner=company)
        Contact.objects.filter(partner=partner).delete()
        log_change(partner, None, request.user, partner, partner.name,
                   action_type=DELETION)
        partner.delete()
        return HttpResponseRedirect(reverse('prm') + '?company=' +
                                    str(company_id))
    elif content_id == ContentType.objects.get_for_model(ContactRecord).id:
        contact_record = get_object_or_404(ContactRecord, partner=partner_id,
                                           id=item_id)
        partner = get_object_or_404(Partner, id=partner_id, owner=company)
        log_change(contact_record, None, request.user, partner,
                   contact_record.contact_name, action_type=DELETION)
        contact_record.delete()
        return HttpResponseRedirect(reverse('partner_records')+'?company=' +
                                    str(company_id)+'&partner=' +
                                    str(partner_id))
    elif content_id == ContentType.objects.get_for_model(PartnerSavedSearch).id:
        saved_search = get_object_or_404(PartnerSavedSearch, id=item_id)
        partner = get_object_or_404(Partner, id=partner_id, owner=company)
        log_change(saved_search, None, request.user, partner,
                   saved_search.email, action_type=DELETION)
        saved_search.delete()
        return HttpResponseRedirect(reverse('partner_searches')+'?company=' +
                                    str(company_id)+'&partner=' +
                                    str(partner_id))


@user_passes_test(lambda u: User.objects.is_group_member(u, 'Employer'))
def prm_overview(request):
    """
    View that is the "Overview" of one's Partner Activity.

    """
    company, partner, user = prm_worthy(request)

    most_recent_activity = get_logs_for_partner(partner)
    dt_range = [datetime.now() + timedelta(-30), datetime.now()]
    records = get_contact_records_for_partner(
        partner, date_time_range=dt_range)
    communication = records.order_by('-created_on')
    records = records.exclude(contact_type='job').count()
    most_recent_communication = communication[:3]
    saved_searches = get_searches_for_partner(partner)
    most_recent_saved_searches = saved_searches[:3]


    ctx = {'partner': partner,
           'company': company,
           'recent_activity': most_recent_activity,
           'recent_communication': most_recent_communication,
           'recent_ss': most_recent_saved_searches,
           'count': records,
           'view_name': 'PRM'}

    return render_to_response('mypartners/overview.html', ctx,
                              RequestContext(request))


@user_passes_test(lambda u: User.objects.is_group_member(u, 'Employer'))
def prm_saved_searches(request):
    """
    View that lists the Partner's Saved Searches

    """
    company, partner, user = prm_worthy(request)
    saved_searches = get_searches_for_partner(partner)
    ctx = {'searches': saved_searches,
           'company': company,
           'partner': partner}
    return render_to_response('mypartners/partner_searches.html', ctx,
                              RequestContext(request))


@user_passes_test(lambda u: User.objects.is_group_member(u, 'Employer'))
def prm_edit_saved_search(request):
    company, partner, user = prm_worthy(request)
    item_id = request.REQUEST.get('id')
    if item_id:
        instance = get_object_or_404(PartnerSavedSearch, id=item_id)
        form = PartnerSavedSearchForm(partner=partner, instance=instance)
    else:
        form = PartnerSavedSearchForm(partner=partner)
    ctx = {
        'company': company,
        'partner': partner,
        'item_id': item_id,
        'form': form,
        'content_type': ContentType.objects.get_for_model(PartnerSavedSearch).id,
        'view_name': 'PRM',
    }
    return render_to_response('mypartners/partner_edit_search.html', ctx,
                              RequestContext(request))


@user_passes_test(lambda u: User.objects.is_group_member(u, 'Employer'))
def verify_contact(request):
    """
    Checks to see if a contact has a My.jobs account. Checks to see if they are
    active as well.

    """
    if request.REQUEST.get('action') != 'validate':
        raise Http404
    email = request.REQUEST.get('email')
    if email == 'None':
        return HttpResponse(json.dumps(
            {'status': 'None',
             'message': 'If a contact does not have an email they will not '
                        'show up on this list.'}))
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return HttpResponse(json.dumps(
            {'status': 'unverified',
             'message': 'A My.jobs account will be created for this contact, '
                        'which will include a personal greeting.'}))
    else:
        # Check to see if user is active
        if user.is_active:
            return HttpResponse(json.dumps(
                {'status': 'verified',
                 'message': ''}))
        else:
            return HttpResponse(json.dumps(
                {'status': 'unverified',
                 'message': 'This contact has an account on My.jobs already '
                            'but has yet to activate their account.'}))


@user_passes_test(lambda u: User.objects.is_group_member(u, 'Employer'))
def partner_savedsearch_save(request):
    """
    Handles saving the PartnerSavedSearchForm and creating the inactive user
    if it is needed.

    """
    company, partner, user = prm_worthy(request)
    item_id = request.REQUEST.get('id', None)

    if item_id:
        item = get_object_or_404(PartnerSavedSearch, id=item_id,
                                 provider=company.id)
        form = PartnerSavedSearchForm(instance=item, auto_id=False,
                                      data=request.POST,
                                      partner=partner)
        if form.is_valid():
            form.save()
            return HttpResponse(status=200)
        else:
            return HttpResponse(json.dumps(form.errors))
    form = PartnerSavedSearchForm(request.POST, partner=partner)

    # Since the feed is created below, this will always be invalid.
    if 'feed' in form.errors:
        del form.errors['feed']

    if form.is_valid():
        instance = form.instance
        try:
            instance.user = User.objects.get(email=instance.email)
        except User.DoesNotExist:
            user = User.objects.create_inactive_user(
                email=instance.email,
                custom_msg=instance.account_activation_message)
            instance.user = user[0]
            Contact.objects.filter(email=instance.email).update(user=instance.user)
        instance.feed = form.data['feed']
        instance.provider = company
        instance.partner = partner
        instance.created_by = request.user
        instance.custom_message = instance.partner_message
        form.save()
        return HttpResponse(status=200)
    else:
        return HttpResponse(json.dumps(form.errors))


@user_passes_test(lambda u: User.objects.is_group_member(u, 'Employer'))
def partner_view_full_feed(request):
    """
    PartnerSavedSearch feed.

    """
    company, partner, user = prm_worthy(request)
    search_id = request.REQUEST.get('id')
    saved_search = get_object_or_404(PartnerSavedSearch, id=search_id)

    if company == saved_search.partnersavedsearch.provider:
        url_of_feed = url_sort_options(saved_search.feed,
                                       saved_search.sort_by,
                                       saved_search.frequency)
        items, count = parse_feed(url_of_feed, saved_search.frequency)
        extras = saved_search.partnersavedsearch.url_extras
        if extras:
            add_extra_params_to_jobs(items, extras)
            saved_search.url = add_extra_params(saved_search.url, extras)
    else:
        return HttpResponseRedirect(reverse('prm_saved_searches'))

    ctx = {
        'search': saved_search,
        'items': items,
        'view_name': 'Saved Searches',
        'is_pss': True,
        'partner': partner.id,
        'company': company.id
    }

    return render_to_response('mysearches/view_full_feed.html', ctx,
                              RequestContext(request))



@user_passes_test(lambda u: User.objects.is_group_member(u, 'Employer'))
def prm_report_records(request):
    ctx = get_record_context(request)
    return render_to_response('mypartners/report_record_view.html', ctx,
                              RequestContext(request))


def get_record_context(request):
    company, partner, user = prm_worthy(request)
    record_type = request.REQUEST.get('record_type')
    dt_range = [datetime.now() + timedelta(-30), datetime.now()]
    contact_records = get_contact_records_for_partner(
        partner, record_type=record_type, date_time_range=dt_range)
    most_recent_activity = get_logs_for_partner(partner)

    contact_type_choices = [('all', 'All')] + list(CONTACT_TYPE_CHOICES)
    contacts = ContactRecord.objects.filter(partner=partner)
    contacts = contacts.values('contact_name').distinct()
    contact_choices = [('all', 'All')]
    [contact_choices.append((c['contact_name'], c['contact_name']))
     for c in contacts]

    ctx = {
        'company': company,
        'contact_choices': contact_choices,
        'contact_type_choices': contact_type_choices,
        'date_display': '30',
        'date_start': dt_range[0],
        'date_end': dt_range[1],
        'most_recent_activity': most_recent_activity,
        'partner': partner,
        'records': contact_records,
        'record_type': record_type,
        'view_name': 'PRM'
    }
    return ctx


@user_passes_test(lambda u: User.objects.is_group_member(u, 'Employer'))
def prm_records(request):
    """
    ContactRecord overview.

    """
    company, partner, user = prm_worthy(request)
    dt_range = [datetime.now() + timedelta(-30), datetime.now()]
    contact_records = get_contact_records_for_partner(partner,
                                                      date_time_range=dt_range)
    most_recent_activity = get_logs_for_partner(partner)

    contact_type_choices = [('all', 'All')] + list(CONTACT_TYPE_CHOICES)
    contacts = ContactRecord.objects.filter(partner=partner)
    contacts = contacts.values('contact_name').distinct()
    contact_choices = [('all', 'All')]
    [contact_choices.append((c['contact_name'], c['contact_name']))
     for c in contacts]

    ctx = {
        'company': company,
        'contact_choices': contact_choices,
        'contact_type_choices': contact_type_choices,
        'date_display': '30',
        'date_start': dt_range[0],
        'date_end': dt_range[1],
        'most_recent_activity': most_recent_activity,
        'partner': partner,
        'records': contact_records,
        'view_name': 'PRM'
    }
    return render_to_response('mypartners/main_records.html', ctx,
                              RequestContext(request))


@user_passes_test(lambda u: User.objects.is_group_member(u, 'Employer'))
def prm_edit_records(request):
    company, partner, user = prm_worthy(request)
    record_id = request.GET.get('id', None)

    try:
        instance = ContactRecord.objects.get(pk=record_id)
    except ContactRecord.DoesNotExist:
        instance = None

    if request.method == 'POST':
        instance = None
        if record_id:
            try:
                instance = ContactRecord.objects.get(pk=record_id)
            except ContactRecord.DoesNotExist:
                instance = None
        form = ContactRecordForm(request.POST, request.FILES,
                                 partner=partner, instance=instance)
        if form.is_valid():
            form.save(user, partner)
            return HttpResponseRedirect(reverse('partner_records') +
                                        '?company=%d&partner=%d' %
                                        (company.id, partner.id))
    else:
        form = ContactRecordForm(partner=partner, instance=instance)

    ctx = {
        'company': company,
        'partner': partner,
        'content_type': ContentType.objects.get_for_model(ContactRecord).id,
        'object_id': record_id,
        'form': form,
    }
    return render_to_response('mypartners/edit_record.html', ctx,
                              RequestContext(request))


@user_passes_test(lambda u: User.objects.is_group_member(u, 'Employer'))
def prm_view_records(request):
    """
    View an individual ContactRecord.

    """
    company, partner, user = prm_worthy(request)
    record_id = request.GET.get('id')
    offset = request.GET.get('offset', 0)
    record_type = request.GET.get('type')
    name = request.GET.get('name')
    range_start = request.REQUEST.get('date_start')
    range_end = request.REQUEST.get('date_end')
    try:
        range_start = datetime.strptime(range_start, "%m/%d/%Y")
        range_end = datetime.strptime(range_end, "%m/%d/%Y")
    except (AttributeError, TypeError):
        range_start = None
        range_end = None

    try:
        record_id = int(record_id)
        offset = int(offset)
    except (TypeError, ValueError):
        return HttpResponseRedirect(reverse('partner_records') +
                '?company=%d&partner=%d' % (company.id, partner.id))

    prev_offset = (offset - 1) if offset > 1 else 0
    records = get_contact_records_for_partner(partner, record_type=record_type,
                                              contact_name=name,
                                              date_time_range=[range_start,
                                                               range_end],
                                              offset=prev_offset,
                                              limit=prev_offset + 3)

    # Since we always retrieve 3, if the record is at the beginning of the
    # list we might have 3 results but no previous.
    if len(records) == 3 and records[0].pk == record_id:
        prev_id = None
        record = records[0]
        next_id = records[1].pk
    elif len(records) == 3:
        prev_id = records[0].pk
        record = records[1]
        next_id = records[2].pk
    # If there are only 2 results, it means there is either no next or
    # no previous, so we need to compare record ids to figure out which
    # is which.
    elif len(records) == 2 and records[0].pk == record_id:
        prev_id = None
        record = records[0]
        next_id = records[1].pk
    elif len(records) == 2:
        prev_id = records[0].pk
        record = records[1]
        next_id = None
    elif len(records) == 1:
        prev_id = None
        record = records[0]
        next_id = None
    else:
        prev_id = None
        record = get_object_or_404(ContactRecord, pk=record_id)
        next_id = None

    # Double check our results and drop the next and previous options if
    # the results were wrong
    if record_id != record.pk:
        prev_id = None
        record = get_object_or_404(ContactRecord, pk=record_id)
        next_id = None

    attachments = PRMAttachment.objects.filter(contact_record=record)
    logs = ContactLogEntry.objects.filter(object_id=record_id)
    record_history = ContactLogEntry.objects.filter(object_id=record_id)
    ctx = {
        'date_start': range_start,
        'date_end': range_end,
        'record': record,
        'partner': partner,
        'company': company,
        'activity': logs,
        'attachments': attachments,
        'record_history': record_history,
        'next_id': next_id,
        'next_offset': offset + 1,
        'prev_id': prev_id,
        'prev_offset': prev_offset,
        'contact_type': record_type,
        'contact_name': name,
        'view_name': 'PRM'

    }

    return render_to_response('mypartners/view_record.html', ctx,
                              RequestContext(request))


@user_passes_test(lambda u: User.objects.is_group_member(u, 'Employer'))
def get_contact_information(request):
    """
    Returns a json object containing a contact's email address and
    phone number if they have one.

    """
    company, partner, user = prm_worthy(request)
    contact_id = request.REQUEST.get('contact_name')
    try:
        contact = Contact.objects.get(pk=contact_id)
    except Contact.DoesNotExist:
        data = {'error': 'Contact does not exist'}
        return HttpResponse(json.dumps(data))

    if partner != contact.partner:
        data = {'error': 'Permission denied'}
        return HttpResponse(json.dumps(data))

    if hasattr(contact, 'email'):
        if hasattr(contact, 'phone'):
            data = {'email': contact.email,
                    'phone': contact.phone}
        else:
            data = {'email': contact.email}
    else:
        if hasattr(contact, 'phone'):
            data = {'phone': contact.phone}
        else:
            data = {}

    return HttpResponse(json.dumps(data))

@user_passes_test(lambda u: User.objects.is_group_member(u, 'Employer'))
def get_records(request):
    """
    Returns a json object containing the records matching the search
    criteria (contact, contact_type, and date_time range) rendered using
    records.html and the date range and date string required to update
    the time_filter.html template to match the search.

    """
    company, partner, user = prm_worthy(request)

    contact = request.REQUEST.get('contact')
    contact_type = request.REQUEST.get('contact_type')
    contact = None if contact == 'all' else contact
    contact_type = None if contact_type == 'all' else contact_type
    records = get_contact_records_for_partner(partner, contact_name=contact,
                                              record_type=contact_type)

    date_range = request.REQUEST.get('date')
    if date_range:
        date_str_results = {
            'today': datetime.now() + timedelta(-1),
            'seven_days': datetime.now() + timedelta(-7),
            'thirty_days': datetime.now() + timedelta(-30),
        }
        range_end = datetime.now()
        range_start = date_str_results.get(date_range)
    else:
        range_start = request.REQUEST.get('date_start')
        range_end = request.REQUEST.get('date_end')
        try:
            range_start = datetime.strptime(range_start, "%m/%d/%Y")
            range_end = datetime.strptime(range_end, "%m/%d/%Y")
        except AttributeError:
            range_start = None
            range_end = None
    date_str = 'Filter by time range'
    if range_start and range_end:
        try:
            date_str = (range_end - range_start).days
            date_str = (("%s Days" % date_str) if date_str != 1
                        else ("%s Day" % date_str))
            records = records.filter(date_time__range=[range_start, range_end])
        except (ValidationError, TypeError):
            pass

    records = get_contact_records_for_partner(partner, contact_name=contact,
                                              record_type=contact_type,
                                              date_time_range=[range_start,
                                                               range_end])
    ctx = {
        'records': records,
        'company': company,
        'partner': partner,
        'contact_type': None if contact_type == 'all' else contact_type,
        'contact_name': None if contact == 'all' else contact,
        'view_name': 'PRM'
    }

    data = {
        'date_end': range_end.strftime('%m/%d/%Y'),
        'date_start': range_start.strftime('%m/%d/%Y'),
        'date_str': date_str,
        'html': render_to_response('mypartners/records.html', ctx,
                                   RequestContext(request)).content,
    }
    return HttpResponse(json.dumps(data))


@user_passes_test(lambda u: User.objects.is_group_member(u, 'Employer'))
def get_uploaded_file(request):
    """
    Determines the location of a PRMAttachment (either in S3 or in local
    storage) and redirects to it.

    PRMAttachments stored in S3 require a generated key and have a 10 minute
    access window.

    """
    company, partner, user = prm_worthy(request)
    file_id = request.GET.get('id', None)
    attachment = get_object_or_404(PRMAttachment, pk=file_id,
                                   contact_record__partner=partner)
    try:
        if repr(default_storage.connection) == 'S3Connection:s3.amazonaws.com':
            from boto.s3.connection import S3Connection

            s3 = S3Connection(settings.AWS_ACCESS_KEY_ID,
                              settings.AWS_SECRET_KEY, is_secure=True)
            path = s3.generate_url(600, 'GET',
                                   bucket=settings.AWS_STORAGE_BUCKET_NAME,
                                   key=attachment.attachment.name,
                                   force_http=True)
        else:
            path = "%s%s" % (settings.MEDIA_URL, attachment.attachment.name)
    except AttributeError:
        path = "%s%s" % (settings.MEDIA_URL, attachment.attachment.name)

    return HttpResponseRedirect(path)


@user_passes_test(lambda u: User.objects.is_group_member(u, 'Employer'))
def partner_main_reports(request):
    company, partner, user = prm_worthy(request)
    dt_range = [datetime.now() + timedelta(-30), datetime.now()]
    records = get_contact_records_for_partner(partner,
                                              date_time_range=dt_range)
    total_records_wo_followup = records.exclude(contact_type='job').count()
    referral = records.filter(contact_type='job').count()

    # need to order_by -count to keep the "All Contacts" list in proper order
    all_contacts = records.values('contact_name', 'contact_email')\
        .annotate(count=Count('contact_name')).order_by('-count')

    # Used for Top Contacts
    contact_records = records\
        .exclude(contact_type='job')\
        .values('contact_name', 'contact_email')\
        .annotate(count=Count('contact_name')).order_by('-count')

    # Individual Referral Records count
    referral_list = records.filter(contact_type='job')\
        .values('contact_name', 'contact_email')\
        .annotate(count=Count('contact_name'))

    # Merge contact_records with referral_list and have all contacts
    # A contact can have 0 contact records and 1 referral record and still show up
    # vice versa with 1 contact record and 0 referrals
    contacts = []
    for contact_obj in all_contacts:
        contact = {}
        name = contact_obj['contact_name']
        email = contact_obj['contact_email']
        contact['name'] = name
        contact['email'] = email
        for cr in contact_records:
            if cr['contact_name'] == name and cr['contact_email'] == email:
                contact['cr_count'] = cr['count']
        if not 'cr_count' in contact:
            contact['cr_count'] = 0
        for ref in referral_list:
            if ref['contact_name'] == name and ref['contact_email'] == email:
                contact['ref_count'] = ref['count']
        if not 'ref_count' in contact:
            contact['ref_count'] = 0
        contacts.append(contact)

    # calculate 'All Others' in Top Contacts (when more than 3)
    total_others = 0
    if contact_records.count() > 3:
        others = contact_records[3:]
        top_contacts_records = contact_records[:3]
        for contact in others:
            total_others += contact['count']

    ctx = {'partner': partner,
           'company': company,
           'contacts': contacts,
           'total_records': total_records_wo_followup,
           'referral': referral,
           'top_contacts': contact_records,
           'others': total_others,
           'view_name': 'PRM'}
    return render_to_response('mypartners/partner_reports.html', ctx,
                              RequestContext(request))


@user_passes_test(lambda u: User.objects.is_group_member(u, 'Employer'))
def partner_get_records(request):
    if request.method == 'GET':
        company, partner, user = prm_worthy(request)
        dt_range = [datetime.now() + timedelta(-30), datetime.now()]
        records = get_contact_records_for_partner(
            partner, date_time_range=dt_range).exclude(contact_type='job')
        email = records.filter(contact_type='email').count()
        phone = records.filter(contact_type='phone').count()
        facetoface = records.filter(contact_type='facetoface').count()

        # figure names
        if email != 1:
            email_name = 'Emails'
        else:
            email_name = 'Email'
        if phone != 1:
            phone_name = 'Phone Calls'
        else:
            phone_name = 'Phone Call'
        if facetoface != 1:
            facetoface_name = 'Face to Face'
        else:
            facetoface_name = 'Face to Face'

        data = {'email': {"count": email, "name": email_name, 'typename': 'email'},
                'phone': {"count": phone, "name": phone_name, 'typename': 'phone'},
                'facetoface': {"count": facetoface, "name": facetoface_name,
                               "typename": "facetoface"}}
        data = OrderedDict(sorted(data.items(), key=lambda t: t[1]['count']))
        data_items = data.items()
        data_items.reverse()
        data = OrderedDict(data_items)
        return HttpResponse(json.dumps(data))
    else:
        raise Http404


@user_passes_test(lambda u: User.objects.is_group_member(u, 'Employer'))
def partner_get_referrals(request):
    if request.method == 'GET':
        company, partner, user = prm_worthy(request)
        dt_range = [datetime.now() + timedelta(-30), datetime.now()]
        records = get_contact_records_for_partner(partner,
                                                  date_time_range=dt_range)
        referrals = records.filter(contact_type='job')

        # (job application, job interviews, job hires)
        nums = referrals.values_list('job_applications', 'job_interviews',
                                     'job_hires')

        applications, interviews, hires = 0, 0, 0
        # add numbers together
        for num_set in nums:
            applications += int(num_set[0])
            interviews += int(num_set[1])
            hires += int(num_set[2])

        # figure names
        app_name, interview_name, hire_name = '', '', ''
        if applications != 1:
            app_name = 'Applications'
        else:
            app_name = 'Application'
        if interviews != 1:
            interview_name = 'Interviews'
        else:
            interview_name = 'Interview'
        if hires != 1:
            hire_name = 'Hires'
        else:
            hire_name = 'Hire'

        data = {'applications': {'count': applications, 'name': app_name},
                'interviews': {'count': interviews, 'name': interview_name},
                'hires': {'count': hires, 'name': hire_name}}

        return HttpResponse(json.dumps(data))
    else:
        raise Http404


@user_passes_test(lambda u: User.objects.is_group_member(u, 'Employer'))
def prm_export(request):
    company, partner, user = prm_worthy(request)
    file_format = request.REQUEST.get('file_format', 'csv')
    fields = retrieve_fields(ContactRecord)
    _, _, records = get_records_from_request(request)

    if file_format == 'xml':
        root = etree.Element("contact_records")
        for record in records:
            xml_record = etree.SubElement(root, "record")
            for field in fields:
                xml = etree.SubElement(xml_record, field)
                xml.text = contact_record_val_to_str(getattr(record, field, ""))
        response = HttpResponse(etree.tostring(root, pretty_print=True),
                                mimetype='application/force-download')
    elif file_format == 'printer_friendly':
        ctx = {
            'company': company,
            'fields': fields,
            'partner': partner,
            'records': records,
        }
        return render_to_response('mypartners/printer_friendly.html', ctx,
                                  RequestContext(request))
    # CSV
    else:
        response = HttpResponse(content_type='text/csv')
        writer = csv.writer(response)
        writer.writerow(fields)
        for record in records:
            values = [getattr(record, field, '') for field in fields]
            values = [contact_record_val_to_str(v) for v in values]
            writer.writerow(values)

    response['Content-Disposition'] = 'attachment; ' \
                                      'filename="company_record_report".%s' \
                                      % file_format

    return response
