from nose import tools
from django.test import TestCase
from django.contrib.auth.models import User, AnonymousUser
from django.test.client import Client

from ella.core.models import Author

from ella_hub.utils.perms import (has_obj_perm, has_user_model_perm,
    has_user_model_object_with_any_perm, is_resource_allowed)


class TestPermsFunctions(TestCase):
    def setUp(self):
        self.user = self.__create_test_user("user", "pass1")
        self.client = Client()

    def tearDown(self):
        self.user.delete()

    def test_has_obj_perm(self):
        author = Author(name="awesome_name", slug="awesome-name",
            email="mail@mail.com", text="like a boss", description="what can i say", id=100)
        author.save()
        self.user.grant('change_author', author)
        tools.assert_equals(has_obj_perm(self.user, author), True)

    def test_no_perms_anonymous_user(self):
        anonym_user = AnonymousUser()
        tools.assert_equals(has_user_model_object_with_any_perm(anonym_user, 'article'),
            False)

    def __create_test_user(self, username, password, is_admin=False):
        user = User.objects.create_user(username=username, password=password)
        user.is_staff = True
        user.is_superuser = is_admin
        user.save()
        return user
