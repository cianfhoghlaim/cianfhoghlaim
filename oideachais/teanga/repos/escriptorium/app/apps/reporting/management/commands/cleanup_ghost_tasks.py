import logging

from django.core.management.base import BaseCommand

from reporting.models import TaskReport

logger = logging.getLogger()


class Command(BaseCommand):
    help = "Check for TaskReport instances with a 'running' status if there is a running process associated, if there is not, set their status to CRASHED."

    verbosity_map = [
        logging.ERROR,
        logging.WARNING,
        logging.INFO,
        logging.DEBUG
    ]

    def handle(self, *args, **kwargs):
        verbosity = kwargs['verbosity']
        logger.setLevel(self.verbosity_map[verbosity])
        count = 0
        for report in TaskReport.objects.filter(workflow_state=TaskReport.WORKFLOW_STATE_STARTED):
            if not report.check_process_running():
                logger.debug('Cleaning up task %d : %s.' % (report.id, report.task_id))
                report.workflow_state = TaskReport.WORKFLOW_STATE_ERROR
                report.save()
                count += 1
        logger.info(f'Cleaned up {count} ghost tasks.')
