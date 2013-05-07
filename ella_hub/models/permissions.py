from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User, Group
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from ella.core.cache import CachedForeignKey


class Permission(models.Model):
    """
    <content_types> - models that have actual permission
    """
    title = models.CharField(_("Name"), max_length=128, unique=True)
    codename = models.CharField(_("Codename"), max_length=128, unique=True)
    description = models.TextField(_("Description"), blank=True)
    restriction = models.BooleanField(_("Restriction"), default=False)
    content_types = models.ManyToManyField(ContentType, verbose_name=_("Content Types"),
        blank=True, null=True, related_name="content_types")

    def __unicode__(self):
        return "%s (%s)" % (self.title, self.codename)

    class Meta:
        app_label = "ella_hub"
        verbose_name = _("Permission")
        verbose_name_plural = _("Permissions")


class ModelPermission(models.Model):
    """
    Mapping a <role> to a <permission> for specific <content_type>.
    """
    role = CachedForeignKey("Role", verbose_name=_("Role"), blank=True, null=True)
    permission = CachedForeignKey(Permission, verbose_name=_("Permission"))
    content_type = CachedForeignKey(ContentType, verbose_name=_("Content type"))

    def __unicode__(self):
        return "%s / %s / %s" % (self.permission.title, self.role.title, self.content_type.name)

    class Meta:
        app_label = "ella_hub"
        verbose_name = _("Model Permission")
        verbose_name_plural = _("Model Permissions")
        unique_together = (
            ('role', 'permission', 'content_type'),
        )


class PrincipalRoleRelation(models.Model):
    """
    Mapping <role> to principal (<user> or <group>).
    """
    user = CachedForeignKey(User, verbose_name=_("User"), blank=True, null=True)
    group = CachedForeignKey(Group, verbose_name=_("Group"), blank=True, null=True)
    role = CachedForeignKey("Role", verbose_name=_("Role"))

    content_type = CachedForeignKey(ContentType, verbose_name=_("Content type"), blank=True, null=True)
    content_id = models.PositiveIntegerField(verbose_name=_("Content id"), blank=True, null=True)
    content = generic.GenericForeignKey(ct_field="content_type", fk_field="content_id")

    def get_principal(self):
        # User has higher priority.
        return self.user or self.group

    def set_principal(self, principal):
        if isinstance(principal, User):
            self.user = principal
        else:
            self.group = principal

    def unset_principals(self):
        self.user = None
        self.group = None

    principal = property(get_principal, set_principal)

    def __unicode__(self):
        if self.user:
            return "%s / %s" % (self.user.username, self.role.title)
        elif self.group:
            return "%s / %s" % (self.group.name, self.role.title)
        else:
            return "- / %s" % (self.role.title)

    class Meta:
        app_label = "ella_hub"
        verbose_name = _("Principal Role Relation")
        verbose_name_plural = _("Principal Role Relations")


class Role(models.Model):

    title = models.CharField(_("Title"), max_length=128, blank=False)
    description = models.TextField(_("Description"), blank=True)

    def add_principal(self, principal, content=None):
        if isinstance(principal, User):
            PrincipalRoleRelation.objects.create(user=principal, role=self)
        else:
            PrincipalRoleRelation.objects.create(group=principal, role=self)

    def get_groups(self, content=None):
        """
        Returns all groups role is assigned to.
        """
        relations = PrincipalRoleRelation.objects.filter(role=self,
            content_id=None, content_type=None).exclude(group=None).select_related('group')
        return [relation.group for relation in relations]

    def get_users(self, content=None):
        """
        Returns all users role is assigned to.
        """
        relations = PrincipalRoleRelation.objects.filter(role=self,
            content_id=None, content_type=None).exclude(user=None).select_related('user')
        return [relation.user for relation in relations]

    def __unicode__(self):
        return u"%s" % self.title

    class Meta:
        app_label = "ella_hub"
        verbose_name = _("Role")
        verbose_name_plural = _("Roles")
