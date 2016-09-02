from datetime import date, timedelta
from email.parser import HeaderParser
from email.utils import getaddresses
import json
import logging
from lxml import etree
import pytz
import re
import unicodecsv
from urllib import urlencode
from validate_email import validate_email

from django.conf import settings
from django.contrib.auth.decorators import user_passes_test
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage
from django.core.paginator import Paginator
from django.core.validators import EmailValidator
from django.db.models import Q, Count
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import (Http404, HttpResponse, HttpResponseRedirect,
                         HttpResponseNotAllowed)
from django.core.urlresolvers import reverse
from django.utils.html import strip_tags
from django.utils.text import force_text
from django.utils.timezone import localtime, now
from django.utils.datastructures import SortedDict
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django_remote_forms.forms import RemoteForm
from urllib2 import HTTPError

from email_parser import build_email_dicts, get_datetime_from_str
import newrelic.agent
from universal.helpers import (get_company_or_404, get_int_or_none,
                               add_pagination, get_object_or_none)
from universal.decorators import warn_when_inactive, restrict_to_staff
from universal.api_validation import FormsApiValidator
from myjobs.models import User

from myjobs.decorators import requires
from myjobs.models import MissingActivity
from mysearches.models import PartnerSavedSearch
from mysearches.helpers import get_interval_from_frequency
from mysearches.forms import PartnerSavedSearchForm
from mypartners.forms import (PartnerForm, ContactForm,
                              NewPartnerForm, ContactRecordForm, TagForm,
                              LocationForm, NuoPartnerForm, NuoContactForm,
                              NuoLocationForm, NuoCommunicationRecordForm,
                              NuoOutreachRecordForm)
from mypartners.models import (Partner, Contact, ContactRecord,
                               PRMAttachment, ContactLogEntry, Tag,
                               CONTACT_TYPE_CHOICES, ADDITION, DELETION,
                               Location, OutreachEmailAddress, OutreachRecord,
                               PartnerLibrarySource, OutreachWorkflowState,
                               OutreachEmailDomain, Status)
from mypartners.helpers import (prm_worthy, add_extra_params,
                                add_extra_params_to_jobs, log_change,
                                contact_record_val_to_str, retrieve_fields,
                                get_records_from_request,
                                filter_partners,
                                new_partner_from_library,
                                send_contact_record_email_response,
                                find_partner_from_email, tag_get_or_create)

logger = logging.getLogger(__name__)


@warn_when_inactive(feature='Partner Relationship Manager is')
@requires('read partner')
def prm(request):
    """
    Partner Relationship Manager

    """
    company = get_company_or_404(request)

    partners = filter_partners(request)
    paginator = add_pagination(request, partners) if partners else None

    if request.is_ajax():
        ctx = {
            'partners': paginator,
            'on_page': 'prm',
            'ajax': 'true',
        }
        response = HttpResponse()
        html = render_to_response('mypartners/includes/partner_column.html',
                                  ctx, RequestContext(request))
        response.content = html.content
        return response

    ctx = {
        'has_partners': True if paginator else False,
        'partners': paginator,
        'company': company,
        'user': request.user,
        'partner_ct': ContentType.objects.get_for_model(Partner).id,
        'view_name': 'PRM'
    }

    return render_to_response('mypartners/prm.html', ctx,
                              RequestContext(request))


@warn_when_inactive(feature='Partner Library is')
@requires('read partner')
def partner_library(request):
    company = get_company_or_404(request)

    if request.is_ajax():
        partners = filter_partners(request, True)
        paginator = add_pagination(request, partners)
        ctx = {
            'partners': paginator,
            'on_page': 'partner_library'
        }
        response = HttpResponse()
        html = render_to_response('mypartners/includes/partner_column.html',
                                  ctx, RequestContext(request))
        response.content = html.content
        return response

    partners = filter_partners(request, True)
    paginator = add_pagination(request, partners)

    ctx = {
        'company': company,
        'view_name': 'PRM',
        'partners': paginator,
        'sources': PartnerLibrarySource.objects.values('search_url', 'name')
    }

    return render_to_response('mypartners/partner_library.html', ctx,
                              RequestContext(request))


@requires('create partner')
def create_partner_from_library(request):
    """ Creates a partner and contact from a library_id. """
    partner = new_partner_from_library(request)

    redirect = False
    if request.REQUEST.get("redirect"):
        redirect = True
    ctx = {
        'partner': partner.id,
        'redirect': redirect
    }

    return HttpResponse(json.dumps(ctx))


@warn_when_inactive(feature='Partner Relationship Manager is')
@requires('update partner')
def partner_details(request):
    company, partner, user = prm_worthy(request)

    form = PartnerForm(instance=partner, auto_id=False)

    contacts = Contact.objects.filter(
        partner=partner, archived_on__isnull=True)
    contact_ct_id = ContentType.objects.get_for_model(Contact).id
    partner_ct_id = ContentType.objects.get_for_model(Partner).id

    ctx = {
        'company': company,
        'form': form,
        'contacts': contacts,
        'partner': partner,
        'contact_ct': contact_ct_id,
        'partner_ct': partner_ct_id,
        'view_name': 'PRM',
        'create_tags': json.dumps(request.user.can(company, 'create tag')),
    }
    return render_to_response('mypartners/partner_details.html', ctx,
                              RequestContext(request))


@warn_when_inactive(feature='Partner Relationship Manager is')
@requires('create partner')
def edit_item(request):
    """ Contact/Partner Form.

        If the user reaches this form thorugh the `edit_contact` URL and a
        valid partner_id is provided, they are presented with the "Add Partner"
        form.

        Conversely, if the user reaches this form through the `create_partner`
        URL, they are presented with "Add Contact" form. If a valid `item_id`
        is passed, we preload the form with that contact's information.
    """
    http404_view = 'mypartners.views.edit_item'
    try:
        partner_id = int(request.REQUEST.get("partner") or 0)
        item_id = int(request.REQUEST.get('id') or 0)
        content_id = int(request.REQUEST.get('ct') or 0)
    except ValueError:
        raise Http404("{view}: partner, item, or content type "
                      "id is bad".format(view=http404_view))

    company = get_company_or_404(request)
    partners = []
    contacts = []
    if partner_id and request.path == reverse('edit_contact'):
        partner = get_object_or_404(company.partner_set.all(), id=partner_id)
        if item_id:
            item = get_object_or_404(Contact, partner=partner, pk=item_id)
            form = ContactForm(instance=item, auto_id=False)
        else:
            contacts = list(partner.contact_set.filter(
                archived_on__isnull=True).values(
                    'pk', 'name', 'email', 'phone'))
            form = ContactForm()
            item = None
    elif request.path == reverse('create_partner'):
        partner = None
        if item_id:
            item = get_object_or_404(Partner, pk=item_id)
            form = PartnerForm(instance=item)
        else:
            partners = list(company.partner_set.values(
                'pk', 'name', 'uri'))
            item = None
            form = NewPartnerForm()
    else:
        raise Http404("{view}: path incorrect and/or no "
                      "partner id provided".format(view=http404_view))

    ctx = {
        'form': form,
        'partner': partner,
        'partners': json.dumps(partners),
        'company': company,
        'contact': item,
        'contacts': json.dumps(contacts),
        'content_id': content_id,
        'view_name': 'PRM',
        'create_tags': json.dumps(request.user.can(company, 'create tag')),
    }
    if item_id:
        ctx['locations'] = Contact.objects.get(pk=item_id).locations.all()

    return render_to_response('mypartners/edit_item.html', ctx,
                              RequestContext(request))


@requires('create partner')
def save_init_partner_form(request):
    form = NewPartnerForm(user=request.user, data=request.POST)

    if form.is_valid():
        form.save()
        return HttpResponse(status=200)
    else:
        return HttpResponse(json.dumps(form.errors))


@requires('update partner')
def save_item(request):
    """
    Generic save for Partner and Contact Forms.

    """
    http404_view = 'mypartners.views.save_item'
    company = get_company_or_404(request)
    content_id = int(request.REQUEST.get('ct') or 0)

    if content_id == ContentType.objects.get_for_model(Contact).id:
        item_id = request.REQUEST.get('id') or None
        try:
            partner_id = int(request.REQUEST.get('partner') or 0)
        except TypeError:
            raise Http404("{view}: Partner id is not an int".format(
                view=http404_view))

        partner = get_object_or_404(company.partner_set.all(), id=partner_id)

        if item_id:
            try:
                item = Contact.objects.get(partner=partner, pk=item_id)
            except Contact.DoesNotExist:
                raise Http404("{view}: Contact id is not an int".format(
                    view=http404_view))
            else:
                form = ContactForm(instance=item, auto_id=False,
                                   data=request.POST)
                if form.is_valid():
                    form.save(request, partner)
                    return HttpResponse(status=200)
                else:
                    return HttpResponse(json.dumps(form.errors))
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save(request, partner)
            return HttpResponse(status=200)
        else:
            return HttpResponse(json.dumps(form.errors))

    if content_id == ContentType.objects.get_for_model(Partner).id:
        try:
            partner_id = int(request.REQUEST.get('partner'))
        except TypeError:
            raise Http404("{view}: Partner id is not an int".format(
                view=http404_view))

        partner = get_object_or_404(company.partner_set.all(), id=partner_id)
        form = PartnerForm(instance=partner, auto_id=False, data=request.POST)
        if form.is_valid():
            form.save(request, partner)
            return HttpResponse(status=200)
        else:
            return HttpResponse(json.dumps(form.errors))
    raise Http404("{view}: Item is not a Partner or Contact".format(
        view=http404_view))


