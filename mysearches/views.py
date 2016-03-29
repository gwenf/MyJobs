import json, datetime, urlparse, urllib
from datetime import date, timedelta

from django.conf import settings
from django.contrib.auth.decorators import user_passes_test
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError
from django.http import (HttpResponseRedirect, HttpResponse, Http404,
                         HttpResponseNotAllowed)
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.views.decorators.csrf import (
    csrf_exempt as django_csrf_exempt)

from urllib2 import HTTPError

from myjobs.decorators import user_is_allowed
from myjobs.models import User
from myjobs.autoserialize import autoserialize
from myjobs.cross_site_verify import cross_site_verify
from mysearches.models import (SavedSearch, SavedSearchDigest,
                               PartnerSavedSearch)
from mysearches.forms import (SavedSearchForm, DigestForm,
                              PartnerSubSavedSearchForm)
from mysearches.helpers import (get_interval_from_frequency, parse_feed,
                                url_sort_options, validate_dotjobs_url)
from universal.decorators import warn_when_inactive, restrict_to_staff


@user_is_allowed(SavedSearch, 'id', pass_user=True)
def delete_saved_search(request, user=None):
    search_id = request.REQUEST.get('id')
    user = user or request.user
    try:
        search_id = int(search_id)

        # a single search is being deleted
        search = get_object_or_404(SavedSearch, id=search_id,
                                   user=user)
        search_name = search.label
        search.delete()
    except ValueError:
        # all searches are being deleted
        SavedSearch.objects.filter(user=user, partnersavedsearch__isnull=True).delete()
        search_name = 'all'

    return HttpResponseRedirect(
        reverse('saved_search_main_query') + '?d=' + str(search_name))


@user_is_allowed()
@user_passes_test(User.objects.not_disabled)
@warn_when_inactive(feature="Saved Searches are")
def saved_search_main(request):
    # instantiate the form if the digest object exists
    try:
        digest_obj = SavedSearchDigest.objects.get(user=request.user)
    except (SavedSearchDigest.DoesNotExist,
            SavedSearchDigest.MultipleObjectsReturned):
        digest_obj = None
    updated = request.REQUEST.get('d')
    saved_searches = SavedSearch.objects.filter(
        user=request.user, partnersavedsearch__isnull=True)
    partner_saved_searches = PartnerSavedSearch.objects.filter(
        user=request.user)

    if request.user.is_verified:
        form = DigestForm(user=request.user, instance=digest_obj)
        add_form = SavedSearchForm(user=request.user)
    else:
        form = None
        add_form = None
    return render_to_response('mysearches/saved_search_main.html',
                              {'saved_searches': saved_searches,
                               'partner_saved_searches': partner_saved_searches,
                               'form': form,
                               'add_form': add_form,
                               'updated': updated,
                               'view_name': 'Saved Searches'},
                              RequestContext(request))


@user_is_allowed()
@user_passes_test(User.objects.is_verified)
@user_passes_test(User.objects.not_disabled)
@warn_when_inactive(feature="Saved Searches are")
def view_full_feed(request):
    search_id = request.REQUEST.get('id')
    saved_search = SavedSearch.objects.get(id=search_id)
    if hasattr(saved_search, 'partnersavedsearch'):
        is_pss = True
    else:
        is_pss = False
    if request.user == saved_search.user:
        url_of_feed = url_sort_options(saved_search.feed,
                                       saved_search.sort_by,
                                       frequency=saved_search.frequency)
        try:
            items, count = parse_feed(url_of_feed, saved_search.frequency,
                                      saved_search.jobs_per_email)
        except HTTPError:
            items = None
            count = 0
        start_date = date.today() + timedelta(get_interval_from_frequency(
            saved_search.frequency))
        return render_to_response('mysearches/view_full_feed.html',
                                  {'search': saved_search,
                                   'items': items,
                                   'view_name': 'Saved Searches',
                                   'is_pss': is_pss,
                                   'start_date': start_date,
                                   'count': count},
                                  RequestContext(request))
    else:
        return HttpResponseRedirect(reverse('saved_search_main'))


@user_passes_test(User.objects.is_verified)
@user_passes_test(User.objects.not_disabled)
def more_feed_results(request):
    # Ajax request comes from the view_full_feed view when user scrolls to
    # bottom of the page
    if request.is_ajax():
        url_of_feed = url_sort_options(request.GET['feed'],
                                       request.GET['sort_by'],
                                       frequency=request.GET['frequency'])
        items = parse_feed(url_of_feed, request.GET['frequency'],
                           offset=request.GET['offset'])[0]
        return render_to_response('mysearches/feed_page.html',
                                  {'items': items}, RequestContext(request))


