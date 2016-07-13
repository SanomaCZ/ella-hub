import shutil

from django.core.management import BaseCommand

from ella_hub.utils import get_media_drafts_root


class Command(BaseCommand):
    help = "Remove draft files created during upload photos"

    def handle(self, *args, **options):
        shutil.rmtree(get_media_drafts_root())
        print('Tmp files removed')