@warn_when_inactive(feature='Partner Relationship Manager is')
@requires('delete partner')
def delete_prm_item(request):
    """
    Deletes Partners and Contacts

    """
    company = get_company_or_404(request)
    partner_id = request.REQUEST.get('partner')
    partner_id = get_int_or_none(partner_id)

    item_id = request.REQUEST.get('id')
    contact_id = get_int_or_none(item_id)

    content_id = request.REQUEST.get('ct')
    content_id = get_int_or_none(content_id)

    if content_id == ContentType.objects.get_for_model(Partner).id:
        partner = get_object_or_404(Partner, id=partner_id, owner=company)
        log_change(partner, None, request.user, partner, partner.name,
                   action_type=DELETION, impersonator=request.impersonator)
        partner.archive()
        return HttpResponseRedirect(reverse('prm') + '?company=' +
                                    str(company.id))
    elif content_id == ContentType.objects.get_for_model(ContactRecord).id:
        contact_record = get_object_or_404(ContactRecord, partner=partner_id,
                                           id=item_id)
        partner = get_object_or_404(Partner, id=partner_id, owner=company)
        # At one point, contacts could be deleted. The previous functionality
        # at this location couldn't handle that, accessing
        # contact_record.contact.name directly. Chaining getattr may not be
        # pretty but it ensures that we will never be accessing nonexistent
        # attributes.
        contact_name = getattr(getattr(contact_record,
                                       'contact',
                                       None),
                               'name',
                               '')
        log_change(contact_record, None, request.user, partner,
                   contact_name, action_type=DELETION,
                   impersonator=request.impersonator)
        contact_record.archive()
        return HttpResponseRedirect(reverse('partner_records')+'?company=' +
                                    str(company.id)+'&partner=' +
                                    str(partner_id))
    elif content_id == ContentType.objects.get_for_model(PartnerSavedSearch).id:
        saved_search = get_object_or_404(PartnerSavedSearch, id=item_id)
        partner = get_object_or_404(Partner, id=partner_id, owner=company)
        log_change(saved_search, None, request.user, partner,
                   saved_search.email, action_type=DELETION,
                   impersonator=request.impersonator)
        saved_search.delete()
        return HttpResponseRedirect(reverse('partner_searches')+'?company=' +
                                    str(company.id)+'&partner=' +
                                    str(partner_id))
    else:
        partner = get_object_or_404(Partner, id=partner_id, owner=company)
        contact = get_object_or_404(Contact, id=contact_id)
        log_change(contact, None, request.user, partner, contact.name,
                   action_type=DELETION, impersonator=request.impersonator)
        contact.archive()
        return HttpResponseRedirect(reverse('partner_details')+'?company=' +
                                    str(company.id)+'&partner=' +
                                    str(partner_id))


@warn_when_inactive(feature='Partner Relationship Manager is')
@requires('read partner')
def prm_overview(request):
    """
    View that is the "Overview" of one's Partner Activity.

    """

    company, partner, _ = prm_worthy(request)

    most_recent_activity = partner.get_logs()
    records = partner.get_contact_records()
    total_records = partner.get_contact_records().count()
    communication = records.order_by('-date_time')
    referrals = records.filter(contact_type='job').count()
    records = records.exclude(contact_type='job').count()
    most_recent_communication = communication[:1]
    saved_searches = partner.get_searches()
    most_recent_saved_searches = saved_searches[:1]

    ctx = {'partner': partner,
           'company': company,
           'recent_activity': most_recent_activity,
           'recent_communication': most_recent_communication,
           'recent_ss': most_recent_saved_searches,
           'count': records,
           'referrals': referrals,
           'view_name': 'PRM',
           'total_records': total_records}

    return render_to_response('mypartners/overview.html', ctx,
                              RequestContext(request))


@warn_when_inactive(feature='Partner Relationship Manager is')
@requires('read tag')
def partner_tagging(request):
    company = get_company_or_404(request)

    tags = Tag.objects.filter(company=company).order_by('name')

    ctx = {'company': company,
           'create_tags': json.dumps(request.user.can(company, 'create tag')),
           'tags': tags}

    return render_to_response('mypartners/partner_tagging.html', ctx,
                              RequestContext(request))


@warn_when_inactive(feature='Partner Relationship Manager is')
@requires('update tag')
def edit_partner_tag(request):
    company = get_company_or_404(request)

    if request.POST:
        pk = request.GET.get('id')
        tag = Tag.objects.filter(pk=pk).first()
        form = TagForm(instance=tag, auto_id=False, data=request.POST)

        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('partner_tagging'))
        else:
            ctx = {
                'company': company,
                'form': form,
                'tag': tag
            }
            return render_to_response('mypartners/edit_tag.html', ctx,
                                      RequestContext(request))
    else:
        data = {'id': request.GET.get('id')}
        pk = request.GET.get('id')
        tag = Tag.objects.filter(pk=pk).first()
        form = TagForm(instance=tag, auto_id=False)

        ctx = {
            'company': company,
            'tag': tag,
            'form': form
        }
        return render_to_response('mypartners/edit_tag.html', ctx,
                                  RequestContext(request))


@warn_when_inactive(feature='Partner Relationship Manager is')
@requires('update contact')
def edit_location(request):
    company, partner, _ = prm_worthy(request)
    contact = get_object_or_none(Contact, id=request.REQUEST.get('id'))
    location = get_object_or_none(
        Location, id=request.REQUEST.get('location'))

    if request.method == 'POST':
        if location:
            form = LocationForm(request.POST, instance=location)
        else:
            form = LocationForm(request.POST)

        if form.is_valid():
            location = form.save(request)

            if location not in contact.locations.all():
                contact.locations.add(location)
                contact.update_last_action_time()

            content_id = ContentType.objects.get_for_model(contact.__class__).pk
            return HttpResponseRedirect(
                reverse('edit_contact') + "?partner=%s&id=%s&ct=%s" % (
                    partner.id, contact.id, content_id))
    else:
        form = LocationForm(instance=location)

    ctx = {
        'form': form,
        'company': company,
        'partner': str(partner.id),
    }
    if contact:
        ctx['contact'] = str(contact.id)
    if location:
        ctx['location'] = str(location.id)

    return render_to_response(
        'mypartners/edit_location.html', ctx, RequestContext(request))


@warn_when_inactive(feature='Partner Relationship Manager is')
@requires('update contact')
def delete_location(request):
    company, partner, _ = prm_worthy(request)
    contact = get_object_or_404(Contact, pk=request.REQUEST.get('id', 0))
    location = get_object_or_404(
        Location, pk=request.REQUEST.get('location', 0))

    contact.update_last_action_time()
    contact.locations.remove(location)

    content_id = ContentType.objects.get_for_model(contact.__class__).pk
    return HttpResponseRedirect(
        reverse('edit_contact') + "?partner=%s&id=%s&ct=%s" % (
            partner.id, contact.id, content_id))


@warn_when_inactive(feature='Partner Relationship Manager is')
@requires('delete tag')
def delete_partner_tag(request):
    company = get_company_or_404(request)

    pk = request.GET.get('id')
    tag = Tag.objects.filter(pk=pk).first()

    if tag:
        tag.delete()

    return HttpResponseRedirect(reverse('partner_tagging'))


@warn_when_inactive(feature='Partner Relationship Manager is')
@requires('read partner saved search')
def prm_saved_searches(request):
    """
    View that lists the Partner's Saved Searches

    """
    company, partner, user = prm_worthy(request)
    saved_searches = partner.get_searches()
    saved_searches = add_pagination(request, saved_searches)
    if request.is_ajax():
        ctx = {
            'partner': partner,
            'searches': saved_searches
        }
        response = HttpResponse()
        html = render_to_response(
            'mypartners/includes/searches_column.html', ctx,
            RequestContext(request))
        response.content = html.content
        return response

    ctx = {
        'searches': saved_searches,
        'company': company,
        'partner': partner,
    }
    return render_to_response('mypartners/partner_searches.html', ctx,
                              RequestContext(request))