@user_passes_test(User.objects.not_disabled)
def validate_url(request):
    if request.is_ajax():
        feed_title, rss_url = validate_dotjobs_url(request.POST['url'],
                                                   request.user)
        if rss_url:
            # returns the RSS url via AJAX to show if field is validated
            # id valid, the label field is auto populated with the feed_title
            data = {'rss_url': rss_url,
                    'feed_title': feed_title,
                    'url_status': 'valid'}

        else:
            data = {'url_status': 'not valid'}
        return HttpResponse(json.dumps(data))


@user_passes_test(User.objects.is_verified)
@user_passes_test(User.objects.not_disabled)
def save_digest_form(request):
    if request.method == 'POST':
        try:
            digest_obj = SavedSearchDigest.objects.get(user=request.user)
        except (SavedSearchDigest.DoesNotExist,
                SavedSearchDigest.MultipleObjectsReturned):
            digest_obj = None

        form = DigestForm(user=request.user, data=request.POST,
                          instance=digest_obj)
        if form.is_valid():
            form.save()
            data = ""
        else:
            data = json.dumps(form.errors)

        if request.is_ajax():
            # If this is an ajax request, we can return success/failure
            return HttpResponse(data)

    # The request is not ajax; Redirect to the main saved search page
    return HttpResponseRedirect(reverse('saved_search_main'))


@user_passes_test(User.objects.is_verified)
@user_passes_test(User.objects.not_disabled)
@warn_when_inactive(feature="Saved Searches are")
def save_search_form(request):
    search_id = request.POST.get('search_id')

    try:
        search_id = int(search_id)
        original = SavedSearch.objects.get(id=search_id, user=request.user)
    except (ValueError, TypeError):
        original = None

    if hasattr(original, 'partnersavedsearch'):
        form = PartnerSubSavedSearchForm(data=request.POST,
                                         instance=original.partnersavedsearch,
                                         request=request)
    else:
        form = SavedSearchForm(user=request.user, data=request.POST,
                               instance=original)

    if form.is_valid():
        form.save()

        if request.is_ajax():
            return HttpResponse(status=200)
        else:
            return HttpResponseRedirect(reverse('saved_search_main'))
    else:
        if request.is_ajax():
            return HttpResponse(json.dumps(form.errors))
        else:
            return render_to_response('mysearches/saved_search_edit.html',
                                      {'form': form,
                                       'search_id': search_id},
                                      RequestContext(request))


@user_passes_test(User.objects.is_verified)
@user_passes_test(User.objects.not_disabled)
@warn_when_inactive(feature="Saved Searches are")
def edit_search(request):
    search_id = request.REQUEST.get('id')
    partner_saved_search = request.REQUEST.get('pss')
    if not partner_saved_search:
        if search_id:
            saved_search = get_object_or_404(SavedSearch, id=search_id,
                                             user=request.user)
            if hasattr(saved_search, 'partnersavedsearch'):
                raise Http404("mysearches.views.edit_search: trying to edit a "
                              "PartnerSavedSearch as a SavedSearch")
        else:
            saved_search = None

        is_pss = False
        form = SavedSearchForm(user=request.user, instance=saved_search,
                               auto_id='id_edit_%s')
    else:
        if search_id:
            saved_search = get_object_or_404(SavedSearch, id=search_id,
                                             user=request.user)
            if hasattr(saved_search, 'partnersavedsearch'):
                is_pss = True
                form = PartnerSubSavedSearchForm(
                    instance=saved_search.partnersavedsearch,
                    auto_id=False,
                    request=request)
        else:
            raise Http404("mysearches.views.edit_search: no id provided")

    return render_to_response('mysearches/saved_search_edit.html',
                              {'form': form,
                               'search_id': search_id,
                               'view_name': 'Saved Searches',
                               'search': saved_search,
                               'is_pss': is_pss,
                               'label': form.instance.label},
                              RequestContext(request))


@user_passes_test(User.objects.is_verified)
@user_passes_test(User.objects.not_disabled)
def save_edit_form(request):
    if request.is_ajax():
        search_id = request.POST.get('search_id')
        saved_search = SavedSearch.objects.get(id=search_id)
        if request.user == saved_search.user:
            form = SavedSearchForm(user=request.user, data=request.POST,
                                   instance=saved_search)
            if form.is_valid():
                form.save()
                return HttpResponse('success')
            else:
                return HttpResponse(json.dumps(form.errors))


