from nose import tools
from django.utils import simplejson
from django.contrib.auth.models import User
from django.test import TestCase
from django.test.client import Client
from ella.utils import timezone
from ella.articles.models import Article
from ella.positions.models import Position
from ella.utils.test_helpers import create_basic_categories


class TestPosition(TestCase):
    def setUp(self):
        self.user = self.__create_test_user("user", "pass", True)
        self.client = Client()
        create_basic_categories(self)

    def tearDown(self):
        self.user.delete()

    def __create_test_user(self, username, password, is_admin=False):
        user = User.objects.create_user(username=username, password=password)
        user.is_staff = True
        user.is_superuser = is_admin
        user.save()
        return user

    def test_get_position(self):
        api_key = self.__login("user", "pass")
        headers = self.__build_headers("user", api_key)

        article = Article.objects.create(title="Article", slug="article",
            category=self.category, publish_from=timezone.now())
        position = Position.objects.create(name="Position",
            category=self.category, target=article)

        response = self.client.get("/admin-api/position/",
            content_type="application/json", **headers)
        tools.assert_equals(response.status_code, 200)
        resources = self.__get_response_json(response)

        tools.assert_equals(len(resources["objects"]), 1)
        tools.assert_is_instance(resources["objects"][0]["target"], dict)

        target = resources["objects"][0]["target"]
        tools.assert_equals(target["title"], "Article")
        tools.assert_equals(target["slug"], "article")
        tools.assert_is_instance(target["category"], dict)

        position.delete()
        article.delete()
        self.__logout(headers)

    def test_create_article_position(self):
        api_key = self.__login("user", "pass")
        headers = self.__build_headers("user", api_key)

        article = Article.objects.create(title="Article", slug="article",
            category=self.category, publish_from=timezone.now())
        payload = simplejson.dumps({
            "name": "Position",
            "category": "/admin-api/category/%d/" % self.category.id,
            "target": "/admin-api/article/%d/" % article.id,
        })
        response = self.client.post("/admin-api/position/", payload,
            content_type="application/json", **headers)
        tools.assert_equals(response.status_code, 201)

        article.delete()
        self.__logout(headers)

    def test_update_position(self):
        api_key = self.__login("user", "pass")
        headers = self.__build_headers("user", api_key)

        article = Article.objects.create(title="Article", slug="article",
            category=self.category, publish_from=timezone.now())
        recipe = Article.objects.create(title="Spinach", slug="spinach",
            category=self.category, publish_from=timezone.now())
        position = Position.objects.create(name="Position",
            category=self.category, target=article)

        payload = simplejson.dumps({
            "name": "Updated name :)",
            "category": "/admin-api/category/%d/" % self.category_nested.id,
            "target": "/admin-api/article/%d/" % recipe.id,
        })
        response = self.client.put("/admin-api/position/%d/" % position.id,
            payload, content_type="application/json", **headers)
        tools.assert_equals(response.status_code, 202)

        position = Position.objects.get(pk=position.pk)
        tools.assert_equals(position.name, "Updated name :)")
        tools.assert_equals(position.category, self.category_nested)
        tools.assert_equals(position.target, recipe)

        position.delete()
        article.delete()
        recipe.delete()
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
            "HTTP_AUTHORIZATION" : "ApiKey %s:%s" % (username, api_key),
        }

    def __get_response_json(self, response):
        return simplejson.loads(response.content)