@warn_when_inactive(feature='Partner Relationship Manager is')
@requires('create partner saved search')
def prm_edit_saved_search(request):
    company, partner, user = prm_worthy(request)
    item_id = request.REQUEST.get('id')
    copy_id = request.REQUEST.get('copies')

    if item_id:
        instance = get_object_or_404(PartnerSavedSearch, id=item_id)
        form = PartnerSavedSearchForm(partner=partner, instance=instance,
                                      request=request)
    elif copy_id:
        try:
            values = PartnerSavedSearch.objects.filter(pk=copy_id).values()[0]
        except IndexError:
            # saved search to be copied doesn't exist since values is empty
            raise Http404("mypartners.views.prm_edit_saved_search: "
                          "PartnerSavedSearch with provided id doesn't exist")
        else:
            values['label'] = "Copy of %s" % values['label']
            values.pop('email', None)
            values.pop('notes', None)
            values.pop('custom_message', None)
            values.pop('partner_message', None)
            form = PartnerSavedSearchForm(initial=values, partner=partner,
                                          request=request)
    else:
        form = PartnerSavedSearchForm(partner=partner, request=request)


    microsites = company.prm_saved_search_sites.values_list('domain', flat=True)
    microsites = [site.replace('http://', '').replace('https://', '').lower()
                  for site in microsites]

    ctx = {
        'company': company,
        'partner': partner,
        'item_id': item_id,
        'form': form,
        'microsites': set(microsites),
        'content_type': ContentType.objects.get_for_model(PartnerSavedSearch).id,
        'view_name': 'PRM',
        'create_tags': json.dumps(request.user.can(company, 'create tag'))
    }

    return render_to_response('mypartners/partner_edit_search.html', ctx,
                              RequestContext(request))


@warn_when_inactive(feature='Partner Relationship Manager is')
@requires('read contact')
def verify_contact(request):
    """
    Checks to see if a contact has a My.jobs account. Checks to see if they are
    active as well.

    """
    if request.REQUEST.get('action') != 'validate':
        raise Http404("mypartners.views.verify_contact: "
                      "'action' is not 'validate'")

    email = request.REQUEST.get('email')
    if email == 'None':
        data = {
            'status': 'None',
            'message': 'If a contact does not have an email they will not '
                       'show up on this list.',
        }
    else:
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            data = {
                'status': 'unverified',
                'message': 'A My.jobs account will be created for this '
                           'contact, which will include a personal greeting.',
            }
        else:
            # Check to see if user is active
            if user.is_active:
                data = {
                    'status': 'verified',
                    'message': '',
                }
            else:
                data = {
                    'status': 'unverified',
                    'message': 'This contact has an account on My.jobs already '
                               'but has yet to activate their account.',
                }
    return HttpResponse(json.dumps(data))


@requires('create partner saved search')
def partner_savedsearch_save(request):
    """
    Handles saving the PartnerSavedSearchForm and creating the inactive user
    if it is needed.

    """
    company, partner, _ = prm_worthy(request)
    item_id = request.REQUEST.get('id', None)

    if item_id:
        item = get_object_or_404(PartnerSavedSearch, id=item_id,
                                 provider=company.id)
        form = PartnerSavedSearchForm(instance=item, auto_id=False,
                                      data=request.POST,
                                      partner=partner,
                                      request=request)
        if form.is_valid():
            form.save()
            return HttpResponse(status=200)
        else:
            return HttpResponse(json.dumps(form.errors))
    form = PartnerSavedSearchForm(request.POST, partner=partner,
                                  request=request)

    # Since the feed is created below, this will always be invalid.
    if 'feed' in form.errors:
        del form.errors['feed']

    if form.is_valid():
        instance = form.instance
        instance.provider = company
        instance.partner = partner
        instance.created_by = request.user
        instance.custom_message = instance.partner_message
        form.save()
        return HttpResponse(status=200)
    else:
        return HttpResponse(json.dumps(form.errors))


@warn_when_inactive(feature='Partner Relationship Manager is')
@requires('read partner saved search')
def partner_view_full_feed(request):
    """
    PartnerSavedSearch feed.

    """
    company, partner, user = prm_worthy(request)
    search_id = request.REQUEST.get('id')
    saved_search = get_object_or_404(PartnerSavedSearch, id=search_id)

    if company == saved_search.partnersavedsearch.provider:
        try:
            items, _ = saved_search.get_feed_items()
            items = [item for item in items if item.get('new')]
            count = len(items)
        except HTTPError:
            items = None
            count = 0
        start_date = date.today() + timedelta(get_interval_from_frequency(
            saved_search.frequency))
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
        'partner': partner,
        'company': company,
        'start_date': start_date,
        'count': count,
    }

    return render_to_response('mysearches/view_full_feed.html', ctx,
                              RequestContext(request))


@warn_when_inactive(feature='Partner Relationship Manager is')
@requires('read communication record')
def prm_records(request):
    """
    ContactRecord overview and ContactRecord overview from PRM reports.

    """
    company, partner, _ = prm_worthy(request)
    _, _, contact_records = get_records_from_request(request)
    paginated_records = add_pagination(request, contact_records)

    ctx = {
        'partner': partner,
        'records': paginated_records
    }

    if request.is_ajax():
        response = HttpResponse()
        html = render_to_response(
            'mypartners/includes/contact_record_column.html', ctx,
            RequestContext(request))
        response.content = html.content
        return response

    contact_type_choices = (('all', 'All'),) + CONTACT_TYPE_CHOICES
    contact_choices = [('all', 'All')] + list(contact_records.values_list(
        'contact__name', 'contact__name').distinct().order_by('contact__name'))

    ctx.update({
        'admin_id': request.REQUEST.get('admin'),
        'company': company,
        'contact_choices': contact_choices,
        'contact_type_choices': contact_type_choices,
        'view_name': 'PRM',
    })

    return render_to_response('mypartners/main_records.html', ctx,
                              RequestContext(request))


@warn_when_inactive(feature='Partner Relationship Manager is')
@requires('create communication record', 'update communication record')
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
            form.save(request, partner)
            search_params = request.GET.copy()
            search_params.update({'id': form.instance.pk})
            return HttpResponseRedirect(reverse('record_view') + '?' +
                                        urlencode(search_params))
    else:
        form = ContactRecordForm(partner=partner, instance=instance)

    ctx = {
        'company': company,
        'partner': partner,
        'content_type': ContentType.objects.get_for_model(ContactRecord).id,
        'item_id': record_id,
        'form': form,
        'create_tags': json.dumps(request.user.can(company, 'create tag'))
    }
    return render_to_response('mypartners/edit_record.html', ctx,
                              RequestContext(request))


@warn_when_inactive(feature='Partner Relationship Manager is')
@requires('read communication record')
def prm_view_records(request):
    """
    View an individual ContactRecord.

    """

    company, partner, _ = prm_worthy(request)
    _, _, contact_records = get_records_from_request(request)
    page_number = int(request.GET.get('page', 1))
    record_id = int(request.GET.get('id', 0))

    # change number of objects per page
    paginator = Paginator(contact_records, 1)

    if record_id:
        pks = list(contact_records.values_list('pk', flat=True))

        if record_id in pks:
            page_number = pks.index(record_id) + 1
        else:
            page_number = 1
            paginator = Paginator(
                ContactRecord.objects.filter(pk=record_id), 1)

    paginated_records = paginator.page(page_number)
    record = paginated_records.object_list[0]

    attachments = record.prmattachment_set.all()
    record_history = ContactLogEntry.objects.filter(
        object_id=record.pk, content_type_id=ContentType.objects.get_for_model(
            ContactRecord).pk)

    search_params = request.GET.copy()
    navigation_params = search_params.copy()
    navigation_params.pop('id', None)

    ctx = {
        'record': record,
        'records': paginated_records,
        'partner': partner,
        'company': company,
        'attachments': attachments,
        'record_history': record_history,
        'view_name': 'PRM',
        'page': page_number,
        'search_params': urlencode(search_params),
        'navigation_params': urlencode(navigation_params)
    }

    return render_to_response('mypartners/view_record.html', ctx,
                              RequestContext(request))

@requires('read contact')
def get_contact_information(request):
    """
    Returns a json object containing a contact's email address and
    phone number if they have one.

    """
    if request.method == "POST" and request.is_ajax():
        _, partner, _ = prm_worthy(request)

        contact_id = request.POST.get('contact') or None
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
    else:
        raise Http404("mypartners.views.get_contact_information: "
                      "request is not an AJAX POST")


@requires("read communication record")
def get_records(request):
    """
    Returns a json object containing the records matching the search
    criteria (contact, contact_type, and date_time range) rendered using
    records.html and the date range and date string requiresd to update
    the time_filter.html template to match the search.

    """
    company, partner, user = prm_worthy(request)

    contact = request.REQUEST.get('contact')
    contact_type = request.REQUEST.get('record_type')

    contact = None if contact in ['all', 'undefined'] else contact
    contact_type = None if contact_type in ['all', 'undefined'] else contact_type
    dt_range, date_str, records = get_records_from_request(request)

    ctx = {
        'records': records.order_by('-date_time'),
        'company': company,
        'partner': partner,
        'contact_type': None if contact_type == 'all' else contact_type,
        'contact_name': None if contact == 'all' else contact,
        'view_name': 'PRM'
    }

    # Because javascript is going to use this, not a template,
    # convert to localtime here
    date_end = localtime(dt_range[1].replace(tzinfo=pytz.utc))
    date_start = localtime(dt_range[0].replace(tzinfo=pytz.utc))

    data = {
        'month_end': date_end.strftime('%m'),
        'day_end': date_end.strftime('%d'),
        'year_end': date_end.strftime('%Y'),
        'month_start': date_start.strftime('%m'),
        'day_start': date_start.strftime('%d'),
        'year_start': date_start.strftime('%Y'),
        'date_str': date_str,
        'html': render_to_response('mypartners/records.html', ctx,
                                   RequestContext(request)).content,
    }
    return HttpResponse(json.dumps(data))


