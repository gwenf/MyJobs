from datetime import date, timedelta, datetime
from itertools import chain, izip_longest
import json
import logging
import newrelic.agent
import os
import sys
import traceback
from urllib2 import HTTPError, URLError

from celery import group
from celery.task import task
from pysolr import Solr

from django.conf import settings
from secrets import options, housekeeping_auth
from django.contrib.sitemaps import ping_google
from django.core.urlresolvers import reverse_lazy
from django.template.loader import render_to_string
from django.db.models import Q

from seo.models import SeoSite, BusinessUnit
from myjobs.models import EmailLog, User, STOP_SENDING, BAD_EMAIL
from jira import JIRA
from myjobs.helpers import log_to_jira
from mymessages.models import Message
from mysearches.models import (SavedSearch, SavedSearchDigest, SavedSearchLog,
                               DOM_CHOICES, DOW_CHOICES)
from mypartners.models import PartnerLibrary, PartnerLibrarySource
from mypartners.helpers import get_library_partners
import import_jobs
from import_jobs.models import ImportRecord
from import_jobs.mongo import jobsfs_to_mongo, seoxml_to_mongo
from postajob.models import Job
from registration.models import ActivationProfile
from djcelery.models import TaskState
import ast
from django.core.mail import send_mail


logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = "/de/data/"
sys.path.insert(0, os.path.join(BASE_DIR))
sys.path.insert(0, os.path.join(BASE_DIR, '../'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
FEED_FILE_PREFIX = "dseo_feed_"


@task(name='tasks.create_jira_ticket')
def create_jira_ticket(summary, description, **kwargs):
    """
    Create a new jira ticket, returning the associated number.

    Examples:

        Synchronously create a jira ticket::

            create_jira_ticket("Test Ticket", "This is a test")

        Asynchronously create a jira ticket::

            create_jira_ticket.delay("Test Ticket", "This is a test")

    Inputs:

    .. note:: watchers and watcher_group are mutually exclusive.

        :summary: The ticket summary
        :description: The ticket description
        :assignee: Who the ticket should be assigned to. Defaults to "-1" which
                   is analogous to selecting "automatic" on the JIRA web form.
        :reporter: Who created the ticket (or is responsible for QCing it).
                   Defaults to "automaticagent".
        :issuetype: The type of issue. Defaults to "Task".
        :project: The project the ticket should be created in. Defaults to
                  "ST", which is Product Support.
        :priority: Ticket Priority. Defaults to "Major".
        :components: A list of components this ticket belongs to.
        :watchers: A list of user names to add as watchers of this ticket.
        :watcher_group: A group to assign as watchesr.

    Output:

    .. note:: The instance isn't returned because we need the ability to pass
              the results to another asynchronous task without blocking, which
              requires that all arguments be serializable.

        The ticket key which corresponds to the created JIRA ticket.
    """
    jira = JIRA(options=options, basic_auth=housekeeping_auth)

    assignee = {'name': kwargs.setdefault('assignee', '-1')}
    reporter = {'name': kwargs.setdefault('reporter', 'automationagent')}
    issuetype = {'name': kwargs.setdefault('issuetype', 'Task')}
    project = {'key': kwargs.setdefault('project', 'ST')}
    priority = {'name': kwargs.setdefault('priority', 'Major')}
    components = [{'name': name}
                  for name in kwargs.setdefault('components', [])]

    watchers = kwargs.setdefault('watchers', set())
    if 'watcher_group' in kwargs:
        watchers = watchers.union(
            jira.group_members(kwargs['watcher_group']).keys())

    if assignee == reporter:
        raise ValueError("Assignee and reporter must be different.")

    fields = {
        'project': project,
        'summary': summary,
        'description': description,
        'issuetype': issuetype,
        'priority': priority,
        'reporter': reporter,
        'assignee': assignee,
        'components': components,
    }

    issue = jira.create_issue(fields=fields)

    for watcher in watchers:
        jira.add_watcher(issue, watcher)

    return issue.key


@task(name='tasks.assign_ticket_to_request')
def assign_ticket_to_request(key, access_request):
    """
    Assign a ticket to a request.

    Examples:
        .. note:: The synchronous variety is for easy of debugging. In real
                  code, you'd probably simply assign the attribute to the
                  access_request instance directly.

        Synchronously:
            assign_ticket_to_request(key, access_request)
        Asynchronously:
            assign_ticket_to_request.delay(key, access_request)

    Input:
        :key: Generally an `AsyncResult` containing a string, which would be
              the JIRA ticket's key.
        :access_request: The `myjobs.models.CompanyAccessRequest` instance to
                         asssign the ticket key to.

    Output:
        The pk of the `myjobs.models.CompanyAccessRequest` instance that the
        ticket key was assigned to.

    """
    access_request.ticket = getattr(key, 'get', lambda: key)()
    access_request.save()

    return access_request.pk


@task(name='tasks.send_search_digest', ignore_result=True,
      default_retry_delay=180, max_retries=2, bind=True)
def send_search_digest(self, search):
    """
    Task used by send_send_search_digests to send individual digest or search
    emails. This can raise three different exceptions depending on various
    factors that may be within or outside of our control. In the event that
    that occurs, we err on the side of momentary network issues and assume that
    this search will send successfully at a later time.

    Inputs:
    :search: SavedSearch or SavedSearchDigest instance to be mailed
    """
    try:
        search.send_email()
    except (ValueError, URLError, HTTPError) as e:
        if self.request.retries < 2:  # retry sending email twice
            raise send_search_digest.retry(arg=[search], exc=e)


PARTNER_LIBRARY_SOURCES = {
    'Employment Referral Resource Directory': {
        'search_url': 'https://ofccp.dol-esa.gov/errd/directory.jsp',
        'download_url': 'https://ofccp.dol-esa.gov/errd/directoryexcel.jsp',
        'params': {
            'reg': 'ALL',
            'stat': 'None',
            'name': '',
            'city': '',
            'sht': 'None',
            'lst': 'None',
            'sortorder': 'asc'
        }
    },
    'Disability and Veterans Community Resources Directory': {
        'search_url': 'https://ofccp.dol-esa.gov/errd/resourcequery.jsp',
        'download_url': 'https://ofccp.dol-esa.gov/errd/resourceexcel.jsp',
        'params': {
            'returnformat': 'html',
            'formname': 'searchfrm',
            'reg': 'ALL',
            'stat': 'None',
            'name': '',
            'city': '',
            'sht': 'None',
            'lst': 'None',
            'sortorder': 'asc'
        }
    }
}


@task(name='tasks.update_partner_library', ignore_result=True,
      default_retry_delay=180, max_retries=2)
def update_partner_library():

    for source in PartnerLibrarySource.objects.all():
        print "Connecting to %s...." % source
        print "Parsing data for PartnerLibrary information..."

        added = skipped = 0
        for partner in get_library_partners(source.search_url,
                                            source.download_url,
                                            json.loads(source.params)):
            # the second join + split take care of extra internal whitespace
            fullname = " ".join(" ".join([partner.first_name,
                                          partner.middle_name,
                                          partner.last_name]).split())
            emails = [email.strip()
                      for email in partner.email_id.split(';', 1)]

            for email in emails:
                # disambiguate records by source, contact name, and address
                if not PartnerLibrary.objects.filter(data_source=source.name,
                                                     contact_name=fullname,
                                                     st=partner.st,
                                                     city=partner.city,
                                                     email=email).exists():
                    PartnerLibrary.objects.create(
                        data_source=source.name,
                        name=partner.organization_name,
                        uri=partner.website,
                        region=partner.region,
                        state=partner.state,
                        area=partner.area,
                        contact_name=fullname,
                        phone=partner.phone,
                        phone_ext=partner.phone_ext,
                        alt_phone=partner.alt_phone,
                        fax=partner.fax,
                        email=email,
                        street1=partner.street1,
                        street2=partner.street2,
                        city=partner.city,
                        st=partner.st,
                        zip_code=partner.zip_code,
                        is_minority=partner.minority,
                        is_female=partner.female,
                        is_disabled=partner.disabled,
                        is_disabled_veteran=partner.disabled_veteran,
                        is_veteran=partner.veteran)
                    added += 1
                else:
                    skipped += 1

        print "%d records added and %d records skipped from '%s.\n" % (
            added, skipped, source)


@task(name='tasks.requeue_missed_searches', ignore_result=True)
def requeue_missed_searches():
    """
    Determine which saved searches should have been sent in the past but have
    not. Send those individually or in digests as appropriate.
    """
    today = date.today()
    day_of_week = str(today.isoweekday())
    day_of_month = today.day

    # We have lists of every day in the week and every day of the month.
    # To exclude searches that will be sent later today, we need to remove
    # today from those lists.
    days_of_week = [choice[0] for choice in DOW_CHOICES]
    days_of_week.remove(day_of_week)
    days_of_month = [choice[0] for choice in DOM_CHOICES]
    days_of_month.remove(day_of_month)

    q = Q()
    # There are 36 distinct last_sent dates we need to check - the six previous
    # days of the week for weekly searches and the last 30 days for monthly
    # searches. We can combine all of these into a single Q.
    for day in days_of_week:
        # Math: today is Monday (1) and the search should have sent on
        # Saturday (6). 1 - 6 = -5. -5 % 7 = 2 days ago. A similar calculation
        # occurs for days of the month.
        # Keep in mind that isoweekday is 1-indexed and starts on Monday. If
        # we weren't already removing today from the list of options, we would
        # be forced to use something other than modulo: 1 - 1 = 0, 0 % 7 = 0,
        # 0 isn't a valid return value for isoweekday.
        days_ago = (today.isoweekday() - int(day)) % 7
        q = q | (Q(frequency='W', day_of_week=day) &
                 (Q(last_sent__lt=today - timedelta(days=days_ago)) |
                  Q(last_sent__isnull=True)))
    for day in days_of_month:
        days_ago = (day_of_month - day) % 31
        # As a happy little side effect of requeuing saved searches, this will
        # resend monthly searches for, for example, the 31st of the month
        # on the first day of the following month if the previous month doesn't
        # have that many days in it.
        q = q | (Q(frequency='M', day_of_month=day) &
                 (Q(last_sent__lt=today - timedelta(days=days_ago)) |
                  Q(last_sent__isnull=True)))

    all_searches = SavedSearch.objects.filter(user__opt_in_myjobs=True,
                                              user__is_disabled=False,
                                              is_active=True)
    all_searches = all_searches.filter(q)

    # Grabbing digests via saved search is the opposite of what we do when
    # sending saved searches normally but this makes joining between tables
    # possible as digests don't have a last_sent attribute.
    digests = all_searches.values_list('user__savedsearchdigest',
                                       flat=True).distinct()
    digests = SavedSearchDigest.objects.filter(pk__in=digests)

    # Accounting for digests greatly increases the complexity of preventing
    # duplicate emails and there are plans to remove them eventually. As such,
    # we are ignoring digests here.
    for digest in digests.filter(is_active=False):
        searches = all_searches.filter(user=digest.user)
        for search in searches:
            send_search_digest.s(search).apply_async()


@task(name='tasks.send_search_digests', ignore_result=True)
def send_search_digests():
    """
    Daily task to send saved searches. If user opted in for a digest, they
    receive it daily and do not get individual saved search emails. Otherwise,
    each active saved search is sent individually.
    """

    def filter_by_time(qs):
        """
        Filters the provided query set for emails that should be sent today

        Inputs:
        :qs: query set to be filtered

        Outputs:
        :qs: filtered query set containing today's outgoing emails
        """
        today = datetime.today()
        day_of_week = today.isoweekday()

        daily = qs.filter(frequency='D')
        weekly = qs.filter(frequency='W', day_of_week=str(day_of_week))
        monthly = qs.filter(frequency='M', day_of_month=today.day)
        return chain(daily, weekly, monthly)

    requeue_missed_searches.apply_async()

    digests = SavedSearchDigest.objects.filter(is_active=True,
                                               user__opt_in_myjobs=True,
                                               user__is_disabled=False)
    digests = filter_by_time(digests)
    for obj in digests:
        send_search_digest.s(obj).apply_async()

    not_digest = SavedSearchDigest.objects.filter(is_active=False,
                                                  user__opt_in_myjobs=True,
                                                  user__is_disabled=False)
    for item in not_digest:
        saved_searches = item.user.savedsearch_set.filter(is_active=True)
        saved_searches = filter_by_time(saved_searches)
        for search_obj in saved_searches:
            send_search_digest.s(search_obj).apply_async()


@task(name='task.delete_inactive_activations', ignore_result=True)
def delete_inactive_activations():
    """
    Daily task checks if activation keys are expired and deletes them.
    Disabled users are exempt from this check.
    """

    for profile in ActivationProfile.objects.all():
        try:
            if profile.activation_key_expired():
                user = profile.user
                if not user.is_disabled and not user.is_verified:
                    user.delete()
                    profile.delete()
        except User.DoesNotExist:
            profile.delete()


@task(name='tasks.process_user_events', ignore_result=True)
def process_user_events(email):
    """
    Processes all email events for a given user.
    """
    user = User.objects.get_email_owner(email=email)

    logs = EmailLog.objects.filter(email=email).order_by('-received')
    newest_log = logs[0]

    filter_by_event = lambda x, num = None: [log for log in logs[:num]
                                           if log.event in x]

    max_errors = 3
    # The presence (and number of events) of deactivate or stop_sending
    # determines what kind (if any) of My.jobs message the user will receive.
    # deactivate takes precedence. The logs query set has already been
    # evaluated, so the only overhead is the list comprehension
    deactivate = filter_by_event(BAD_EMAIL, num=3)
    num_errors = len(deactivate)
    stop_sending = filter_by_event(STOP_SENDING)
    update_fields = []
    if user:
        if (num_errors == max_errors
                or stop_sending) and user.opt_in_myjobs:
            user.opt_in_myjobs = False
            if num_errors == max_errors:
                # Only deactivate the user if the previous "max_deactivations"
                # communications fail, not for one-off failures.
                user.is_verified = False
                user.deactivate_type = deactivate[0].event
                update_fields.append('is_verified')
                body = ('<b>Warning</b>: Attempts to send messages to {email} '
                        'have failed. Please check your email address in your '
                        '<a href="{{settings_url}}">'
                        'account settings</a>.').format(
                            email=deactivate[0].email)
            else:
                user.deactivate_type = stop_sending[0].event
                body = ('<b>Warning</b>: We have received a request to stop '
                        'communications with {email}. If this was in error, '
                        'please opt back into emails in your '
                        '<a href="{{settings_url}}">'
                        'account settings</a>.').format(
                            email=stop_sending[0].email)
            body = body.format(settings_url=reverse_lazy('edit_account'))
            Message.objects.create_message(users=user, subject='', body=body)
            update_fields.extend(['deactivate_type',
                                  'opt_in_myjobs'])

        if user.last_response < newest_log.received:
            user.last_response = newest_log.received
            update_fields.append('last_response')

        # If update_fields is an empty iterable, the save is aborted
        # This doesn't hit the DB unless a field has changed
        user.save(update_fields=update_fields)

    logs.filter(processed=False).update(processed=True)


@task(name='tasks.process_batch_events', ignore_result=True)
def process_batch_events():
    """
    Processes all events that have accumulated over the last day, sends emails
    to inactive users, and disables users who have been inactive for a long
    period of time.
    """
    now = date.today()
    EmailLog.objects.filter(received__lte=now - timedelta(days=60),
                            processed=True).delete()

    emails = set(EmailLog.objects.values_list('email', flat=True).filter(
        processed=False))

    result = group(process_user_events.subtask((email,))
                   for email in emails).apply()
    result.join()

    # These users have not responded in a month. Send them an email if they
    # own any saved searches
    inactive = User.objects.select_related('savedsearch_set')
    inactive = inactive.filter(Q(last_response=now - timedelta(days=172)) |
                               Q(last_response=now - timedelta(days=179)))

    category = '{"category": "User Inactivity (%s)"}'
    for user in inactive:
        if user.savedsearch_set.exists():
            time = (now - user.last_response).days
            message = render_to_string('myjobs/email_inactive.html',
                                       {'user': user,
                                        'time': time})

            site = user.registration_source()
            headers = {'X-SMTPAPI': category}
            user.email_user(message, email_type=settings.INACTIVITY, site=site,
                            headers=headers)

    # These users have not responded in 90 days. Stop sending emails.
    users = User.objects.filter(last_response__lte=now - timedelta(days=180))
    users.update(opt_in_myjobs=False)


def split_list(l, list_len, fill_val=None):
    """
    Splits a list into sublists.

    inputs:
    :l: The list to be split.
    :list_len: The length of the resulting lists.
    :fill_val: The value that is inserted when there are less items in the
        final list than list_len.

    outputs:
    A generator of tuples size list_len.

    """
    args = [iter(l)] * list_len
    return izip_longest(fillvalue=fill_val, *args)


@task(name='tasks.expire_jobs', ignore_result=True)
def expire_jobs():
    jobs = Job.objects.filter(date_expired__lt=date.today(),
                              is_expired=False, autorenew=False)
    for job in jobs:
        # Setting is_expired to True will trigger job.remove_from_solr()
        job.is_expired = True
        job.save()

    jobs = Job.objects.filter(date_expired__lt=date.today(),
                              is_expired=False, autorenew=True)
    for job in jobs:
        job.date_expired = date.today() + timedelta(days=30)
        # Saving will trigger job.add_to_solr().
        job.save()


@task(name="tasks.task_clear_bu_cache", acks_late=True, ignore_results=True)
def task_clear_bu_cache(buid, **kwargs):
    try:
        BusinessUnit.clear_cache(buid)
    except:
        logging.error(traceback.format_exc(sys.exc_info()))


@task(name="tasks.task_update_solr", acks_late=True, ignore_result=True, soft_time_limit=3600)
def task_update_solr(jsid, **kwargs):
    try:
        import_jobs.update_solr(jsid, **kwargs)
        if kwargs.get('clear_cache', False):
            task_clear_bu_cache.delay(buid=int(jsid), countdown=1500)
            ImportRecord(buid=int(jsid), success=True).save()
    except Exception as e:
        logging.error(traceback.format_exc(sys.exc_info()))
        ImportRecord(buid=int(jsid), success=False).save()
        raise task_update_solr.retry(exc=e)


@task(name='tasks.etl_to_solr', ignore_result=True, send_error_emails=True, soft_time_limit=3600)
def task_etl_to_solr(guid, buid, name):
    try:
        import_jobs.update_job_source(guid, buid, name)
        BusinessUnit.clear_cache(int(buid))
        ImportRecord(buid=int(buid), success=True).save()
    except Exception as e:
        logging.error("Error loading jobs for jobsource: %s", guid)
        logging.exception(e)
        ImportRecord(buid=int(buid), success=False).save()
        raise task_etl_to_solr.retry(exc=e)


@task(name='tasks.jobsfs_to_mongo', ingore_result=True, send_error_emails=False)
def task_jobsfs_to_mongo(guid, buid, name):
    try:
        jobsfs_to_mongo(guid, buid, name)
    except Exception as e:
        logging.error("Error loading mongo from jobsfs for guid: %s", guid)
        logging.exception(e)
        raise task_jobsfs_to_mongo.retry(exc=e)


@task(name='tasks.seoxml_to_mongo', ingore_result=True, send_error_emails=False)
def task_seoxml_to_mongo(buid, **kwargs):
    try:
        seoxml_to_mongo(buid)
    except Exception as e:
        logging.error("Error loading mongo from seoxml for buid: %s", buid)
        logging.exception(e)
        raise task_seoxml_to_mongo.retry(exc=e)


@task(name='tasks.priority_etl_to_solr', ignore_result=True, soft_time_limit=3600)
def task_priority_etl_to_solr(guid, buid, name):
    try:
        import_jobs.update_job_source(guid, buid, name)
        BusinessUnit.clear_cache(int(buid))
        ImportRecord(buid=int(buid), success=True).save()
    except Exception as e:
        logging.error("Error loading jobs for jobsource: %s", guid)
        logging.exception(e)
        ImportRecord(buid=int(buid), success=False).save()
        raise task_priority_etl_to_solr.retry(exc=e)


@task(name="tasks.task_clear_solr", ignore_result=True)
def task_clear_solr(jsid):
    """Delete all jobs for a given Business Unit/Job Source."""
    import_jobs.clear_solr(jsid)


@task(name="tasks.task_force_create", ignore_result=True)
def task_force_create(jsid):
    import_jobs.force_create_jobs(jsid.id)


@task(name="tasks.task_submit_sitemap", ignore_result=True)
def task_submit_sitemap(domain):
    """
    Submits yesterday's sitemap to google for the given domain
    Input:
        :domain: sitemap domain
    """
    ping_google('http://{d}/sitemap.xml'.format(d=domain))


@task(name="tasks.task_submit_all_sitemaps", ignore_result=True)
def task_submit_all_sitemaps():
    sites = SeoSite.objects.all()
    for site in sites:
        task_submit_sitemap.delay(site.domain)


def get_event_list(events):
    """
    Turns a block of json events into a list of events.

    :param events: A json encoded group of events.
    :return: A list of the events as dictionaries.
    """

    try:
        # try parsing post data as json
        event_list = json.loads(events)
    except ValueError:  # nope, it's V1 or V2
        event_list = []
        events = events.splitlines()
        for event_str in events:
            if event_str == '':
                continue
            # nested try :/ -need to catch json exceptions
            try:
                event_list.append(json.loads(event_str))
            except ValueError:  # Bad json
                newrelic.agent.record_exception(
                    *sys.exc_info())
                return []
    except Exception:
        newrelic.agent.record_exception(*sys.exc_info())
        return []
    else:
        # If only one event was posted, this could be any
        # version of the api; event_list will be a list of
        # dicts if using V3 but will be a dict for V1 and V2.
        if type(event_list) != list:
            event_list = [event_list]

    return event_list


def event_list_to_email_log(event_list):
    """
    :param event_list: A list of events, where each event is a dictionary.
    :return: A list of EmailLog objects.
    """
    events_to_create = []
    for event in event_list:
        category = event.get('category', '')
        email_log_args = {
            'email': event['email'], 'event': event['event'],
            'received': date.fromtimestamp(float(event['timestamp'])),
            'category': category,
            # Events can have a response (delivered, deferred),
            # a reason (bounce, block), or neither, but never
            # both.
            'reason': event.get('response',
                                event.get('reason', ''))
        }
        if event['event'] == 'bounce' and category == 'My.jobs email redirect':
            subject = 'My.jobs email redirect failure'
            body = """
                   Contact: %s
                   Type: %s
                   Reason: %s
                   Status: %s
                   """ % (event['email'], event['type'],
                          event['reason'], event['status'])
            issue_dict = {
                'summary': 'Redirect email failure',
                'description': body,
                'issuetype': {'name': 'Bug'}
            }
            log_to_jira(subject, body, issue_dict, event['email'])

        is_list = isinstance(category, list)
        for env in ['QC', 'Staging', 'Local', 'Jenkins']:
            # This event has multiple attached categories and env is one of them
            # or there is only one category, which is env.
            if (is_list and env in category) or \
                    (not is_list and category == env):
                break
        else:
            if is_list:
                try:
                    category.remove('Production')
                except ValueError:
                    pass
                else:
                    if len(category) == 1:
                        # This preserves our prior functionality - if there are
                        # legitimately multiple categories on this email,
                        # category will remain a list and this will get logged
                        # by NewRelic.
                        category = category[0]
            elif category == 'Production':
                category = ''

            # These categories resemble the following:
            # Saved Search Sent (<list of keys>|event_id)
            try:
                event_id = category.split('|')[-1][:-1]
            except AttributeError:
                newrelic.agent.record_exception(*sys.exc_info())
                return []
            if event_id:
                try:
                    log = SavedSearchLog.objects.get(uuid=event_id)
                    email_log_args['send_log'] = log
                    if event['event'] not in BAD_EMAIL:
                        log.was_received = True
                        log.save()
                except SavedSearchLog.DoesNotExist:
                    pass
            events_to_create.append(EmailLog(**email_log_args))

    return events_to_create


@task(name="tasks.process_sendgrid_event", ignore_result=True)
def process_sendgrid_event(events):
    """
    Processes events POSTed by SendGrid.

    :events: A request body containing a batch of events from SendGrid. A batch
             of events is a series of JSON strings separated by new lines
             (Version 1 and 2) or as well formed JSON (Version 3)

    """
    event_list = get_event_list(events)
    events_to_create = event_list_to_email_log(event_list)
    EmailLog.objects.bulk_create(events_to_create)


@task(name="tasks.send_event_email", ignore_result=True)
def send_event_email(email_task):
    """
    Send an appropriate email given an EmailTask instance.

    Inputs:
    :email_task: EmailTask we are using to generate this email
    """
    email_task.task_id = send_event_email.request.id
    email_task.save()

    email_task.send_email()

    email_task.completed_on = datetime.now()
    email_task.save()


@task(name="tasks.requeue_failures", ignore_result=True)
def requeue_failures(hours=8):
    ALERT_THRESHOLD = 15
    period = datetime.datetime.now() - datetime.timedelta(hours=hours)

    failed_tasks = TaskState.objects.filter(state__in=['FAILURE', 'STARTED', 'RETRY'],
                                            tstamp__gt=period,
                                            name__in=['tasks.etl_to_solr',
                                                      'tasks.priority_etl_to_solr'])
    count = len(failed_tasks)
    if count > ALERT_THRESHOLD:
        send_mail(recipient_list=["matt@apps.directemployers.org", "jmclaughlin@apps.directemployers.org"],
                  from_email="requeue_failures@apps.directemployers.org",
                  subject="%s Import tasks failed" % count,
                  message="There were %s failed tasks last night, which exceeded the alert threshold of %s" % (count, ALERT_THRESHOLD),
                  fail_silently=False)

    for task in failed_tasks:
        task_etl_to_solr.delay(*ast.literal_eval(task.args))
        print "Requeuing task with args %s" % task.args


@task(name='clean_import_records', ignore_result=True)
def clean_import_records(days=31):
    days_ago = datetime.now() - timedelta(days=days)
    ImportRecord.objects.filter(date__lt=days_ago).delete()

