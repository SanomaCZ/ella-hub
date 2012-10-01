# -*- coding: utf-8 -*-

from nose import tools
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.utils.translation import ugettext_lazy as _

from ella.utils import timezone

from ella_hub.models import Permission, Role, ModelPermission, CommonArticle, Recipe


class TestPermissionModels(TestCase):
    def setUp(self):
        self.permission = Permission.objects.create(title="Test Permission",
            codename="test_perm", description="Good perm.")
        self.role = Role.objects.create(title="Test Role", description="Good role.")
        self.content_type = ContentType.objects.get_for_model(CommonArticle)
        self.model_permission = ModelPermission.objects.create(role=self.role,
            permission=self.permission, content_type=self.content_type)

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
