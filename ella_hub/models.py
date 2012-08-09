#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import date

from jsonfield import JSONField


class Draft(models.Model):
    """Auto-saved objects and user templates."""

    content_type = models.ForeignKey(ContentType, verbose_name=_('Model'))
    user = models.ForeignKey(User, verbose_name=_('User'))
    name = models.CharField(_('Name'), max_length=64, blank=True)
    timestamp = models.DateTimeField(editable=False, auto_now=True)
    data = JSONField(_('Data'))

    def __unicode__(self):
        if self.name != '':
            return u"%s (%s)" % (self.name, date(self.timestamp, 'y-m-d H:i'))
        else:
            return u"%s %s (%s)" % (_("Autosaved"), _(self.content_type.name),
                date(self.timestamp, 'y-m-d H:i'))

    class Meta:
        verbose_name = _('Draft item')
        verbose_name_plural = _('Draft items')
        ordering = ('-timestamp',)