@user_is_allowed(SavedSearch, 'id')
def unsubscribe_confirmation(request):
    unsub_links = {
        "all_searches": reverse('unsubscribe') + "?id=digest",
        "all_email": reverse('unsubscribe_all') + "?id=all"
    }
    search_id = request.REQUEST.get('id')
    if search_id is not None and search_id.isdigit():
        unsub_links['single_search'] = reverse(
            'unsubscribe') + "?id={}".format(search_id)
    return render_to_response(
        'mysearches/saved_search_unsubscribe_confirmation.html',
        {'links': unsub_links}, RequestContext(request))


@user_is_allowed(SavedSearch, 'id', pass_user=True)
def unsubscribe(request, user=None):
    """
    Deactivates a user's saved searches.

    Inputs:
    :request: HttpRequest object
    :search_id: the string 'digest' to disable all searches
        or the id value of a specific search to be disabled
    """
    search_id = request.REQUEST.get('id')
    user = user or request.user
    has_pss = None
    try:
        search_id = int(search_id)
        saved_search = get_object_or_404(SavedSearch, id=search_id,
                                         user=user)

        # saved_search is a single search rather than a queryset this time
        cache = [saved_search]
        if saved_search.is_active:
            saved_search.is_active = False
            has_pss = hasattr(saved_search, 'partnersavedsearch')
            if has_pss:
                saved_search.partnersavedsearch.unsubscribed = True
                saved_search.partnersavedsearch.save()
                # method expects an iterable and I didn't want to run
                # another query
                user.send_opt_out_notifications(
                    [saved_search.partnersavedsearch])
            saved_search.save()

    except ValueError:
        digest = SavedSearchDigest.objects.get_or_create(
            user=user)[0]
        if digest.is_active:
            digest.is_active = False
            digest.save()
        saved_searches = SavedSearch.objects.filter(user=user,
                                                    is_active=True)

        # we want the associated partner saved searches themselves
        user.send_opt_out_notifications([
            search.partnersavedsearch for search in saved_searches.filter(
                partnersavedsearch__isnull=False)])

        # saved_searches that have partner saved searches
        ss_have_pss = saved_searches.filter(partnersavedsearch__isnull=False)
        # Bulk update (django 1.6) can't dig through a Foreign Key have to
        # iterate with a for loop
        for ss in ss_have_pss:
            ss.partnersavedsearch.unsubscribed = True
            ss.partnersavedsearch.save()

        # Updating the field that a queryset was filtered on seems to empty
        # that queryset; Make a copy and then update the queryset
        cache = list(saved_searches)
        saved_searches.update(is_active=False)
    except TypeError:
        raise Http404("mysearches.views.unsubscribe: no id provided")

    return render_to_response('mysearches/saved_search_disable.html',
                              {'search_id': search_id,
                               'searches': cache,
                               'email_user': user,
                               'contains_pss': has_pss},
                              RequestContext(request))


def saved_search_widget(request):
    saved_search_url = request.REQUEST.get('url')
    callback = request.REQUEST.get('callback')
    success_email = request.REQUEST.get('success')
    search = None
    user = request.user if request.user.is_authenticated() else None

    if user:
        try:
            search = SavedSearch.objects.filter(user=user,
                                                url=saved_search_url)[0]
        except IndexError:
            pass

    if success_email and not search:
        try:
            search = SavedSearch.objects.filter(user__email=success_email,
                                                url=saved_search_url)[0]
        except IndexError:
            pass

    ctx = {
        'user': user,
        'search': search,
        'success': success_email,
        'is_pss': hasattr(search, 'partnersavedsearch'),
    }
    html = render_to_response('mysearches/saved_search_widget.html', ctx,
                              RequestContext(request))

    return HttpResponse("%s(%s)" % (callback, json.dumps(html.content)),
                        content_type='text/javascript')


