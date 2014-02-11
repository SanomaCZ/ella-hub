from django.core.management import BaseCommand

from ella_hub.api import EllaHubApi
from ella_hub.utils.workflow import init_ella_workflow


class Command(BaseCommand):
    help = "Init ella workflow"

    def handle(self, *args, **options):
        init_ella_workflow(resources=EllaHubApi.collect_resources())
        print 'done'
