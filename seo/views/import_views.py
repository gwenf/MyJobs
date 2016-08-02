# Library Imports
from datetime import timedelta
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from djcelery.models import TaskState
import json
import logging

# Our Imports
from seo import helpers
from seo.decorators import sns_json_message
from tasks import task_check_solr_count, task_etl_to_solr, task_update_solr,\
    task_priority_etl_to_solr,task_jobsfs_to_mongo, task_seoxml_to_mongo



# Logging
logger = logging.getLogger(__name__)

@csrf_exempt
@sns_json_message
def confirm_load_jobs_from_etl(response):
    """
    Called when a job source is ready to be imported. Calls celery update
    tasks.

    """

    blocked_jsids=('4051c882-fa2c-4c93-9db5-91c9add39def',
                     '10f89212-654e-4ee5-8655-2bbb4770252f',
                     'e6fa8adb-07c9-4b15-87ad-5816c3968d43',
                     '8667bd35-c6d3-4008-8b62-36d6b6e3bb62',
                     'c94ddf73-23c8-4b6c-ad5a-a98b5f2a04b0',
                     '5de582a0-cab5-45f8-88a8-a31f7fe03025',
                     '72690d11-b3fc-403c-8726-c80883e27774',
                     'e0fe5671-c591-40d4-bba9-f0d8542882e2',
                     'dd5fd646-655b-4867-8784-700bb5c6315b',
                     'c4d56d17-7b35-436a-8871-80d8c2e37bf9',
                     'ff794484-8f24-4bdc-96e3-227c9dec2c26',
                     'cd7fc92a-9bff-4bbd-a10a-ffd6a57a93a1',
                     '3388e1e9-8292-4d6f-a5ee-c4ed2bae59a4',
                     '868672a0-c22b-4337-9dcc-2fa5b6671592',
                     '09ae740c-36d8-432d-bc84-de538dbac8fd',
                     '03516574-c452-45ab-b217-8ea0357be747',
                     '1b0e4f3b-a9e1-40b9-8c8b-85a65882c2a3',
                     'de0762b3-698b-4a3b-92d2-388144edb15a',
                     '77e1b0eb-4017-44b7-ab9d-898d35390b81',
                     '905ad700-0a73-4da1-8bf5-b12bf6ba89a7',
                     'f39aaaf4-e126-4d53-bdf3-98831f45d731',
                     '1f78a1c6-1ced-4d80-b338-1c3bd8ac57a7',
                     '4d9330b3-8ca8-41ef-8ca2-305da6ddc5f0',
                     'aeb6cdb4-1b02-4bab-b398-4d3980097659',
                     'c20f2c86-bd08-4cce-af94-b3339944676e',
                     '249308c5-623b-41b9-9364-2589e49b5e02',
                     '27f0d51d-2882-4168-bfca-cb415f666fb3',
                     '8d506b65-f911-449e-bad8-c308a196e1c0',
                     'c6203550-2435-4137-9c11-b0710f3ef4cf',
                     '682deefb-fde9-4de2-8985-13371d04a8ff',
                     'c8bfb1b1-398a-46a4-a1f4-fbdb5354ee78',
                     '769ca60a-f4e7-446d-b2ba-b66a5a3e9313',
                     '7ecfcde8-b7e1-4bb1-a671-b52d729903b5',
                     '817d2b90-9299-4ef6-b484-46208ce69e19',
                     '00152da3-1abe-458e-8895-121ca9008cf7',
                     '94d95b97-24e4-4d98-8ecf-1dce6202c523',
                     'ccc31e40-a65f-46b0-a194-b0517c33a7f6',
                     'be4dcd74-ff51-4f99-8057-55a876b3ce56',
                     '15079de2-7de2-4191-b8cf-7924036b4b97',
                     'c8d8da8c-542f-4620-b90b-4a37d55d659f',
                     '66cbd5e6-c86b-4659-b80c-11aa5a5fa6a7',
                     '265357bd-a619-40b7-b9bc-9674d6e96400',
                     '7d6ea31f-e36d-43e7-b68e-d9dbd45446f7',
                     'b3c58f53-144a-4de7-807b-8fe140259d7f',
                     '23322abe-6faf-4303-b08b-713e5127e019',
                     'bedee5c5-a9ca-459f-899b-29482712d7c9',
                     '69f485d0-40d5-430f-a5eb-6221ee14092d',
                     'b0c01590-0085-4ab5-b0b0-27149fa0fb4a',
                     '536dcdbb-2a88-40d8-bf68-8630306c2818',
                     'ad875783-c49e-49ff-b82a-b0538026e089',
                     '0ab41358-8323-4863-9f19-fdb344a75a35',)

    logger.info("sns received for ETL")

    if response:
        if response.get('Subject', None)!='END':
            msg=json.loads(response['Message'])
            jsid=msg['jsid']
            buid=msg['buid']
            name=msg['name']
            prio=msg["priority"]
            if jsid.lower() in blocked_jsids:
                logger.info("Ignoring sns for %s", jsid)
                return None

            logger.info("Creating ETL Task (%s, %s, %s)"%(jsid, buid, name))
            if int(prio)==1:
                task_priority_etl_to_solr.delay(jsid, buid, name)
            else:
                task_etl_to_solr.delay(jsid, buid, name)
            task_jobsfs_to_mongo.delay(jsid, buid, name)


@csrf_exempt
@sns_json_message
def send_sns_confirm(response):
    """
    Called when a job feed file is ready to be imported. Calls celery update
    tasks.

    """
    # Postajob buids and state job bank buids
    allowed_buids=[1228, 5480]+range(2650, 2704)

    logger.info("sns received for SEOXML")
    if response:
        if response['Subject']!='END':
            buid=response['Subject']
            if int(buid) in allowed_buids:
                logger.info("Creating update_solr task for %s"%buid)
                set_title=helpers.create_businessunit(int(buid))
                task_update_solr.delay(buid, force=True, set_title=set_title)
                task_seoxml_to_mongo.delay(buid)
            else:
                logger.info("Skipping update_solr for %s because it is not in the allowed buids list." % buid)


@staff_member_required
def import_dashboard(request):
    Tminus24 = timezone.now() - timedelta(days=1)
    Tminus48 = timezone.now() - timedelta(days=2)

    last24 = TaskState.objects.filter(tstamp__gt=Tminus24)
    last24 = last24.filter(name__in=['tasks.priority_etl_to_solr',
                                   'tasks.etl_to_solr',
                                   'tasks.task_update_solr'])
    
    previous24 = TaskState.objects.filter(tstamp__lt=Tminus24, tstamp__gt=Tminus48)
    previous24 = previous24.filter(name__in=['tasks.priority_etl_to_solr',
                                            'tasks.etl_to_solr',
                                            'tasks.task_update_solr'])
    today = {
             'tasks': last24.count(),
             'failures': last24.filter(state='FAILURE').count()
    }
    yesterday = {
             'tasks': previous24.count(),
             'failures': previous24.filter(state='FAILURE').count()
    }

    return render_to_response('seo/import_dashboard.html', {'today': today, 'yesterday':yesterday},
                              context_instance=RequestContext(request))
