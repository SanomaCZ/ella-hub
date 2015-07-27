from django.db import models, IntegrityError
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import date

from jsonfield import JSONField

from ella.core.models import Publishable


class Draft(models.Model):
    """Auto-saved objects and user templates."""

    content_type = models.ForeignKey(ContentType, verbose_name=_("Model"))
    user = models.ForeignKey(User, verbose_name=_("User"))
    name = models.CharField(_("Name"), max_length=64, blank=True)

    timestamp = models.DateTimeField(editable=False)
    data = JSONField(_("Data"))

    def __unicode__(self):
        if self.name:
            return u"%s (%s)" % (self.name, date(self.timestamp, "y-m-d H:i"))
        else:
            return u"%s %s (%s)" % (
                _("Autosaved"),
                _(self.content_type.name),
                date(self.timestamp, "y-m-d H:i")
            )

    def save(self, *args, **kwargs):
        self.timestamp = now().replace(microsecond=0)
        super(Draft, self).save(*args, **kwargs)

    class Meta:
        app_label = "ella_hub"
        verbose_name = _("Draft item")
        verbose_name_plural = _("Draft items")
        ordering = ("-timestamp",)


class PublishableLockManager(models.Manager):
    def lock(self, publishable, user):
        try:
            return self.create(publishable=publishable, locked_by=user)
        except IntegrityError:
            # duplicate entry 'publishable'
            return None

    def is_locked(self, publishable):
        try:
            return self.get(publishable=publishable)
        except PublishableLock.DoesNotExist:
            return None

    def unlock(self, publishable):
        return self.filter(publishable=publishable).delete()


class PublishableLock(models.Model):
    """Lock for publishable objects."""

    objects = PublishableLockManager()

    publishable = models.OneToOneField(
        Publishable,
        verbose_name=_("Locked publishable")
    )
    locked_by = models.ForeignKey(User)
    timestamp = models.DateTimeField(editable=False, auto_now=True)

    def __unicode__(self):
        return _("Publishable #%d locked by '%s'") % (
            self.publishable.id,
            self.locked_by.username,
        )

    class Meta:
        app_label = "ella_hub"
        verbose_name = _("Publishable lock")
        verbose_name_plural = _("Publishable locks")
