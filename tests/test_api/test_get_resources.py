import django.utils.simplejson as json

from nose import tools
from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User

from ella.articles.models import Article
from ella.utils.test_helpers import create_basic_categories
from ella.utils import timezone

from ella_hub.utils import get_all_resource_classes
from ella_hub.utils.workflow import init_ella_workflow


class TestGetResources(TestCase):
    def setUp(self):
        self.user = self.__create_test_user("user", "pass", True)
        self.client = Client()

        init_ella_workflow(get_all_resource_classes())
        create_basic_categories(self)

        Article.objects.create(title="Jop", slug="jop", category=self.category,
            publish_from=timezone.now())
        Article.objects.create(title="Spinach", category=self.category_nested,
            publish_from=timezone.now(), slug="spinach")
        Article.objects.create(title="Jop3", category=self.category,
            publish_from=timezone.now(), slug="jop3")

    def tearDown(self):
        self.user.delete()
        Article.objects.all().delete()

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

        resource_names = (
            "user",
            "site",
            "article",
            "author",
            "category",
            "photo",
            "formatedphoto",
            "format",
            "listing",
            "publishable",
            "tag",
            "related",
            "position",
        )

        for resource in resource_names:
            tools.assert_true(resource in resources)
            tools.assert_true("list_endpoint" in resources[resource])
            tools.assert_true("schema" in resources[resource])

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
            tools.assert_true(isinstance(resource_list["objects"], list))

            response = self.client.get("/admin-api/%s/schema/" % resource_name, **headers)
            tools.assert_equals(response.status_code, 200)

        self.__logout(headers)

    def test_check_modified_resource_structure(self):
        """
        Meta informations from returned JSON should be present.
        """
        api_key = self.__login("user", "pass")
        headers = self.__build_headers("user", api_key)

        response = self.client.get("/admin-api/article/", **headers)
        tools.assert_equals(response.status_code, 200)
        resources = self.__get_response_json(response)

        tools.assert_true(isinstance(resources, dict))
        tools.assert_in("meta", resources)

        for object in resources["objects"]:
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

        for object in resources["objects"]:
            tools.assert_true("url" in object)

        # article should inherit every publishable field
        response = self.client.get("/admin-api/article/", **headers)
        resources = self.__get_response_json(response)

        for object in resources["objects"]:
            tools.assert_true("url" in object)

        self.__logout(headers)

    def test_category_full_title(self):
        api_key = self.__login("user", "pass")
        headers = self.__build_headers("user", api_key)

        url = "/admin-api/category/%d/" % self.category_nested.id
        response = self.client.get(url, **headers)
        tools.assert_equals(response.status_code, 200)
        resource = self.__get_response_json(response)

        tools.assert_in("full_title", resource)
        expected_title = u"%s > %s" % (self.category.title, self.category_nested.title)
        tools.assert_equals(resource["full_title"], expected_title)

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
