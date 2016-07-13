import os
import shutil

from django.core.management import BaseCommand

from ella_hub.utils import get_media_drafts_root


class Command(BaseCommand):
    help = "Remove draft files created during upload photos"

    def handle(self, *args, **options):
        drafts_dir = get_media_drafts_root()
        if os.path.exists(drafts_dir) and os.path.isdir(drafts_dir):
            shutil.rmtree(drafts_dir)
            print('Tmp files removed')
        else:
            print("Path %s does not exists or last part is not directory" % drafts_dir)
