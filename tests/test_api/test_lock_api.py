import unittest
import django.utils.simplejson as json

from nose import tools
from django.test.client import Client
from django.contrib.auth.models import User
from ella.utils.test_helpers import create_basic_categories
from ella.utils import timezone

from ella_hub.models import PublishableLock, Recipe


class TestLockApi(unittest.TestCase):
    def setUp(self):
        self.user = self.__create_test_user("user", "pass", is_admin=True)
        self.client = Client()

        create_basic_categories(self)
        self.publishable = Recipe.objects.create(title="Spinach",
            category=self.category_nested, publish_from=timezone.now(),
            slug="spinach-ou-jeee", cook_time=30)

    def tearDown(self):
        self.user.delete()
        self.publishable.delete()

    def __create_test_user(self, username, password, is_admin=False):
        user = User.objects.create_user(username=username, password=password)
        user.is_superuser = is_admin
        user.save()
        return user

    def test_locked_unlocked(self):
        api_key = self.__login("user", "pass")
        headers = self.__build_headers("user", api_key)
        url = "/admin-api/is-publishable-locked/%d/" % self.publishable.id

        response = self.client.get(url, **headers)
        resources = self.__get_response_json(response)
        tools.assert_false(resources["locked"])

        PublishableLock.objects.lock(self.publishable, self.user)
        response = self.client.get(url, **headers)
        resources = self.__get_response_json(response)
        tools.assert_true(resources["locked"])
        tools.assert_equals(resources["locked_by"],
            "/admin-api/user/%d/" % self.user.id)

        PublishableLock.objects.unlock(self.publishable)
        response = self.client.get(url, **headers)
        resources = self.__get_response_json(response)
        tools.assert_false(resources["locked"])

        self.__logout(headers)

    def test_double_lock(self):
        api_key = self.__login("user", "pass")
        headers = self.__build_headers("user", api_key)
        url = "/admin-api/lock-publishable/%d/" % self.publishable.id

        response = self.client.post(url, **headers)
        resources = self.__get_response_json(response)
        tools.assert_true(resources["locked"])

        # 2nd lock should fail
        response = self.client.post(url, **headers)
        resources = self.__get_response_json(response)
        tools.assert_false(resources["locked"])

        self.__logout(headers)

    def test_lock_unlock(self):
        api_key = self.__login("user", "pass")
        headers = self.__build_headers("user", api_key)
        lock_url = "/admin-api/lock-publishable/%d/" % self.publishable.id
        unlock_url = "/admin-api/unlock-publishable/%d/" % self.publishable.id

        response = self.client.post(lock_url, **headers)
        resources = self.__get_response_json(response)
        tools.assert_true(resources["locked"])
        tools.assert_true(PublishableLock.objects.is_locked(self.publishable))

        response = self.client.post(unlock_url, **headers)
        tools.assert_false(PublishableLock.objects.is_locked(self.publishable))

        self.__logout(headers)

    def __login(self, username, password):
        response = self.client.post('/admin-api/login/', data={"username": username, "password": password})
        tools.assert_equals(response.status_code, 200)

        resources = self.__get_response_json(response)
        tools.assert_true("api_key" in resources)

        return resources["api_key"]

    def __logout(self, headers):
        response = self.client.post('/admin-api/logout/', **headers)
        tools.assert_equals(response.status_code, 302)

    def __build_headers(self, username, api_key):
        return {
            "HTTP_AUTHORIZATION" : "ApiKey %s:%s" % (username, api_key),
        }

    def __get_response_json(self, response):
        return json.loads(response.content)
