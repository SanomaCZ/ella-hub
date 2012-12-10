from nose import tools
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
import django.utils.simplejson as json
from django.test import TestCase
from django.test.client import Client

from ella_hub.models import Draft
from ella_hub.utils import get_all_resource_classes
from ella_hub.utils.workflow import init_ella_workflow


class TestDraft(TestCase):
    def setUp(self):
        init_ella_workflow(get_all_resource_classes())
        self.user = self.__create_test_user("user", "pass", True)
        self.client = Client()

    def tearDown(self):
        self.user.delete()

    def __create_test_user(self, username, password, is_admin=False):
        user = User.objects.create_user(username=username, password=password)
        user.is_staff = True
        user.is_superuser = is_admin
        user.save()
        return user

    def test_no_drafts(self):
        api_key = self.__login("user", "pass")
        headers = self.__build_headers("user", api_key)

        response = self.client.get("/admin-api/draft/", **headers)
        tools.assert_equals(response.status_code, 200)

        resources = self.__get_response_json(response)
        tools.assert_equals(resources["objects"], [])

        self.__logout(headers)

    def test_draft_inserted(self):
        api_key = self.__login("user", "pass")
        headers = self.__build_headers("user", api_key)

        response = self.client.get("/admin-api/draft/", **headers)
        tools.assert_equals(response.status_code, 200)
        resources = self.__get_response_json(response)
        tools.assert_equals(resources["objects"], [])

        draft_count = 11
        self.__insert_article_drafts(draft_count)

        response = self.client.get("/admin-api/draft/?limit=%d" % draft_count, **headers)
        tools.assert_equals(response.status_code, 200)
        resources = self.__get_response_json(response)
        tools.assert_equals(len(resources["objects"]), draft_count)

        self.__logout(headers)
        self.__delete_article_drafts()

    def test_filter_draft_via_content_type(self):
        api_key = self.__login("user", "pass")
        headers = self.__build_headers("user", api_key)

        draft_count = 4
        self.__insert_article_drafts(draft_count)

        response = self.client.get(
            "/admin-api/draft/?content_type=article&limit=%d" % draft_count, **headers)
        tools.assert_equals(response.status_code, 200)
        resources = self.__get_response_json(response)
        tools.assert_equals(len(resources["objects"]), draft_count)

        response = self.client.get(
            "/admin-api/draft/?content_type=author&limit=100", **headers)
        tools.assert_equals(response.status_code, 200)
        resources = self.__get_response_json(response)
        tools.assert_equals(len(resources["objects"]), 0)

        self.__logout(headers)
        self.__delete_article_drafts()

    def test_inserted_via_post_method(self):
        api_key = self.__login("user", "pass")
        headers = self.__build_headers("user", api_key)

        data = json.dumps({
            "content_type": "article",
            "data": {"id": 222, "field": "value", "another_field": True},
        })
        response = self.client.post("/admin-api/draft/", data=data,
            content_type="application/json", **headers)
        tools.assert_equals(response.status_code, 201)
        resource = self.__get_response_json(response)

        tools.assert_true(isinstance(resource, dict))
        tools.assert_true("user" in resource)
        tools.assert_true("data" in resource)
        tools.assert_true("name" in resource)

        tools.assert_equals(resource["name"], "")
        tools.assert_equals(type(resource["data"]), dict)
        tools.assert_equals(resource["data"]["id"], 222)
        tools.assert_equals(resource["data"]["field"], "value")
        tools.assert_equals(resource["data"]["another_field"], True)

        self.__logout(headers)

    def test_detail_data_deserialized_and_serialized_as_json(self):
        """
        Data should be properly serialized and stored as JSON in JSONField
        and then properly deserialized into JSON object in response.
        """
        api_key = self.__login("user", "pass")
        headers = self.__build_headers("user", api_key)

        data = json.dumps({
            "content_type": "article",
            "data": {"id": 222, "field": "value", "another_field": True},
        })
        response = self.client.post("/admin-api/draft/", data=data,
            content_type="application/json", **headers)
        tools.assert_equals(response.status_code, 201)
        resource = self.__get_response_json(response)

        tools.assert_true(isinstance(resource, dict))
        tools.assert_true("user" in resource)
        tools.assert_true("data" in resource)
        tools.assert_true("name" in resource)

        tools.assert_equals(resource["name"], "")
        tools.assert_equals(type(resource["data"]), dict)
        tools.assert_equals(resource["data"]["id"], 222)
        tools.assert_equals(resource["data"]["field"], "value")
        tools.assert_equals(resource["data"]["another_field"], True)

        # get detail of draft resource
        response = self.client.get("/admin-api/draft/%d/" % resource["id"], **headers)
        tools.assert_equals(response.status_code, 200)
        resource = self.__get_response_json(response)

        tools.assert_equals(resource["name"], "")
        tools.assert_equals(type(resource["data"]), dict)
        tools.assert_equals(resource["data"]["id"], 222)
        tools.assert_equals(resource["data"]["field"], "value")
        tools.assert_equals(resource["data"]["another_field"], True)

        Draft.objects.all().delete()
        self.__logout(headers)

    def test_list_data_deserialized_and_serialized_as_json(self):
        api_key = self.__login("user", "pass")
        headers = self.__build_headers("user", api_key)

        for id in range(6):
            data = json.dumps({
                "content_type": "article",
                "data": {"id": id, "field": "value", "another_field": True},
            })
            response = self.client.post("/admin-api/draft/", data=data,
                content_type="application/json", **headers)
            tools.assert_equals(response.status_code, 201)

        response = self.client.get("/admin-api/draft/", **headers)
        tools.assert_equals(response.status_code, 200)
        resources = self.__get_response_json(response)

        resources = sorted(resources["objects"], key=lambda i: i["data"]["id"])
        for id, draft in enumerate(resources):
            tools.assert_equals(draft["name"], "")
            tools.assert_equals(type(draft["data"]), dict)
            tools.assert_equals(draft["data"]["id"], id)
            tools.assert_equals(draft["data"]["field"], "value")
            tools.assert_equals(draft["data"]["another_field"], True)

        Draft.objects.all().delete()
        self.__logout(headers)

    def test_draft_data_stored_correctly(self):
        """
        Tests if data in JSONFiled are stored as JSON,
        not as serialized JSON string.
        """

        api_key = self.__login("user", "pass")
        headers = self.__build_headers("user", api_key)

        data = json.dumps({
            "content_type": "article",
            "data": {"id": 222, "field": "value", "another_field": True},
        })
        response = self.client.post("/admin-api/draft/", data=data,
            content_type="application/json", **headers)
        tools.assert_equals(response.status_code, 201)

        article_ct = ContentType.objects.get(app_label="articles", model="article")
        draft = Draft.objects.get(content_type=article_ct, user=self.user)
        tools.assert_equals(draft.content_type, article_ct)
        tools.assert_equals(draft.user, self.user)
        tools.assert_equals(draft.name, "")
        tools.assert_equals(type(draft.data), dict)
        tools.assert_equals(draft.data["id"], 222)
        tools.assert_equals(draft.data["field"], "value")
        tools.assert_equals(draft.data["another_field"], True)

        Draft.objects.all().delete()
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
            "HTTP_CONTENT_TYPE" : "application/json",
        }

    def __get_response_json(self, response):
        return json.loads(response.content)

    def __insert_article_drafts(self, count):
        article_content_type = ContentType.objects.get(app_label="articles",
            model="article")

        for i in range(count):
            Draft.objects.create(content_type=article_content_type,
                name="draft_%d" % i , user=self.user,
                data={"id": i, "field": "value", "another_field": True})

    def __delete_article_drafts(self):
        Draft.objects.all().delete()
