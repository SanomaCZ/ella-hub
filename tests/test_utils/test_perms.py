from nose import tools
from django.test import TestCase
from django.contrib.auth.models import User, AnonymousUser, Group
from django.test.client import Client
from ella.core.models import Author
from ella.articles.models import Article
from ella_hub.models import Permission, Role
from ella_hub.utils.perms import (has_model_state_permission,
    has_object_permission, grant_permission)
from ella_hub.utils.perms import (add_role, get_roles,
    remove_role, remove_roles)


class TestPermUtils(TestCase):
    def setUp(self):
        self.user = self.__create_test_user("user", "pass1")
        self.group = Group.objects.create(name="Test group")
        self.role = Role.objects.create(title="Test role")
        self.perm = Permission.objects.create(title="Test perm",
            codename="test_perm")
        self.client = Client()

    def tearDown(self):
        self.user.delete()
        self.group.delete()
        self.role.delete()
        self.perm.delete()

    def test__perm_anonym_user(self):
        anonym_user = AnonymousUser()
        tools.assert_equals(has_model_state_permission(Article, anonym_user,
            "can_whatever"), False)
        author = Author(name="Test author")
        tools.assert_equals(has_object_permission(author, anonym_user,
            "can_whatever"), False)

    def test_perm_does_not_exist(self):
        tools.assert_equals(has_model_state_permission(Article, self.user,
            "can_whatever"), False)
        author = Author(name="Test author")
        tools.assert_equals(has_object_permission(author, self.user,
            "can_whatever"), False)

    def test_perm_restriction(self):
        self.perm.restriction = True
        self.perm.save()
        tools.assert_equals(has_model_state_permission(Article, self.user,
            "test_perm"), False)
        author = Author(name="Test author")
        tools.assert_equals(has_object_permission(author,
            self.user, "test_perm"), False)

        self.user.is_superuser = True
        self.user.save()

        self.perm.restriction = False
        self.perm.save()

        tools.assert_equals(has_model_state_permission(Article, self.user,
            "test_perm"), True)
        tools.assert_equals(has_object_permission(author,
            self.user, "test_perm"), True)


    def test_grant_permission(self):
        add_role(self.user, self.role)
        tools.assert_equals(grant_permission(Article, self.role,
            "can_whatever"), False)

        grant_permission(Article, self.role, "test_perm")
        tools.assert_equals(has_model_state_permission(Article, self.user,
            "test_perm"), True)

    def test_add_role(self):
        add_role(self.user, self.role)
        tools.assert_equals(self.role in get_roles(self.user), True)
        remove_roles(self.user)

        add_role(self.group, self.role)
        tools.assert_equals(self.role in get_roles(self.group), True)


    def test_remove_role(self):
        add_role(self.user, self.role)
        remove_role(self.user, self.role)
        tools.assert_equals(get_roles(self.user), [])

        tools.assert_equals(remove_role(self.user, self.role), False)

        add_role(self.group, self.role)
        remove_role(self.group, self.role)
        tools.assert_equals(get_roles(self.group), [])


    def test_remove_roles(self):
        tools.assert_equals(remove_roles(self.user), False)

        second_role = Role.objects.create(title="Second role")
        add_role(self.user, self.role)
        add_role(self.user, second_role)
        remove_roles(self.user)
        tools.assert_equals(get_roles(self.user), [])

        add_role(self.group, self.role)
        add_role(self.group, second_role)
        remove_roles(self.group)
        tools.assert_equals(get_roles(self.group), [])


    def __create_test_user(self, username, password, is_admin=False):
        user = User.objects.create_user(username=username, password=password)
        user.is_staff = True
        user.is_superuser = is_admin
        user.save()
        return user
