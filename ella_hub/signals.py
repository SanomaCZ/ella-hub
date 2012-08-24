from django.db.models import signals
from django.contrib.auth.models import User

from ella.core.models import Publishable
from tastypie.models import create_api_key

from ella_hub.models import PublishableLock
from ella_hub.exceptions import PublishableLocked


# generate API key for new user
signals.post_save.connect(create_api_key, sender=User)
