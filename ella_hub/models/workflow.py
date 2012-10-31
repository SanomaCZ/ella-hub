from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User

from ella_hub.models.permissions import Permission, Role


class Workflow(models.Model):

    title = models.CharField(_("Title"), max_length=128, blank=False, unique=True)
    description = models.TextField(_("Description"), blank=True)
    initial_state =models.ForeignKey("State", verbose_name=_("Initial state"),
        blank=True, null=True, related_name="workflow_initial_state")

    permissions = models.ManyToManyField(Permission, verbose_name=_("Permissions"),
        through="WorkflowPermissionRelation")

    def get_initial_state(self):
        if self.initial_state:
            return self.initial_state
        else:
            try:
                return self.states.all()[0]
            except IndexError:
                return None

    def set_to_model(self, model):
        content_type = ContentType.objects.get_for_model(model)
        try:
            relation = WorkflowModelRelation.objects.get(content_type=content_type)
        except WorkflowModelRelation.DoesNotExist:
            WorkflowModelRelation.objects.create(content_type=content_type, workflow=self)
        else:
            relation.workflow = self
            relation.save()

    def __unicode__(self):
        if self.initial_state:
            return u"%s : %s" % (self.title, self.initial_state.title)
        else:
            return u"%s" % self.title

    class Meta:
        app_label = "ella_hub"
        verbose_name = _("Workflow")
        verbose_name_plural = _("Workflows")


class State(models.Model):

    title = models.CharField(_("Title"), max_length=128, blank=False)
    codename = models.CharField(_("Codename"), max_length=128, blank=False)
    description = models.TextField(_("Description"), blank=True)
    workflow = models.ForeignKey("Workflow", verbose_name=_("Workflow"),
        blank=True, null=True, related_name="states")
    transitions = models.ManyToManyField("Transition", verbose_name=_("Transitions"),
        blank=True, null=True)

    def __unicode__(self):
        return u"%s" % self.title

    class Meta:
        app_label = "ella_hub"
        verbose_name = _("State")
        verbose_name_plural = _("States")


class Transition(models.Model):

    title = models.CharField(_("Title"), max_length=128, blank=False)
    description = models.TextField(_("Description"), blank=True)
    workflow = models.ForeignKey("Workflow", verbose_name=_("Workflow"), blank=True)
    destination = models.ForeignKey("State", verbose_name=_("Destination"), blank=False)

    def __unicode__(self):
        return u"%s (-> %s)" % (self.title, self.destination.title)

    class Meta:
        app_label = "ella_hub"
        verbose_name = _("Transition")
        verbose_name_plural = _("Transition")


class StateObjectRelation(models.Model):

    content_type = models.ForeignKey(ContentType, verbose_name=_("Content type"),
        related_name="state_object", blank=True, null=True)
    content_id = models.PositiveIntegerField(_("Content id"), blank=True, null=True)
    content = generic.GenericForeignKey(ct_field="content_type", fk_field="content_id")
    state = models.ForeignKey(State, verbose_name = _("State"))

    def __unicode__(self):
        return "%s %s - %s" % (self.content_type.name, self.content_id, self.state.title)

    class Meta:
        unique_together = ("content_type", "content_id", "state")
        app_label = "ella_hub"
        verbose_name = _("State-Object Relation")
        verbose_name_plural = _("State-Object Relations")


class StatePermissionRelation(models.Model):

    state = models.ForeignKey("State", verbose_name=_("State"))
    permission = models.ForeignKey("Permission", verbose_name=_("Permission"))
    role = models.ForeignKey("Role", verbose_name=_("Role"))

    def __unicode__(self):
        return "%s / %s / %s" % (self.state.title, self.role.title, self.permission.title)

    class Meta:
        app_label = "ella_hub"
        verbose_name = _("State-Permission Relation")
        verbose_name_plural = _("State-Permission Relations")


class WorkflowModelRelation(models.Model):

    content_type = models.ForeignKey(ContentType, verbose_name=_("Content Type"),
        unique=True)
    workflow = models.ForeignKey(Workflow, verbose_name=_("Workflow"),
        related_name="wmr_workflow")

    def __unicode__(self):
        return "%s / %s" % (self.content_type.name, self.workflow.title)

    class Meta:
        app_label = "ella_hub"
        verbose_name = _("Workflow-Model Relation")
        verbose_name_plural = _("Workflow-Model Relations")


class WorkflowPermissionRelation(models.Model):

    workflow = models.ForeignKey(Workflow, verbose_name=_("Workflow"),
        related_name="wpr_workflow")
    permission = models.ForeignKey(Permission, related_name="permissions")

    def __unicode__(self):
        return "%s / %s" % (self.workflow.title, self.permission.title)

    class Meta:
        app_label = "ella_hub"
        verbose_name = _("Workflow-Permission Relation")
        verbose_name_plural = _("Workflow-Permission Relations")
