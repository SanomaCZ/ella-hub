from nose import tools
from django.test import TestCase
from django.utils import simplejson
from django.contrib.auth.models import User

from ella.core.models import Author
from ella.utils import timezone
from ella.utils.test_helpers import create_basic_categories
from ella_taggit.models import PublishableTag, PublishableTaggedItem

from ella_hub.models import CommonArticle
from ella_hub.utils import get_all_resource_classes
from ella_hub.utils.workflow import init_ella_workflow


class TestTag(TestCase):
    def setUp(self):
        init_ella_workflow(get_all_resource_classes())
        self.user = self.__create_test_user("user", "pass", is_admin=True)
        create_basic_categories(self)
        self.article = CommonArticle.objects.create(title="Art title",
            category=self.category, publish_from=timezone.now(), slug="article")

    def tearDown(self):
        self.user.delete()
        Author.objects.all().delete()
        CommonArticle.objects.all().delete()
        PublishableTag.objects.all().delete()
        PublishableTaggedItem.objects.all().delete()

    def test_create_tags(self):
        api_key = self.__login("user", "pass")
        headers = self.__build_headers("user", api_key)

        payload = simplejson.dumps({
            "name": "Tag1",
        })
        response = self.client.post("/admin-api/tag/", payload,
            content_type="application/json", **headers)
        tools.assert_equals(response.status_code, 201)

        payload = simplejson.dumps({
            "name": "Tag2",
            "slug": "slug-for-tag2",
        })
        response = self.client.post("/admin-api/tag/", payload,
            content_type="application/json", **headers)
        tools.assert_equals(response.status_code, 201)

        payload = simplejson.dumps({
            "name": "Tag3",
            "description": "Description of Tag#3",
        })
        response = self.client.post("/admin-api/tag/", payload,
            content_type="application/json", **headers)
        tools.assert_equals(response.status_code, 201)

        response = self.client.get("/admin-api/tag/", **headers)
        resources = self.__get_response_json(response)
        tools.assert_equals(len(resources), 3)
        t1, t2, t3 = resources

        tools.assert_equals(t1["name"], "Tag1")
        tools.assert_equals(t1["slug"], "tag1")
        tools.assert_equals(t1["description"], "")

        tools.assert_equals(t2["name"], "Tag2")
        tools.assert_equals(t2["slug"], "slug-for-tag2")
        tools.assert_equals(t2["description"], "")

        tools.assert_equals(t3["name"], "Tag3")
        tools.assert_equals(t3["slug"], "tag3")
        tools.assert_equals(t3["description"], "Description of Tag#3")

        self.__logout(headers)

    def test_tags_in_publishables(self):
        t1 = PublishableTag.objects.create(name="Tag1")
        t2 = PublishableTag.objects.create(name="Tag2", description="Tag")
        self.article.tags.add(t1, t2)

        api_key = self.__login("user", "pass")
        headers = self.__build_headers("user", api_key)

        for resource in ("publishable", "article"):
            response = self.client.get("/admin-api/%s/" % resource, **headers)
            tools.assert_equals(response.status_code, 200)

            resources = self.__get_response_json(response)
            tools.assert_true(len(resources) > 0)
            tools.assert_in("tags", resources[0])
            tools.assert_equals(len(resources[0]["tags"]), 2)

        self.__logout(headers)

    def test_upload_tags_with_publishable(self):
        t1 = PublishableTag.objects.create(name="Model tag")

        api_key = self.__login("user", "pass")
        headers = self.__build_headers("user", api_key)

        payload = simplejson.dumps({
            "title": "Test article",
            "slug": "test-article",
            "category": "/admin-api/category/%d/" % self.category.id,
            "content": "Content of article",
            "description": "Description of article",
            "publish_from": "2012-08-07T14:51:29",
            "publish_to": "2012-08-15T14:51:35",
            "authors": [{
                "email": "mail@mail.com",
                "description": "this is descr.",
                "name": "Author",
                "slug": "author",
            }],
            "tags": [
                "/admin-api/tag/%d/" % t1.id,
                {
                    "name": "API tag",
                    "description": "API tag description",
                },
            ],
        })
        response = self.client.post("/admin-api/article/", payload,
            content_type="application/json", **headers)
        tools.assert_equals(response.status_code, 201)
        resource = self.__get_response_json(response)
        tools.assert_in("resource_uri", resource)

        response = self.client.get(resource["resource_uri"], **headers)
        tools.assert_equals(response.status_code, 200)
        resource = self.__get_response_json(response)
        tools.assert_in("tags", resource)
        tools.assert_equals(len(resource["tags"]), 2)
        expected_tags = [
            {
                "name": t1.name,
                "slug": t1.slug,
                "description": u"",
            },
            {
                "name": "API tag",
                "slug": "api-tag",
                "description": "API tag description",
            },
        ]

        for expected, returned in zip(expected_tags, resource["tags"]):
            tools.assert_equals(expected["name"], returned["name"])
            tools.assert_equals(expected["slug"], returned["slug"])
            tools.assert_equals(expected["description"], returned["description"])

        self.__logout(headers)

    def test_update_tagged_publishable(self):
        t1 = PublishableTag.objects.create(name="Model tag")

        api_key = self.__login("user", "pass")
        headers = self.__build_headers("user", api_key)

        resource_uri = "/admin-api/article/%d/" % self.article.id
        response = self.client.get(resource_uri, **headers)
        tools.assert_equals(response.status_code, 200)
        resource = self.__get_response_json(response)
        tools.assert_in("tags", resource)
        tools.assert_equals(len(resource["tags"]), 0)

        payload = simplejson.dumps({
            "authors": [{
                "email": "mail@mail.com",
                "description": "this is descr.",
                "name": "Author",
                "slug": "author",
            }],
            "tags": [
                "/admin-api/tag/%d/" % t1.id,
                {
                    "name": "API tag",
                    "description": "API tag description",
                }, {
                    "name": "Tag#2 via API",
                    "slug": "tag-2-api",
                },
            ],
        })
        response = self.client.put(resource_uri, payload,
            content_type="application/json", **headers)
        tools.assert_equals(response.status_code, 202,
            "status %d with error: %s" % (response.status_code, response.content))
        resource = self.__get_response_json(response)
        tools.assert_in("resource_uri", resource)

        response = self.client.get(resource["resource_uri"], **headers)
        tools.assert_equals(response.status_code, 200)
        resource = self.__get_response_json(response)
        tools.assert_in("tags", resource)
        tools.assert_equals(len(resource["tags"]), 3)
        expected_tags = [
            {
                "name": t1.name,
                "slug": t1.slug,
                "description": u"",
            },
            {
                "name": u"API tag",
                "slug": u"api-tag",
                "description": u"API tag description",
            },
            {
                "name": u"Tag#2 via API",
                "slug": u"tag-2-api",
                "description": u"",
            },
        ]

        for expected, returned in zip(expected_tags, resource["tags"]):
            tools.assert_equals(expected["name"], returned["name"])
            tools.assert_equals(expected["slug"], returned["slug"])
            tools.assert_equals(expected["description"], returned["description"])

        self.__logout(headers)

    def test_filter_by_tags(self):
        t1 = PublishableTag.objects.create(name="Tag1")
        t2 = PublishableTag.objects.create(name="Tag2", description="Tag")
        self.article.tags.add(t1, t2)

        api_key = self.__login("user", "pass")
        headers = self.__build_headers("user", api_key)

        url = "/admin-api/tag/related/article/%d;%d/" % (t1.id, t2.id)
        response = self.client.get(url, **headers)
        tools.assert_equals(response.status_code, 200)
        resources = self.__get_response_json(response)

        tools.assert_equals(len(resources), 1, resources)
        tools.assert_equals(resources[0]["id"], self.article.id, resources)

        self.__logout(headers)

    def test_filter_by_tags_with_priority(self):
        """
        Article with more tags should have higher priority.
        """
        article = CommonArticle.objects.create(title="Title non-title",
            category=self.category, publish_from=timezone.now(), slug="non-titled")
        t1 = PublishableTag.objects.create(name="Tag1")
        t2 = PublishableTag.objects.create(name="Tag2", description="Tag")
        article.tags.add(t1, t2)
        self.article.tags.add(t2)

        api_key = self.__login("user", "pass")
        headers = self.__build_headers("user", api_key)

        url = "/admin-api/tag/related/article/%d;%d/" % (t1.id, t2.id)
        response = self.client.get(url, **headers)
        tools.assert_equals(response.status_code, 200)
        resources = self.__get_response_json(response)

        tools.assert_equals(len(resources), 2, resources)
        tools.assert_equals(resources[0]["id"], article.id, resources)
        tools.assert_equals(resources[1]["id"], self.article.id, resources)

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

        return resources["api_key"]

    def __logout(self, headers):
        response = self.client.post('/admin-api/logout/', **headers)
        tools.assert_equals(response.status_code, 302)

    def __build_headers(self, username, api_key):
        return {
            "HTTP_AUTHORIZATION": "ApiKey %s:%s" % (username, api_key),
        }

    def __get_response_json(self, response):
        return simplejson.loads(response.content)
