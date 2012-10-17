from nose import tools
from django.test import TestCase
from django.contrib.auth.models import User, AnonymousUser
from django.test.client import Client

from ella.core.models import Author

from ella_hub.utils.perms import is_resource_allowed


class TestPermsFunctions(TestCase):
    def setUp(self):
        self.user = self.__create_test_user("user", "pass1")
        self.client = Client()

    def tearDown(self):
        self.user.delete()

    def __create_test_user(self, username, password, is_admin=False):
        user = User.objects.create_user(username=username, password=password)
        user.is_staff = True
        user.is_superuser = is_admin
        user.save()
        return user
