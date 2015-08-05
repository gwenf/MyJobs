import ast
from django.core.management.base import NoArgsCommand
from djcelery.models import TaskState
from datetime import datetime, timedelta
from tasks import task_etl_to_solr

class Command(NoArgsCommand):
    args = 'None'
    help = 'REqueues tasks that failed in the last eight hours.'

    def handle_noargs(self, **options):
        eight_hours_ago = datetime.now() - timedelta(hours=8)

        failed_tasks = TaskState.objects.filter(state__in=['FAILURE', 'STARTED', 'RETRY'], 
                                                tstamp__gt=eight_hours_ago, 
                                                name__in=['tasks.etl_to_solr',
                                                          'tasks.priority_etl_to_solr'])

        for task in failed_tasks:
            task_etl_to_solr.delay(*ast.literal_eval(task.args))
            print "Requeuing task with args %s" % task.args