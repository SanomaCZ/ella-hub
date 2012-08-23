from django.dispatch import receiver
from django.db.models import signals
from django.contrib.auth.models import User

from ella.core.models import Publishable
from tastypie.models import create_api_key

from ella_hub.models import PublishableLock


# generate API key for new user
signals.post_save.connect(create_api_key, sender=User)


@receiver(signals.pre_save)
def check_locked_publishable(sender, instance, **kwargs):
    if not isinstance(instance, Publishable):
        return

    try:
        lock = PublishableLock.objects.get(publishable=instance)
    except PublishableLock.DoesNotExist:
        return

    if lock.locked:
        raise ValueError(unicode(lock))
