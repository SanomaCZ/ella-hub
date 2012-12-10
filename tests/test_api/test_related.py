import django.utils.simplejson as json

from nose import tools
from django.test import TestCase
from django.contrib.auth.models import User

from ella.core.models import Related
from ella.articles.models import Article
from ella.utils.test_helpers import create_basic_categories
from ella.utils import timezone


class TestRelated(TestCase):
    def setUp(self):
        self.user = self.__create_test_user("user", "pass", True)

        create_basic_categories(self)

        self.article = Article.objects.create(title="Jop", slug="jop",
            category=self.category, publish_from=timezone.now())
        self.recipe = Article.objects.create(title="Spinach", slug="spinach",
            category=self.category_nested, publish_from=timezone.now())
        self.encyclopedia = Article.objects.create(title="Enc", slug="enc",
            category=self.category, publish_from=timezone.now())

    def tearDown(self):
        self.user.delete()
        Article.objects.all().delete()

    def __create_test_user(self, username, password, is_admin=False):
        user = User.objects.create_user(username=username, password=password)
        user.is_staff = True
        user.is_superuser = is_admin
        user.save()
        return user

    def test_related_resource_created(self):
        api_key = self.__login("user", "pass")
        headers = self.__build_headers("user", api_key)

        related = Related.objects.create(publishable=self.article,
            related=self.recipe)

        response = self.client.get("/admin-api/related/", **headers)
        tools.assert_equals(response.status_code, 200)
        resources = self.__get_response_json(response)

        tools.assert_equals(len(resources["objects"]), 1)

        related.delete()
        self.__logout(headers)

    def test_create_related_resource(self):
        api_key = self.__login("user", "pass")
        headers = self.__build_headers("user", api_key)

        payload = json.dumps({
            "publishable": "/admin-api/article/%d/" % self.article.id,
            "related": "/admin-api/article/%d/" % self.recipe.id,
        })
        response = self.client.post("/admin-api/related/", payload,
            content_type="application/json", **headers)
        tools.assert_equals(response.status_code, 201, response.content)
        resources = self.__get_response_json(response)

        Related.objects.get(id=resources["id"]).delete()

        self.__logout(headers)

    def __login(self, username, password):
        response = self.client.post('/admin-api/login/',
            data={"username": username, "password": password})
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
