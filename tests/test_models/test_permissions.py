# -*- coding: utf-8 -*-

from nose import tools
from django.contrib.auth.models import User, Group
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.utils.translation import ugettext_lazy as _

from ella.articles.models import Article
from ella.utils import timezone

from ella_hub.models import Permission, Role, ModelPermission, PrincipalRoleRelation


class TestPermissionModels(TestCase):
    def setUp(self):
        self.permission = Permission.objects.create(title="Test Permission",
            codename="test_perm", description="Good perm.")
        self.role = Role.objects.create(title="Test Role", description="Good role.")
        self.content_type = ContentType.objects.get_for_model(Article)
        self.model_permission = ModelPermission.objects.create(role=self.role,
            permission=self.permission, content_type=self.content_type)
        self.prr = PrincipalRoleRelation(role=self.role)

    def tearDown(self):
        ModelPermission.objects.all().delete()
        Permission.objects.all().delete()
        Role.objects.all().delete()

    def test_to_string(self):
        # permission
        tools.assert_equals(unicode(self.permission), u"%s (%s)" % (
            self.permission.title, self.permission.codename))

        self.permission.title = u"Someľčť titleščľ"
        self.permission.codename = u"someľčť_titleščľ"
        self.permission.save()

        tools.assert_equals(unicode(self.permission), u"%s (%s)" % (
            self.permission.title, self.permission.codename))

        # role
        tools.assert_equals(unicode(self.role), u"%s" % (self.role.title))

        self.role.title = u"Someľčť titleščľ"
        self.role.save()

        tools.assert_equals(unicode(self.role), u"%s" % (self.role.title))

        # model_permission
        tools.assert_equals(unicode(self.model_permission), u"%s / %s / %s" % (
            self.permission.title, self.role.title,
            self.content_type.name))

        # principal role relation
        self.user = User.objects.create(username="admin_user", password="pass1")
        self.group = Group.objects.create(name="test_group")

        tools.assert_equals(unicode(self.prr), u"- / %s" % self.role.title)

        self.prr.set_principal(self.group)
        tools.assert_equals(unicode(self.prr), u"%s / %s" % (self.group.name, self.role.title))
        self.prr.set_principal(self.user)
        tools.assert_equals(unicode(self.prr), u"%s / %s" % (self.user.username, self.role.title))

    def test_principals(self):
        self.user = User.objects.create(username="admin_user", password="pass1")
        self.group = Group.objects.create(name="test_group")
        self.prr = PrincipalRoleRelation.objects.create(role=self.role)

        self.prr.set_principal(self.user)
        self.prr.save()
        tools.assert_equals(self.prr.get_principal(), self.user)

        self.prr.set_principal(self.group)
        self.prr.save()
        tools.assert_equals(self.prr.get_principal(), self.user)

        self.prr.unset_principals()
        self.prr.set_principal(self.group)
        self.prr.save()
        tools.assert_equals(self.prr.get_principal(), self.group)

        self.role.add_principal(self.user)
        tools.assert_equals(self.role.get_users(), [self.user])

        self.prr.unset_principals()
        self.prr.save()
        self.role.add_principal(self.group)
        tools.assert_equals(self.role.get_groups(), [self.group])
