from django.db.models import signals
from django.contrib.auth.models import User

from tastypie.models import ApiKey

from ella_hub.utils.timezone import now


def create_api_key(sender, **kwargs):
        """
        A signal for hooking up automatic ``ApiKey`` creation.
        """
        if kwargs.get('created') is True:
            ApiKey.objects.create(user=kwargs.get('instance'), created=now())

# generate API key for new user
signals.post_save.connect(create_api_key, sender=User)
