from nose import tools

from django.contrib.auth.models import User
from django.test import TestCase
from django.test.client import Client
from django.utils import simplejson as json

from ella_hub.utils import get_all_resource_classes
from ella_hub.utils.perms import add_role
from ella_hub.utils.test_helpers import create_advanced_workflow, delete_test_workflow


class TestLoginResponse(TestCase):
    def setUp(self):
        self.user = self.__create_test_user("user", "pass", True)
        self.client = Client()
        create_advanced_workflow(self, get_all_resource_classes())

    def tearDown(self):
        self.user.delete()
        delete_test_workflow()

    def test_base_structure(self):
        api_key, auth_tree, system = self.__login("user", "pass")
        headers = self.__build_headers("user", api_key)

        tools.assert_true("articles" in auth_tree)
        tools.assert_true("resources" in system)

        for resource in auth_tree["articles"].values():
            tools.assert_true("allowed_http_methods" in resource)
            tools.assert_true("fields" in resource)
            for field in resource["fields"].values():
                tools.assert_true("readonly" in field)
                tools.assert_true("disabled" in field)

        self.__logout(headers)

    def test_super_role_fields(self):
        (api_key, auth_tree, system) = self.__login("user", "pass")
        headers = self.__build_headers("user", api_key)

        add_role(self.user, self.super_role)

        for resource in auth_tree["articles"].values():
            for field_name, field_values in resource["fields"].items():
                if field_name not in ["resource_uri"]:
                    tools.assert_false(field_values["readonly"])
                    tools.assert_false(field_values["disabled"])

        self.__logout(headers)


    def test_base_role_fields(self):
        add_role(self.user, self.base_role)
        self.user.is_superuser = False
        self.user.save()

        api_key, auth_tree, system = self.__login("user", "pass")
        headers = self.__build_headers("user", api_key)

        for resource_name, resource_fields in auth_tree["articles"].items():
            for field_name, field_values in resource_fields["fields"].items():
                if resource_name == "article" and field_name == "authors":
                    tools.assert_true(field_values["disabled"])
                else:
                    tools.assert_false(field_values["disabled"])
                tools.assert_true(field_values["readonly"])

        self.__logout(headers)


    def __create_test_user(self, username, password, is_admin=False):
        user = User.objects.create_user(username=username, password=password)
        user.is_staff = True
        user.is_superuser = is_admin
        user.save()
        return user

    def __login(self, username, password):
        response = self.client.post('/admin-api/login/', data={"username": username, "password": password})
        tools.assert_equals(response.status_code, 200)

        resources = self.__get_response_json(response)
        tools.assert_true("api_key" in resources)
        tools.assert_true("auth_tree" in resources)
        tools.assert_true("system" in resources)

        return resources["api_key"], resources["auth_tree"], resources["system"]

    def __logout(self, headers):
        response = self.client.post('/admin-api/logout/', **headers)
        tools.assert_equals(response.status_code, 302)

    def __build_headers(self, username, api_key):
        return {
            "HTTP_AUTHORIZATION": "ApiKey %s:%s" % (username, api_key),
        }

    def __get_response_json(self, response):
        return json.loads(response.content)