@user_passes_test(lambda u: u.is_superuser)
def send_saved_search(request):
    if settings.DEBUG:
        search_id = request.GET.get('id')
        search = SavedSearch.objects.get(pk=search_id)
        search.send_email(additional_headers=('"filters":{"clicktrack":{'
                                              '"settings":{"enable":0}}}'))
        if request.GET.get('is_pss'):
            search = search.partnersavedsearch
            redirect_to = reverse('partner_view_full_feed') + \
                '?partner={partner_id}&id={search_id}'.format(
                    partner_id=search.partner.pk,
                    search_id=search.pk
                )
        else:
            redirect_to = reverse('view_full_feed') + '?id={search_id}'.format(
                search_id=search_id)
        return HttpResponseRedirect(redirect_to)
    else:
        raise Http404("mysearches.views.send_saved_search: "
                      "feature not available outside of QC")


def user_creation_retrieval(auth_user, email):
    """
    Retrieve user account for adding saved searches. If the email belongs
    to a user and that user is not logged in, error is raised.

    :param auth_user: Currently logged in user
    :param email: Email attempting to be added
    :return: New or existing user account tied to provided email
    """
    if not auth_user:
        raise ValueError('No user provided. This field is required')

    if not email:
        raise ValueError('No email provided. This field is required')

    # retrieve the user account is created, otherwise, create it
    email_user_account, created = User.objects.create_user(email=email,
                                                           send_email=True)

    if not created and email_user_account != auth_user:
        raise ValueError('This email has already been taken. If this is your'
                         ' email, please log in to add this search')
        # TODO: ADD LINK

    return email_user_account, created


def add_or_activate_saved_search(user, url):
    """
    Attempt to add a new saved search to a user, or it is already exists,
    make sure it is active.

    :param user: User recieving search
    :param url: URL for search
    :return: The new or activated search
    """
    if not url:
        raise ValueError("No URL provided")

    url = urllib.unquote(url)

    label, feed = validate_dotjobs_url(url, user)
    if not (label and feed):
        raise ValueError("Invalid .JOBS URL Provided")

    # Create notes field noting that it was created as current date/time
    now = datetime.datetime.now().strftime('%A, %B %d, %Y %l:%M %p')
    notes = 'Saved on ' + now
    if url.find('//') == -1:
        url = 'http://' + url
    netloc = urlparse.urlparse(url).netloc
    notes += ' from ' + netloc

    search_args = {'url': url,
                   'label': label,
                   'feed': feed,
                   'user': user,
                   'email': user.email,
                   'frequency': 'D',
                   'day_of_week': None,
                   'day_of_month': None,
                   'notes': notes}

    try:
        # if search already exists, activate it
        saved_search = SavedSearch.objects.get(user=search_args['user'],
                                email__iexact=search_args['email'],
                                url=search_args['url'])
        saved_search.is_active = True
        saved_search.save()
    except SavedSearch.DoesNotExist:
        # if there's no search for that email/user, create it
        saved_search = SavedSearch(**search_args)
        saved_search.save()
        saved_search.initial_email()

    return saved_search


def get_value_from_request(request, key):
    """
    Checks GET, POST and body for key, returns whatever is found or none

    :param request: request with get, post, or body
    :param key: key being searched for
    :return: value for key or none
    """
    request_body = {}
    try:
        # if request.body exists and is a json object, load it
        request_body = json.loads(request.body)
    except ValueError:
        pass

    value = (request.GET.get(key) or
             request.POST.get(key) or
             request_body.get(key))
    return value

def remove_anchor_from_url(url):
    """
    Remove anchor tags from the provided URL. %23 is '#' url encoded.

    """
    if url.find('%23') != -1:
        return url[:url.index('%23')]
    return url

@django_csrf_exempt
@cross_site_verify
@autoserialize
def secure_saved_search(request):
    """
    Handling for creation of a saved search via the saved search secure block
    widget.

    :param request: inbound request
    :return: Dictionary, to be converted by autoserialize decorator
    """
    allowed_methods = ['GET','POST']
    if request.method not in allowed_methods:
        raise HttpResponseNotAllowed(allowed_methods)

    response =  {'error':'', 'user_created': False, 'search_activated':False}
    email_in = get_value_from_request(request, 'email')

    try:
        new_search_account, user_created = user_creation_retrieval(request.user,
                                                                   email_in)
    except ValueError as ex:
        response['error'] = ex.message
        return response
    except ValidationError:
        response['error'] = "Invalid email."
        return response

    response['user_created'] = user_created

    url = remove_anchor_from_url(get_value_from_request(request, 'url'))

    try:
        saved_search = add_or_activate_saved_search(new_search_account, url)
    except ValueError as ex:
        response['error'] = ex.message
        return response

    if saved_search:
        response['search_activated'] = True

    return response
