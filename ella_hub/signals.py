from django.db.models import signals
from django.contrib.auth.models import User

from tastypie.models import create_api_key


# generate API key for new user
signals.post_save.connect(create_api_key, sender=User)