@warn_when_inactive(feature='Partner Relationship Manager is')
@requires("read communication record")
def get_uploaded_file(request):
    """
    Determines the location of a PRMAttachment (either in S3 or in local
    storage) and redirects to it.

    PRMAttachments stored in S3 requires a generated key and have a 10 minute
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


@warn_when_inactive(feature='Partner Relationship Manager is')
@requires('read communication record')
def partner_main_reports(request):
    company, partner, user = prm_worthy(request)
    dt_range, date_str, records = get_records_from_request(request)

    ctx = {
        'admin_id': request.REQUEST.get('admin'),
        'partner': partner,
        'company': company,
        'contacts': records.contacts,
        'total_records': records.communication_activity.count(),
        'referral': records.referrals,
        'top_contacts': records.contacts[:3],
        'others': sum(contact['records'] for contact in records.contacts[3:]),
        'view_name': 'PRM',
        'date_start': dt_range[0],
        'date_end': dt_range[1],
        'date_display': date_str,
    }
    return render_to_response('mypartners/partner_reports.html', ctx,
                              RequestContext(request))


@requires('read communication record')
def partner_get_records(request):
    if request.method == 'GET':
        prm_worthy(request)

        dt_range, date_str, records = get_records_from_request(request)
        records = records.exclude(contact_type='job')
        email = records.filter(contact_type='email').count()
        email += records.filter(contact_type='pssemail').count()
        phone = records.filter(contact_type='phone').count()
        meetingorevent = records.filter(contact_type='meetingorevent').count()

        # figure names
        if email != 1:
            email_name = 'Emails'
        else:
            email_name = 'Email'
        if phone != 1:
            phone_name = 'Phone Calls'
        else:
            phone_name = 'Phone Call'
        if meetingorevent != 1:
            meetingorevent_name = 'Meeting or Event'
        else:
            meetingorevent_name = 'Meetings & Events'

        data = SortedDict()

        data['email'] = {"count": email, "name": email_name,
                         'typename': 'email'}
        data['phone'] = {"count": phone, "name": phone_name,
                         'typename': 'phone'}
        data['meetingorevent'] = {"count": meetingorevent,
                                  "name": meetingorevent_name,
                                  "typename": "meetingorevent"}

        return HttpResponse(json.dumps(data))
    else:
        raise Http404("mypartners.views.partner_get_records: "
                      "request method is not GET")


@requires('read communication record')
def partner_get_referrals(request):
    if request.method == 'GET':
        prm_worthy(request)
        dt_range, date_str, records = get_records_from_request(request)

        # figure names
        if records.applications != 1:
            app_name = 'Applications'
        else:
            app_name = 'Application'
        if records.interviews != 1:
            interview_name = 'Interviews'
        else:
            interview_name = 'Interview'
        if records.hires != 1:
            hire_name = 'Hires'
        else:
            hire_name = 'Hire'

        data = {
            'applications': {'count': records.applications, 'name': app_name,
                             'typename': 'job'},
            'interviews': {'count': records.interviews, 'name': interview_name,
                           'typename': 'job'},
            'hires': {'count': records.hires, 'name': hire_name,
                      'typename': 'job'},
        }

        return HttpResponse(json.dumps(data))
    else:
        raise Http404("mypartners.views.partner_get_referrals: "
                      "request method is not GET")


@warn_when_inactive(feature='Partner Relationship Manager is')
@user_passes_test(lambda u: User.objects.is_group_member(u, 'Employer'))
@requires("read communication record")
def prm_export(request):
    # TODO: investigate using django's builtin serialization for XML
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
                value = getattr(record, field, '')

                if hasattr(value, 'all'):
                    value = ', '.join([val.name for val in value.all() if val])

                xml.text = contact_record_val_to_str(value)
        response = HttpResponse(etree.tostring(root, pretty_print=True,
                                               xml_declaration=True),
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
    # CSV/XLS
    else:
        response = HttpResponse(content_type='text/csv')
        writer = unicodecsv.writer(response, encoding='utf-8')
        writer.writerow(fields)
        for record in records:
            values = [getattr(record, field, '') for field in fields]
            values = [
                contact_record_val_to_str(v)
                if not hasattr(v, 'all') else
                ', '.join([val.name for val in v.all() if val]) for v in values
            ]
            # Remove the HTML and reformat.
            values = [strip_tags(v) for v in values]
            # replaces multiple occurences of space by a single sapce.
            values = [' '.join(filter(bool, v.split(' '))) for v in values]
            values = [re.sub('\s+\n\s+', '\n', v) for v in values]
            writer.writerow(values)

    response['Content-Disposition'] = 'attachment; ' \
                                      'filename="company_record_report".%s' \
                                      % file_format

    return response


@csrf_exempt
def process_email(request):
    """
    Creates one or more contact/outreach records from an email
    received via POST.
    """
    PRM_EMAIL_HOST = 'prm@%s' % settings.PRM_EMAIL_HOST
    if request.method != 'POST':
        # We receive emails via HTTP POST. Any other verbs are denied.
        logger.warning("process_email: received {method} request, returning "
                       "early.".format(method=request.method))
        return HttpResponse(status=200)

    admin_email = request.REQUEST.get('from')
    headers = request.REQUEST.get('headers')
    key = request.REQUEST.get('key')
    subject = request.REQUEST.get('subject')
    email_text = request.REQUEST.get('text')
    if key != settings.EMAIL_KEY:
        logger.warning("process_email: invalid email key provided, returning "
                       "early.")
        return HttpResponse(status=200)
    if headers:
        parser = HeaderParser()
        headers = parser.parsestr(headers)

    if headers and 'Date' in headers:
        try:
            date_time = get_datetime_from_str(headers.get('Date'))
        except Exception:
            date_time = now()
    else:
        date_time = now()

    to = request.REQUEST.get('to', '')
    cc = request.REQUEST.get('cc', '')
    recipient_emails_and_names = getaddresses(["%s, %s" % (to, cc)])
    bcc_addresses = []
    try:
        # prm@my.jobs (and other outreach addresses) appears in the 'envelope'
        # parameter posted from SendGrid if we were added to this email via BCC
        envelope = json.loads(request.POST.get('envelope',
                                               ''))
    except ValueError:
        # envelope was not valid JSON or was not provided
        pass
    else:
        bcc_addresses = envelope.get('to', [])
        if bcc_addresses:
            recipient_emails_and_names += getaddresses(bcc_addresses)
    contact_emails = filter(None,
                            [email[1] for email in recipient_emails_and_names])

    NUO_HOSTS = OutreachEmailAddress.objects.filter(email__in=[
        contact.rsplit('@', 1)[0] for contact in contact_emails])
    NUO_LOCAL = [host.email for host in NUO_HOSTS]
    admin_user, admin_email, is_nuo, error = get_admin(request, admin_email,
                                                       NUO_HOSTS)
    if error is not None:
        return error

    newrelic.agent.add_custom_parameter("to", to)
    newrelic.agent.add_custom_parameter("cc", cc)
    newrelic.agent.add_custom_parameter("bcc", bcc_addresses)
    newrelic.agent.add_custom_parameter("admin_email", admin_email)
    newrelic.agent.add_custom_parameter("contact_emails",
                                        ", ".join(contact_emails))

    contact_emails, date_time = determine_contacts(
        contact_emails, email_text, PRM_EMAIL_HOST, NUO_LOCAL, admin_email,
        date_time)

    partners, company, error = determine_partners(
        request, admin_user, contact_emails, admin_email, NUO_HOSTS, is_nuo)
    if error is not None:
        return error
    possible_contacts, created_contacts, unmatched_contacts = make_contacts(
        request, contact_emails, partners, admin_user)

    logger.info("created_contacts: {contacts}".format(contacts=", ".join([
                contact.email for contact in created_contacts])))
    logger.info("unmatched_contacts: {contacts}".format(contacts=", ".join(
                unmatched_contacts)))

    attachments, error = make_attachments(request, contact_emails, admin_email)
    if error is not None:
        return error
    created_records, attachment_failures, error = make_records(
        request, date_time, possible_contacts, created_contacts,
        contact_emails, admin_email, admin_user, subject, email_text,
        attachments, NUO_HOSTS)
    if error is not None:
        return error
    send_contact_record_email_response(created_records, created_contacts,
                                       attachment_failures, unmatched_contacts,
                                       None, admin_email,
                                       is_nuo=not bool(admin_user),
                                       company=company,
                                       buckets=NUO_LOCAL)
    return HttpResponse(status=200)


def check_outreach_domain(admin_email):
    """
    Grabs an outreach email domain from an email address, if one exists
    """
    domain = admin_email.rsplit('@', 1)[1]

    return OutreachEmailDomain.objects.filter(
        domain=domain).first()


def check_company_connections(request, admin_email, nuo_hosts, email_domain):
    """
    When this is called, we know that nuo_hosts is either empty or
    contains outreach email addresses from at most one company.

    What we need to do is grab the user, if one exists, that is associated
    with the provided email address and determine what, if any, companies
    it is connected to.

    Inputs:
    :request: http request
    :admin_email: sender of this email
    :nuo_hosts: list of outreach addresses found in this email
    :email_domain: OutreachEmailDomain instance that matches admin_email,
        if one exists

    Outputs:
    :admin_user: user connected to admin_email, if one exists
    :admin_email: admin_user's primary address (if admin_user exists) or input
        admin_email
    :is_nuo: bool; is this a non-user outreach email
    :error:
    """
    admin_user = User.objects.get_email_owner(admin_email,
                                              only_verified=True)

    if admin_user is None:
        if nuo_hosts:
            if email_domain:
                # It is perfectly acceptable for a non-user outreach
                # participant to not have an associated User.
                logger.info("Email address {email} could not be associated "
                            "with a verified user but NUO addresses {nuo} "
                            "were found".format(
                                email=admin_email,
                                nuo=",".join(map(unicode, nuo_hosts))))
                return None, admin_email, True, None
            else:
                return None, None, None, HttpResponse(20)
        else:
            # At least one of admin_user or nuo_hosts must be truthy -
            # non-user outreach participants cannot create records by emailing
            # prm@my.jobs
            logger.warning(
                "The email address {email} could not be associated "
                "with a verified user.".format(email=admin_email))
            logger.warning("POST data: {post}".format(post=json.dumps(
                request.POST)))
            return None, None, None, HttpResponse(200)
    else:
        user_companies = admin_user.roles.values_list('company',
                                                      flat=True).distinct()
        nuo_companies = set(nuo_hosts.values_list('company',
                                                  flat=True).distinct())
        if ((nuo_companies.issubset(user_companies)
                and len(nuo_companies) == 1)
                or (not bool(nuo_companies))):
            # All outreach emails in use mapped to a single company that this
            # user is a part of or no outreach emails were used
            admin_email = admin_user.email
            is_nuo = False
        elif email_domain and all([email_domain.company.pk == outreach
                                   for outreach in nuo_companies]):
            # The current user's email matches an outreach domain and all
            # outreach emails that were used match that domain's owner
            admin_user = None
            is_nuo = True
        else:
            logger.warning(
                "The account associated with {email} is connected to or "
                "sent email to multiple companies".format(email=admin_email))
            return None, None, None, HttpResponse(200)
        return admin_user, admin_email, is_nuo, None


def get_admin(request, admin_email, nuo_hosts):
    """
    Determines the sender of this email and maps that address to a user
    if appropriate.

    Inputs:
    :request: http request
    :admin_email: email of sender
    :nuo_hosts: list of outreach emails found in this email

    Outputs:
    :admin_user: None if is_nuo is True, else the user matching admin_email
    :admin_email: input admin_email, or admin_user.email if different
    :is_nuo: bool; is this a non-user outreach email
    :error: returned to denote a problem with the email (usually due to an
        invalid use of this system)
    """
    admin_emails = [email for name, email in getaddresses([admin_email])]

    # Get the first valid address based on admin_emails. getaddresses can
    # return an extra tuple with an invalid email address.
    email_validator = EmailValidator()
    for admin_email in admin_emails:
        try:
            email_validator(admin_email)
        except ValidationError:
            pass
        else:
            break

    email_domain = None
    if nuo_hosts:
        email_domain = check_outreach_domain(admin_email)
        if email_domain:
            nuo_companies = set(host.company for host in nuo_hosts)
            if set([email_domain.company]) != nuo_companies:
                # nuo_companies either does not contain the correct company
                # or contains more than one company; either way, drop this mail
                logger.warning(
                    u"Email address {email} matches a domain used by {member} "
                    u"({match}) but sent message to {addresses}".format(
                        email=admin_email,
                        match=email_domain.domain,
                        addresses=u', '.join(host.address
                                             for host in nuo_hosts)))
                return None, None, None, HttpResponse(200)
            else:
                return None, admin_email, True, None
    return check_company_connections(request, admin_email, nuo_hosts,
                                     email_domain)


def determine_contacts(contact_emails, email_text, prm_email_host,
                       nuo_local, admin_email, date_time):
    """
    Examines various parts of the received email and extracts addresses
    from to/cc or forward headers

    Inputs:
    :contact_emails: to/cc fields
    :email_text: email body
    :prm_email_host: prm@my.jobs on production, prm@qc.my.jobs on qc
    :nuo_local: list of outreach addresses that were found in this email
    :admin_email: sender of this email
    :date_time: time that we think this email was sent; may be modified by
        forward headers

    Outputs:
    :contact_emails: input list, modified by forward status and nuo_local list
    :date_time: input date_time or the value we parsed from forward headers
    """
    # If this is a forward, we need to parse forward headers.
    # There are three different cases in which we know this is a forward.
    # 1) There are no contacts
    forward = contact_emails == []
    # 2) The only contacts are outreach email addresses
    forward |= (
        len(contact_emails) == len(nuo_local) and
        set(contact.lower().rsplit('@', 1)[0]
            for contact in contact_emails) == set(nuo_local))
    # 3) The only contact is the normal PRM address
    forward |= (len(contact_emails) == 1 and
                contact_emails[0].lower() == prm_email_host)
    if forward:
        # If PRM_EMAIL_HOST is the only contact, assume it's a forward.
        fwd_headers = build_email_dicts(email_text)
        try:
            recipient_emails_and_names = fwd_headers[0]['recipients']
            contact_emails = [recipient[1] for recipient
                              in recipient_emails_and_names]
            date_time = fwd_headers[0]['date']
        except IndexError:
            contact_emails = []

    # Prevent duplicate contact records for an email address because
    # the address was in both To and CC.
    contact_emails = list(set(contact_emails))

    validated_contacts = []
    for element in contact_emails:
        if (not (element.lower() == prm_email_host
                 or element.lower().rsplit('@', 1)[0] in nuo_local)
                and validate_email(element)):
            validated_contacts.append(element)

    contact_emails = validated_contacts

    try:
        contact_emails.remove(admin_email)
    except ValueError:
        pass
    return contact_emails, date_time


def determine_partners(request, admin_user, contact_emails, admin_email,
                       nuo_hosts, is_nuo):
    """
    Ensures that there is one company connected to either admin_user or
    nuo_hosts, as appropriate. Grabs all partners for that company.

    Inputs:
    :request: http request
    :admin_user: sending user; None for non-user outreach
    :contact_emails: final list of contact emails
    :admin_email: sender of this email
    :nuo_hosts: list of outreach addresses found in this email
    :is_nuo: bool; is this a non-user outreach email

    Outputs:
    :partners: list of partners owned by this company
    :company: only company tied to this user or the company that owns the
        outreach addresses that were used
    :error:
    """
    partners = []

    error_text = None
    if is_nuo:
        companies = set(host.company for host in nuo_hosts)
        if len(companies) > 1:
            error_text = (
                "The outreach addresses used are for multiple companies. To "
                "create records for multiple companies, send mail to each "
                "separately.")
            logger.warning("Email address {email} sent to multiple outreach "
                           "addresses".format(email=admin_email))
            logger.warning("POST data: {post}".format(
                post=json.dumps(request.POST)))
        else:
            company = companies.pop()
            partners = company.partner_set.all()
    else:
        company_count = admin_user.roles.values(
            "company").distinct().count()

        if company_count > 1:
            error_text = (
                "Your account is setup as the admin for multiple companies. "
                "Because of this we cannot match this email with a "
                "specific partner on a specific company with 100% certainty. "
                "You will need to login to My.jobs and go to "
                "https://secure.my.jobs/prm to create your record manually.")
            logger.warning("User with email address {user} is associated with "
                           "multiple companies.".format(user=admin_user))
            logger.warning("POST data: {post}".format(
                post=json.dumps(request.POST)))

        else:
            company = admin_user.roles.first().company
            partners = company.partner_set.all()
    if error_text:
        send_contact_record_email_response([], [], [], contact_emails,
                                           error_text, admin_email)
        return None, None, HttpResponse(200)

    return partners, company, None


def make_contacts(request, contact_emails, partners, admin_user):
    """
    Makes a list of Contact objects that consists of rows pulled from the
    database (if an email already exists as a contact in one of the provided
    partners) or new rows (if no row exists and we were able to determine
    the correct partner)

    Inputs:
    :request: http request
    :contact_emails: list of emails that we will attempt to turn into Contact
        objects
    :partners: list of partners that will be used to determine if a contact
        exists
    :admin_user: sending user; used to log changes

    Outputs:
    :possible_contacts: list of existing rows in the Contact table
    :created_contacts: list of rows that we added to the Contact table
    :unmatched_contacts: list of email addresses that we were unable to tie
        to a partner
    """
    possible_contacts, created_contacts, unmatched_contacts = [], [], []
    for contact in contact_emails:
        try:
            matching_contacts = Contact.objects.filter(email=contact,
                                                       partner__in=partners)
            [possible_contacts.append(x) for x in matching_contacts]
            if not matching_contacts:
                poss_partner = find_partner_from_email(partners, contact)
                if poss_partner:
                    new_contact = Contact.objects.create(name=contact,
                                                         email=contact,
                                                         partner=poss_partner)
                    change_msg = "Contact was created from email."
                    log_change(new_contact, None, admin_user,
                               new_contact.partner, new_contact.name,
                               action_type=ADDITION, change_msg=change_msg,
                               impersonator=request.impersonator)
                    created_contacts.append(new_contact)
                else:
                    unmatched_contacts.append(contact)
        except ValueError:
            unmatched_contacts.append(contact)
    return possible_contacts, created_contacts, unmatched_contacts


def make_attachments(request, contact_emails, admin_email):
    """
    Creates a list of attachments from the provided email.

    Inputs:
    :request: http request
    :contact_emails: list of email addresses from this email; used in messaging
    :admin_email: sender of this email

    Outputs:
    :attachments: list of attachments
    :error:
    """
    num_attachments = int(request.POST.get('attachments', 0))
    attachments = []
    for file_number in range(1, num_attachments+1):
        try:
            attachment = request.FILES['attachment%s' % file_number]
        except KeyError:
            error = "There was an issue with the email attachments. The " \
                    "contact records for the email will need to be created " \
                    "manually."
            send_contact_record_email_response([], [], [], contact_emails,
                                               error, admin_email)
            return None, HttpResponse(200)
        attachments.append(attachment)
    return attachments, None


def make_records(request, date_time, possible_contacts, created_contacts,
                 contact_emails, admin_email, admin_user, subject, email_text,
                 attachments, nuo_hosts):
    """
    Creates communication/outreach records as appropriate from the information
    provided.

    Inputs:
    :request: http request
    :date_time: date/time that we've determined this record occurred
    :possible_contacts: list of contacts pulled from the database
    :created_contacts: list of created contacts
    :contact_emails: list of email addresses pulled from this email
    :admin_email: sender of this email
    :admin_user: user connected to admin_email
    :subject: subject of the email we're processing
    :email_text: body of the email we're processing
    :attachments: list of attachments
    :nuo_hosts: list of outreach addresses we found in this email

    Outputs:
    :created_records: list of records that were created
    :attachment_failures: list of attachments that could not be turned into
        PRMAttachments for some reason
    :error:
    """
    created_records = []
    attachment_failures = []
    date_time = now() if not date_time else date_time
    all_contacts = possible_contacts + created_contacts
    if not all_contacts:
        error = "No contacts or contact records could be created " \
                "from this email. You will need to log in and manually " \
                "create contact records for this email."
        send_contact_record_email_response([], [], [], contact_emails,
                                           error, admin_email)
        return None, None, HttpResponse(200)

    for contact in all_contacts:
        if admin_user:
            change_msg = "Email was sent by %s to %s" % \
                         (admin_user.get_full_name(), contact.name)
            record = ContactRecord.objects.create(partner=contact.partner,
                                                  contact_type='email',
                                                  contact=contact,
                                                  contact_email=contact.email,
                                                  contact_phone=contact.phone,
                                                  created_by=admin_user,
                                                  date_time=date_time,
                                                  subject=subject,
                                                  notes=force_text(email_text))
            try:
                for attachment in attachments:
                    prm_attachment = PRMAttachment()
                    prm_attachment.attachment = attachment
                    prm_attachment.contact_record = record
                    prm_attachment._partner = contact.partner
                    prm_attachment.save()
                    # The file pointer for this attachment is now at the end of
                    # the file; reset it to the beginning for future use.
                    attachment.seek(0)
            except AttributeError:
                attachment_failures.append(record)
            log_change(record, None, admin_user, contact.partner, contact.name,
                       action_type=ADDITION, change_msg=change_msg,
                       impersonator=request.impersonator)
            created_records.append(record)
        else:
            workflow_state, _ = OutreachWorkflowState.objects.get_or_create(
                state='New')
            for email in nuo_hosts:
                record = OutreachRecord.objects.create(
                    outreach_email=email, from_email=admin_email,
                    email_body=email_text, subject=subject,
                    current_workflow_state=workflow_state)
                record.partners.add(contact.partner)
                record.contacts.add(contact)
                created_records.append(record)
    return created_records, attachment_failures, None


@restrict_to_staff()
@requires("read outreach email address")
def nuo_main(request):
    """
    View for non user outreach module
    GET /prm/view/nonuseroutreach
    """
    company = get_company_or_404(request)

    ctx = { "company": company }

    return render_to_response('nonuseroutreach/nuo_main.html', ctx,
                              RequestContext(request))


@restrict_to_staff()
@requires("read outreach email address")
def api_get_nuo_inbox_list(request):
    """
    GET /prm/api/nonuseroutreach/inbox/list

    Retrieves all non user outreach inboxes for a company. Returns json object
    with id, email of each.

    """
    company = get_company_or_404(request)
    inboxes = OutreachEmailAddress.objects.filter(company=company).values(
        'pk', 'email')

    return HttpResponse(
        json.dumps(
            list(inboxes)), content_type='application/json; charset=utf-8')


@restrict_to_staff()
@requires("create outreach email address")
def api_add_nuo_inbox(request):
    """
    Create a new ``OutreachEmailAddress`` instance from the provided email.

    """
    company = get_company_or_404(request)
    if not request.method == "POST":
        raise Http404("This view is only accessible via POST method, not %s" %
                      request.method)

    inbox = OutreachEmailAddress.objects.create(
        company=company,
        email=request.POST.get("email"))
    ctx = {"pk": inbox.pk, "email": inbox.email}

    return HttpResponse(json.dumps(ctx),
                        content_type='application/json; charset=utf-8')


@restrict_to_staff()
@requires("delete outreach email address")
def api_delete_nuo_inbox(request):
    """
    Remove an existing NonUserOutreachEmailAddress

    """
    if not request.method == "POST":
        raise Http404("This view is only accessible via POST method, not %s" %
                      request.method)

    inbox = OutreachEmailAddress.objects.filter(pk=request.POST.get('id'))
    if inbox:
        inbox.delete()
        ctx = {"status": "success"}
    else:
        ctx = {"status": "not found"}

    return HttpResponse(json.dumps(ctx),
                        content_type='application/json; charset=utf-8')

@restrict_to_staff()
@requires("update outreach email address")
def api_update_nuo_inbox(request):
    if not request.method == "POST":
        raise Http404("This view is only accessible via POST method, not %s" %
                      request.method)

    inbox = OutreachEmailAddress.objects.filter(pk=request.POST.get('id'))
    if inbox:
        inbox.update(email=request.POST.get('email'))
        ctx = {"status": "success"}
    else:
        ctx = {"status": "not found"}

    return HttpResponse(json.dumps(ctx),
                        content_type='application/json; charset=utf-8')


@restrict_to_staff()
@requires("read outreach record")
def api_get_nuo_records_list(request):
    """
    GET /prm/api/nonuseroutreach/records/list

    Retrieves all non user outreach records for a company. Returns json object
    with all relevant information for each.

    """
    company = get_company_or_404(request)
    outreach_emails = OutreachEmailAddress.objects.filter(company=company)
    records = OutreachRecord.objects.filter(outreach_email__in=outreach_emails)
    json_res = [{
        'dateAdded': record.date_added.strftime('%m-%d-%Y'),
        'outreachEmail': record.outreach_email.email + '@my.jobs',
        'fromEmail': record.from_email,
        'currentWorkflowState': record.current_workflow_state.state,
        'id': record.id,
    } for record in records]

    return HttpResponse(json.dumps(json_res), mimetype='application/json')

@restrict_to_staff()
@requires("read outreach record")
def api_get_individual_nuo_record(request, record_id=None):
    """
    GET /prm/api/nonuseroutreach/records/record

    Retrieves the information for a given outreach record.

    """
    company = get_company_or_404(request)
    if not record_id:
        raise Http404("No record id provided")
    outreach_emails = OutreachEmailAddress.objects.filter(company=company)
    try:
        record = OutreachRecord.objects.get(outreach_email__in=outreach_emails,
                                            pk=record_id)
        json_obj = {
            "date_added": record.date_added.strftime('%m-%d-%Y'),
            "outreach_email": record.outreach_email.email + '@my.jobs',
            "from_email": record.from_email,
            "subject": record.subject,
            "email_body": record.email_body,
            "current_workflow_state": record.current_workflow_state.state,
        }
    except OutreachRecord.DoesNotExist:
        json_obj = {}

    return HttpResponse(json.dumps(json_obj), mimetype='application/json')


def build_contact_forms(company, form_data):
    if form_data is None:
        contact_data = None
        location_data = None
    else:
        contact_data = {}
        location_data = dict(form_data)
        for field in NuoContactForm.Meta.fields:
            if field in location_data:
                contact_data[field] = location_data.pop(field)
    return {
        'contact': NuoContactForm(contact_data, company=company),
        'location': NuoLocationForm(location_data),
    }


def merge_contact_forms(contact_forms):
    contact_remote_form = RemoteForm(contact_forms['contact']).as_dict()
    location_remote_form = RemoteForm(contact_forms['location']).as_dict()

    combined_order = []
    combined_order.extend(contact_remote_form['ordered_fields'])
    combined_order.extend(location_remote_form['ordered_fields'])
    combined_order.remove('notes')
    combined_order.append('notes')
    combined_fields = contact_remote_form['fields'].copy()
    combined_fields.update(location_remote_form['fields'])
    combined_data = contact_remote_form['data'].copy()
    combined_data.update(location_remote_form['data'])
    combined_errors = contact_remote_form['errors'].copy()
    combined_errors.update(location_remote_form['errors'])
    return {
        'fields': combined_fields,
        'ordered_fields': combined_order,
        'data': combined_data,
        'errors': combined_errors,
    }


@restrict_to_staff()
@requires("convert outreach record")
def api_get_nuo_forms(request):
    company = get_company_or_404(request)
    forms = {
        'partner': NuoPartnerForm(company=company),
        'communication_record': NuoCommunicationRecordForm(company=company),
        'outreach_record': NuoOutreachRecordForm(),
    }

    payload = {
        k: RemoteForm(f).as_dict()
        for (k, f) in forms.iteritems()
    }

    contact_forms = build_contact_forms(company, None)
    contact_payload = merge_contact_forms(contact_forms)
    payload['contact'] = contact_payload

    return HttpResponse(json.dumps(payload), mimetype='application/json')


@csrf_exempt
@restrict_to_staff()
@requires("convert outreach record")
def api_convert_outreach_record(request):
    """
    POST /prm/api/nonuseroutreach/records/convert

    convert data object into contactrecord, create partner, contact where
    necessary.

    Example data object (JSON):
    This example represents a data set with a NEW partner and contact. If
    either was selected from an existing record, only the PK field of that
    object would be populated, ex. {... contact:{pk:"12"} ...}

    {
        "outreachrecord": {
            "pk": "101",
            "current_workflow_state": "33"
        },
        "partner": {
            "pk": "",
            "name": "James B",
            "data_source": "email",
            "uri": "http://www.example.com",
            "tags": [
                "12",
                "68"
            ]
        },
        "contacts": [
            {
                "pk": "",
                "name": "Nicole J",
                "email": "nicolej@test.com",
                "phone": "7651234123",
                "location": {
                    "pk": "",
                    "address_line_one": "",
                    "address_line_two": "",
                    "city": "Newtoneous",
                    "state": "AZ",
                    "country_code": "1",
                    "label": "new place"
                },
                "tags": [
                    "54",
                    "12",
                    "newone"
                ],
                "notes": "long note left here"
            },
            {
                "pk": "",
                "name": "Markus Johnson",
                "email": "markiej@test.com",
                "phone": "1231231234",
                "location": {
                    "pk": "",
                    "address_line_one": "boopie",
                    "address_line_two": "",
                    "city": "Blampitity",
                    "state": "NY",
                    "country_code": "1",
                    "label": "newish place"
                },
                "tags": [
                    "54",
                    "12",
                    "newone"
                ],
                "notes": "another long note left here"
            }
        ],
        "contactrecord": {
            "contact_type": "phone",
            "location": "dining hall",
            "length": "10:30",
            "subject": "new job",
            "date_time": "2016-01-01 05:10",
            "notes": "dude was chill",
            "job_id": "10",
            "job_applications": "20",
            "job_interviews": "10",
            "job_hires": "0",
            "tags": [
                "10",
                "15",
                "3"
            ]
        }
    }

    :return: status code 200 on success, 400, 405 indicates error

    """
    def add_tags_to_object(object_to_tag, tags_list):
        """
        save any new tags and add them to the provided object

        :param object_to_tag: object which should have tags added to it
        :param tags_list: list of tags
        :return:
        """
        for tag in tags_list:
            tag.save()
        object_to_tag.tags.add(*list(tags_list))

    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    user_company = get_company_or_404(request)
    data_object = request.POST.get('request', '{}')
    validate_only = request.GET.get('validate_only', 0)

    if not data_object or data_object == '{}':
        validator = FormsApiValidator({})
        validator.note_api_error('data object not provided')
        return validator.build_error_response()

    if 'data' not in data_object:
        validator = FormsApiValidator({})
        validator.note_api_error('data key missing')
        return validator.build_error_response()

    try:
        data_object = json.loads(data_object)
    except (TypeError, ValueError):
        validator = FormsApiValidator({})
        validator.note_api_error('data object not formatted for JSON')
        return validator.build_error_response()

    validator = FormsApiValidator(data_object)
#    valid_keys = {'outreachrecord', 'contactrecord', 'contacts'}

    # verify that data object has correct keys, no additional keys and
    # that the value is a dict
#    extra_keys = validator.forms() - valid_keys
#    missing_keys = valid_keys - validator.forms()

#    if extra_keys:
#        for key in extra_keys:
#            validator.note_api_error('%s is an invalid key' % key)

#    if missing_keys:
#        validator.note_api_error(
#            'object missing keys %s' % ', '.join(missing_keys))

    # if there are any errors at this point, end processing
    if validator.has_errors():
        return validator.build_error_response()

    # pull outreach record, validate it belongs to member's company
    outreach_data = data_object['data']['outreach_record']
    outreach_form = NuoOutreachRecordForm(outreach_data)
    outreach_pk = outreach_data.pop('pk', None)
#    outreach_validator = validator.isolate_validator('outreachrecord')
#    outreach_data = outreach_validator.get_values()
#    outreach_pk = outreach_data.get('pk', None)
#    workflow_pk = outreach_data.get('current_workflow_state', None)
#    try:
#        outreach_record = OutreachRecord.objects.get(
#            pk=outreach_pk, outreach_email__company=user_company
#        )
#    except OutreachRecord.DoesNotExist:
#        validator.note_api_error("invalid outreach record pk")

#    try:
#        workflow_status = OutreachWorkflowState.objects.get(pk=workflow_pk)
#    except OutreachWorkflowState.DoesNotExist:
#        validator.note_api_error("invalid outreach workflow pk")

    contacts_data = data_object['data']['contacts']
    contact_results = []
    for contact_data in contacts_data:
        contact_pk = contact_data.pop('pk', None)
        create_contact = request.user.can(user_company, "create contact")
        if contact_pk:
            contact = Contact.objects.get(
                pk=contact_pk,
                partner__owner=user_company)
            contact_results.append(contact)
        else:
            if create_contact:
                contact_forms = build_contact_forms(
                    user_company, contact_data)
                contact_results.append(contact_forms)
            else:
                # XXX: do these with the form.
                validator.note_api_error(
                    "User does not have permission to create a contact.")

    partner_form = None
    partner = None
    partner_data = data_object['data']['partner']
    partner_pk = partner_data.pop('pk', None)
    create_partner = request.user.can(user_company, "create partner")
    if partner_pk:
        partner = Partner.objects.get(pk=partner_pk, owner=user_company)
    else:
        if create_partner:
            partner_data['owner'] = user_company
            partner_form = NuoPartnerForm(partner_data, company=user_company)
        else:
            validator.note_api_error(
                "User does not have permission to create a partner.")

    communication_record_form = None
    communication_record = None
    if 'communication_record' in data_object['data']:
        communication_record_data = data_object['data']['communication_record']
        communication_record_pk = communication_record_data.pop('pk', None)
        create_communication_record = request.user.can(
            user_company, u'create communication record')
        if communication_record_pk:
            communication_record = ContactRecord.get(
                pk=communication_record_pk, partner__owner=user_company)
        else:
            if create_communication_record:
                communication_record_form = NuoCommunicationRecordForm(
                    communication_record_data, company=user_company)
            else:
                validator.note_api_error(
                    "User does not have permission to create a " +
                    "communication record.")

    # Run is_valid on all the forms.
    def all_forms_iter():
        yield outreach_form
        yield partner_form
        for result in contact_results:
            if isinstance(result, Contact):
                continue
            yield result['contact']
            yield result['location']
        yield communication_record_form

    all_forms = list(all_forms_iter())
    has_errors = False
    status = 200
    all_validity = [f.is_valid() for f in all_forms if f is not None]
    if any(not v for v in all_validity):
        has_errors = True
        status = 400

    payload = {
        'forms': {
            'contacts': [],
        },
    }
    if partner_form:
        partner_form_payload = RemoteForm(partner_form).as_dict()
        del partner_form_payload['data']['owner']
        payload['forms']['partner'] = partner_form_payload
    elif partner:
        payload['forms']['partner'] = {
            'data': {'pk': partner.pk, 'name': partner.name},
        }

    for result in contact_results:
        if isinstance(result, Contact):
            payload['forms']['contacts'].append({
                'data': {'pk': contact.pk, 'name': contact.name}
            })
        else:
            contact_form_payload = merge_contact_forms(result)
            payload['forms']['contacts'].append(contact_form_payload)

    if communication_record_form:
        communication_record_form_payload = RemoteForm(
            communication_record_form).as_dict()
        payload['forms']['communication_record'] = (
            communication_record_form_payload)
    elif communication_record:
        payload['forms']['communication_record'] = {
            'data': {
                'pk': communication_record.pk,
                'name': communication_record.name,
            },
        }

    outreach_form_payload = RemoteForm(outreach_form).as_dict()
    payload['forms']['outreach_record'] = outreach_form_payload
    payload['forms']['outreach_record']['data']['pk'] = outreach_pk

    if has_errors or validate_only:
        return HttpResponse(
            json.dumps(payload), status=status, mimetype='application/json')

    partner.save()
    outreach_record.partners.add(partner)
    add_tags_to_object(partner, partner_tags)

    for contact in contacts:
        contact['contact'].partner = partner
        if contact['contact'].notes:
            contact['contact'].notes = '%s\n%s' % (contact['contact'].notes,
                                                   contact['notes'])
        else:
            contact['contact'].notes = contact['notes']
        contact['contact'].save()
        outreach_record.contacts.add(contact['contact'])
        if contact.get('location', None):
            contact['location'].save()
            contact['contact'].locations.add(contact['location'])
        add_tags_to_object(contact['contact'], contact['tags'])

        contact_record.partner = partner
        contact_record.contact = contact['contact']
        contact_record.save()
        outreach_record.communication_records.add(contact_record)
        add_tags_to_object(contact_record, contact_record_tags)

    outreach_record.current_workflow_state = workflow_status
    outreach_record.save()

    return HttpResponse('"success"')


@requires('read tag')
def tag_names(request):
    if request.method == 'GET':
        company = get_company_or_404(request)
        value = request.GET.get('value', "")
        names = list(Tag.objects.filter(
            company=company, name__icontains=value).values_list(
                'name', flat=True))
        names = sorted(
            names, key=lambda x: x if not x.startswith(value) else "-" + x)
        return HttpResponse(json.dumps(names))


@requires('read tag')
def tag_color(request):
    if request.method == 'GET':
        company = get_company_or_404(request)
        name = request.GET.get('name')
        colors = list(Tag.objects.filter(
            company=company, name=name).values_list('hex_color', flat=True))
        return HttpResponse(json.dumps(colors))


@requires('create tag')
def add_tags(request):
    company = get_company_or_404(request)
    data = request.GET.get('data', '').split(',')
    tag_get_or_create(company.id, data)
    return HttpResponse(json.dumps('success'))


@require_http_methods(['GET', 'POST'])
@requires('read partner')
def api_get_partners(request):
    """
    GET /prm/api/partner/
    POST /prm/api/partner/

    Returns a list of partners. If a parameter named "q" is provided,
    we filter for partners whose name contain that value. The partners
    whose name start with that value, if any exist, are moved to the
    beginning of the returned list.
    """
    company = get_company_or_404(request)

    q = request.GET.get('q') or request.POST.get('q')
    if q:
        partners = list(company.partner_set.filter(name__icontains=q).annotate(Count('contact')))
        sorted_partners = filter(
            lambda partner: partner.name.lower().startswith(q.lower()),
            partners)
        sorted_partners.extend(set(partners).difference(
            sorted_partners))
    else:
        sorted_partners = company.partner_set.all().annotate(Count('contact'))
    return HttpResponse(json.dumps([{'id': partner.pk,
                                     'name': partner.name,
                                     'contact_count': partner.contact__count}
                                    for partner in sorted_partners]))


@require_http_methods(['GET'])
@requires('read partner')
def api_get_partner(request, partner_id):
    """
    GET /prm/api/partner/1/

    Returns the partner with an ID of 1. Results in a 404 if that partner
    doesn't exist or is owned by a different company.
    """
    company = get_company_or_404(request)

    partner = get_object_or_404(company.partner_set, pk=partner_id)
    return HttpResponse(json.dumps({'id': partner.pk, 'name': partner.name}))


@require_http_methods(['POST'])
@requires('create partner')  # Possible dependency on "create tag" - see below
def api_create_partner(request):
    """
    POST /prm/api/partner/create/

    Creates and returns a partner based on the provided POST data. Adds/creates
    tags as appropriate.
    """
    company = get_company_or_404(request)
    names = request.POST.getlist('tags')
    tags = []
    if names:
        tags = list(company.tag_set.filter(name__in=names))
        existing_tags = [tag.name for tag in tags]
        new_tags = set(names).difference(existing_tags)
        if new_tags:
            if request.user.can(company, 'create tag'):
                for new_tag in set(names).difference(existing_tags):
                    tags.append(company.tag_set.create(name=new_tag,
                                created_by=request.user))
            else:
                return MissingActivity('mypartners.views.api_create_partner: '
                                       'user does not have "create tag" '
                                       'permissions')

    partner = Partner.objects.create(
        name=request.POST['name'],
        uri=request.POST.get('uri', ''),
        data_source=request.POST.get('data_source', ''),
        owner=company
    )

    if tags:
        partner.tags = tags
    return HttpResponse(json.dumps({'id': partner.pk, 'name': partner.name}))


@require_http_methods(['GET', 'POST'])
@requires('read contact')
def api_get_contacts(request):
    """
    GET /prm/api/contact/
    POST /prm/api/contact/

    Returns a list of contacts. If a parameter named "q" is provided,
    we filter for contacts whose name contain that value. If a parameter named
    "partner_id" is provided, we only search that partner's contacts. The
    contacts whose name start with "q", if any exist, are moved to the
    beginning of the returned list.
    """
    company = get_company_or_404(request)

    q = request.GET.get('q') or request.POST.get('q')
    partner_id = (request.GET.get('partner_id')
                  or request.POST.get('partner_id'))
    if partner_id:
        contact_args = {'partner__id': partner_id}
    else:
        contact_args = {'partner__owner': company}

    contacts = (
        Contact.objects.filter(**contact_args).prefetch_related('partner'))
    if q:
        q_obj = Q(email__icontains=q) | Q(name__icontains=q)
        contacts = list(contacts.filter(q_obj))
        sorted_contacts = filter(
            lambda contact: (contact.name.lower().startswith(q.lower())
                             or contact.email.lower().startswith(q.lower())),
            contacts)
        sorted_contacts.extend(set(contacts).difference(sorted_contacts))
    else:
        sorted_contacts = contacts
    return HttpResponse(json.dumps([
        {
            'id': contact.pk,
            'name': contact.name,
            'email': contact.email,
            'partner': {
                'pk': contact.partner.pk,
                'name': contact.partner.name,
            },
        } for contact in sorted_contacts]))


@require_http_methods(['GET'])
@requires('read contact')
def api_get_contact(request, contact_id):
    """
    GET /prm/api/contact/1/

    Returns the contact with an ID of 1. Results in a 404 if that contact
    doesn't exist or is owned by a different company.
    """
    company = get_company_or_404(request)
    contact = get_object_or_404(Contact, pk=contact_id, partner__owner=company)
    return HttpResponse(json.dumps({'id': contact.pk,
                                    'name': contact.name,
                                    'email': contact.email}))


@require_http_methods(['POST'])
@requires('create contact')
def api_create_contact(request):
    """
    POST /prm/api/contact/create/

    Creates and returns a contact based on the provided POST data.
    """
    company = get_company_or_404(request)
    partner = get_object_or_404(company.partner_set,
                                pk=request.POST['partner_id'])
    contact = Contact.objects.create(
        name=request.POST['name'],
        email=request.POST.get('email', ''),
        phone=request.POST.get('phone', ''),
        notes=request.POST.get('notes', ''),
        partner=partner
    )
    location = Location.objects.create(
        **{key: request.POST.get('key', '')
           for key in ['address_line_one', 'address_line_two', 'city', 'state',
                       'postal_code', 'label']}
    )
    contact.locations.add(location)

    return HttpResponse(json.dumps({'id': contact.pk,
                                    'name': contact.name,
                                    'email': contact.email}))


@require_http_methods(['GET', 'POST'])
def api_get_workflow_states(request):
    return HttpResponse(json.dumps(
        [{'id': ows.pk, 'name': ows.state}
         for ows in OutreachWorkflowState.objects.all()]))
