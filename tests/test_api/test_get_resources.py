from nose import tools
from django.contrib.auth.models import User
import django.utils.simplejson as json
from django.test import TestCase
from django.test.client import Client

from ella.utils.test_helpers import create_basic_categories
from ella.utils import timezone

from ella_hub.models import CommonArticle, Recipe, Encyclopedia


class TestGetResources(TestCase):
    def setUp(self):
        self.user = self.__create_test_user("user", "pass", True)
        self.client = Client()
        create_basic_categories(self)
        CommonArticle.objects.create(title="Jop",
            category=self.category, publish_from=timezone.now(), slug="jop")
        Recipe.objects.create(title="Spinach", category=self.category_nested,
            publish_from=timezone.now(), slug="spinach", cook_time=30)
        Encyclopedia.objects.create(title="Jop3", category=self.category,
            publish_from=timezone.now(), slug="jop3")

    def tearDown(self):
        self.user.delete()
        CommonArticle.objects.all().delete()
        Recipe.objects.all().delete()
        Encyclopedia.objects.all().delete()

    def __create_test_user(self, username, password, is_admin=False):
        user = User.objects.create_user(username=username, password=password)
        user.is_staff = True
        user.is_superuser = is_admin
        user.save()
        return user

    def test_ella_resources_present(self):
        api_key = self.__login("user", "pass")
        headers = self.__build_headers("user", api_key)

        response = self.client.get("/admin-api/", **headers)
        resources = self.__get_response_json(response)

        tools.assert_true("user" in resources)
        tools.assert_true("list_endpoint" in resources["user"])
        tools.assert_true("schema" in resources["user"])

        tools.assert_true("site" in resources)
        tools.assert_true("list_endpoint" in resources["site"])
        tools.assert_true("schema" in resources["site"])

        tools.assert_true("article" in resources)
        tools.assert_true("list_endpoint" in resources["article"])
        tools.assert_true("schema" in resources["article"])

        tools.assert_true("author" in resources)
        tools.assert_true("list_endpoint" in resources["author"])
        tools.assert_true("schema" in resources["author"])

        tools.assert_true("category" in resources)
        tools.assert_true("list_endpoint" in resources["category"])
        tools.assert_true("schema" in resources["category"])

        tools.assert_true("photo" in resources)
        tools.assert_true("list_endpoint" in resources["photo"])
        tools.assert_true("schema" in resources["photo"])

        tools.assert_true("formatedphoto" in resources)
        tools.assert_true("list_endpoint" in resources["formatedphoto"])
        tools.assert_true("schema" in resources["formatedphoto"])

        tools.assert_true("format" in resources)
        tools.assert_true("list_endpoint" in resources["format"])
        tools.assert_true("schema" in resources["format"])

        tools.assert_true("listing" in resources)
        tools.assert_true("list_endpoint" in resources["listing"])
        tools.assert_true("schema" in resources["listing"])

        tools.assert_true("publishable" in resources)
        tools.assert_true("list_endpoint" in resources["publishable"])
        tools.assert_true("schema" in resources["publishable"])

        self.__logout(headers)

    def test_ella_resources_accessible(self):
        api_key = self.__login("user", "pass")
        headers = self.__build_headers("user", api_key)

        response = self.client.get("/admin-api/", **headers)
        resources = self.__get_response_json(response)

        for resource_name in resources:
            response = self.client.get("/admin-api/%s/" % resource_name, **headers)
            tools.assert_equals(response.status_code, 200)
            resource_list = self.__get_response_json(response)
            tools.assert_true(isinstance(resource_list, list))

            response = self.client.get("/admin-api/%s/schema/" % resource_name, **headers)
            tools.assert_equals(response.status_code, 200)

        self.__logout(headers)

    def test_check_modified_resource_structure(self):
        """
        Meta informations from returned JSON should be removed.
        """
        api_key = self.__login("user", "pass")
        headers = self.__build_headers("user", api_key)

        response = self.client.get("/admin-api/article/", **headers)
        tools.assert_equals(response.status_code, 200)
        resources = self.__get_response_json(response)

        tools.assert_true(isinstance(resources, list))
        for object in resources:
            tools.assert_true(isinstance(object, dict))

        self.__logout(headers)

    def test_url_filed_in_publishables_present(self):
        """
        URL field should be added in every publishable object.
        """
        api_key = self.__login("user", "pass")
        headers = self.__build_headers("user", api_key)

        response = self.client.get("/admin-api/publishable/", **headers)
        resources = self.__get_response_json(response)

        for object in resources:
            tools.assert_true("url" in object)

        # article should inherit every publishable field
        response = self.client.get("/admin-api/article/", **headers)
        resources = self.__get_response_json(response)

        for object in resources:
            tools.assert_true("url" in object)

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
            "HTTP_AUTHORIZATION": "ApiKey %s:%s" % (username, api_key),
        }

    def __get_response_json(self, response):
        return json.loads(response.content)
