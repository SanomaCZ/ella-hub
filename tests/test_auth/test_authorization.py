import os
import django.utils.simplejson as json

from PIL import Image
from urlparse import urlparse, urlsplit
from nose import tools, SkipTest
from django.conf import settings
from django.contrib.auth.models import User, Group
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.db import connection
from django.template import RequestContext
from django.test import TestCase
from django.test.client import Client, FakePayload, MULTIPART_CONTENT
from ella.articles.models import Article
from ella.core.models import Author

from ella_hub import utils
from ella_hub.utils import get_all_resource_classes
from ella_hub.utils.workflow import init_ella_workflow, set_state
from ella_hub.utils.perms import grant_permission
from ella_hub.utils.test_helpers import create_basic_workflow, delete_test_workflow
from ella_hub.models import Permission, Role, PrincipalRoleRelation, ModelPermission
from ella_hub.models import Workflow, State, Transition, StateObjectRelation, StatePermissionRelation
from ella_hub.models import WorkflowPermissionRelation


class PatchClient(Client):
    """
    Construct a test client which can do PATCH requests.
    """
    def patch(self, path, data={}, content_type=MULTIPART_CONTENT, **extra):
        patch_data = self._encode_data(data, content_type)
        parsed = urlparse(path)
        r = {
            "CONTENT_LENGTH": len(patch_data),
            "CONTENT_TYPE": content_type,
            "PATH_INFO": self._get_path(parsed),
            "QUERY_STRING": parsed[4],
            "REQUEST_METHOD": "PATCH",
            "wsgi.input": FakePayload(patch_data),
        }
        r.update(extra)
        return self.request(**r)


class TestAuthorization(TestCase):
    def setUp(self):
        self.client = PatchClient()
        create_basic_workflow(self)

        (self.admin_user, self.banned_user, self.role_user) = self.__create_test_users(self.test_role)

        self.article_model_ct = None
        self.photo_filename = self.__create_tmp_image(".test_image.jpg")

        self.new_author = json.dumps({
            "description": "this is descr.",
            "email": "mail@mail.com",
            "id": 100,
            "name": "dumb_name",
            "resource_uri": "/admin-api/author/100/",
            "slug": "dumb-name",
            "text": "this is text",
        })

        self.new_user = json.dumps({
            "email": "user@mail.com",
            "first_name": "test",
            "id": 100,
            "is_staff": True,
            "is_superuser": True,
            "last_name": "user",
            "password": "heslo",
            "resource_uri": "/admin-api/user/100/",
            "username": "test_user",
        })

        self.new_category = json.dumps({
            "content": "this is content",
            "description": "this is a category description",
            "id": 100,
            "resource_uri": "/admin-api/category/100/",
            "site": "/admin-api/site/100/",
            "slug": "category1",
            "template": "category.html",
            "title": "category100",
            "tree_path": "category100",
            "app_data": None,
        })

        self.new_article = json.dumps({
            "authors": [{
                "description": "this is descr.",
                "email": "mail@mail.com",
                "id": 100,
                "name": "dumb_name",
                "resource_uri": "/admin-api/author/100/",
                "slug": "dumb-name",
                "text": "this is text",
            }],
            "category": "/admin-api/category/100/",
            "content": "this is awesome new-article content",
            "description": "this is awesome description",
            "id": 100,
            "publish_from": "2012-08-07T14:51:29",
            "publish_to": "2012-08-15T14:51:35",
            "resource_uri": "/admin-api/article/100/",
            "slug": "test-article",
            "title": "test_article",
            "app_data": None,
        })

        self.new_photo = {
            "title": "photo1",
            "authors": ["/admin-api/author/100/"],
            "image": "attached_object_id:" + os.path.basename(self.photo_filename),
            "id": 100,
            "resource_uri": "/admin-api/photo/100/",
            "description": "this is description",
            "app_data": None,
        }

        self.new_site = json.dumps({
            "domain": "test_domain.com",
            "id": 100,
            "name": "test_domain.com",
            "resource_uri": "/admin-api/site/100/",
        })

        self.new_format = json.dumps({
            "id": 100,
            "resource_uri": "/admin-api/format/100/",
            "flexible_height": False,
            "flexible_max_height": None,
            "max_height": 200,
            "max_width": 200,
            "name": "format_name",
            "nocrop": True,
            "resample_quality": 95,
            "sites": ["/admin-api/site/100/"],
            "stretch": True,
        })

        self.new_formatedphoto = json.dumps({
            "id": 100,
            "resource_uri": "/admin-api/formatedphoto/100/",
            "crop_height": 0,
            "crop_left": 0,
            "crop_top": 0,
            "crop_width": 0,
            "format": "/admin-api/format/100/",
            "height": 200,
            "photo": "/admin-api/photo/100/",
            "width": 200,
        })

        self.new_listing = json.dumps({
            "category": "/admin-api/category/100/",
            "commercial": "false",
            "id": 100,
            "publish_from": "2012-08-07T14:51:29",
            "publish_to": "2012-08-15T14:51:35",
            "resource_uri": "/admin-api/listing/100/",
            "publishable": "/admin-api/article/100/",
        })

    def tearDown(self):
        self.admin_user.delete()
        self.banned_user.delete()
        self.role_user.delete()

        Author.objects.all().delete()
        PrincipalRoleRelation.objects.all().delete()
        StateObjectRelation.objects.all().delete()

        delete_test_workflow()

        os.remove(self.photo_filename)
        connection.close()


    def __create_test_users(self, test_role):
        # Creating admin user.
        admin_user = User.objects.create_user(username="admin_user", password="pass1")
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.save()

        # Create banned user
        banned_user = User.objects.create_user(username="banned_user", password="pass2")
        banned_user.is_staff = False
        banned_user.is_superuser = False
        banned_user.save()

        # Create user with specified role permissions
        user = User.objects.create_user(username="user", password="pass3")
        user.is_staff = True
        user.is_superuser = False
        user.save()
        PrincipalRoleRelation.objects.get_or_create(user=user, role=test_role)

        return (admin_user, banned_user, user)


    def test_role_user_state1_perms(self):
        """
        Testing user permission in state1.
        """
        api_key = self.__login("user", "pass3")
        headers = self.__build_headers("user", api_key)

        test_author = Author.objects.create(id=100, name="dumb_name")

        set_state(test_author, self.state1)

        response = self.client.post("/admin-api/author/", data=self.new_author,
            content_type='application/json', **headers)
        tools.assert_equals(response.status_code, 201)

        response = self.client.get("/admin-api/author/100/", **headers)
        tools.assert_equals(response.status_code, 200)

        response = self.client.put("/admin-api/author/100/", data=self.new_author,
            content_type='application/json', **headers)
        tools.assert_equals(response.status_code, 202)

        response = self.client.patch("/admin-api/author/100/", data=self.new_author,
            content_type='application/json', **headers)
        tools.assert_equals(response.status_code, 202)

        response = self.client.delete("/admin-api/author/100/", **headers)
        tools.assert_equals(response.status_code, 204)

        self.__logout(headers)

    def test_role_user_state2_perms(self):
        """
        Testing user permission in state2.
        """
        api_key = self.__login("user", "pass3")
        headers = self.__build_headers("user", api_key)

        test_author = Author.objects.create(id=100, name="dumb_name")

        set_state(test_author, self.state2)

        response = self.client.post("/admin-api/author/", data=self.new_author,
            content_type='application/json', **headers)
        tools.assert_equals(response.status_code, 201)

        response = self.client.get("/admin-api/author/100/", **headers)
        tools.assert_equals(response.status_code, 200)

        response = self.client.put("/admin-api/author/100/", data=self.new_author,
            content_type='application/json', **headers)
        tools.assert_equals(response.status_code, 202)

        response = self.client.patch("/admin-api/author/100/", data=self.new_author,
            content_type='application/json', **headers)
        tools.assert_equals(response.status_code, 202)

        response = self.client.delete("/admin-api/author/100/", **headers)
        tools.assert_equals(response.status_code, 403)

        self.__logout(headers)

    def test_role_user_state3_perms(self):
        """
        Testing user permission in state3.
        """
        api_key = self.__login("user", "pass3")
        headers = self.__build_headers("user", api_key)

        test_author = Author.objects.create(id=100, name="dumb_name")

        set_state(test_author, self.state3)

        response = self.client.post("/admin-api/author/", data=self.new_author,
            content_type='application/json', **headers)
        tools.assert_equals(response.status_code, 201)

        response = self.client.get("/admin-api/author/100/", **headers)
        tools.assert_equals(response.status_code, 200)

        response = self.client.put("/admin-api/author/100/", data=self.new_author,
            content_type='application/json', **headers)
        tools.assert_equals(response.status_code, 403)

        response = self.client.patch("/admin-api/author/100/", data=self.new_author,
            content_type='application/json', **headers)
        tools.assert_equals(response.status_code, 403)

        response = self.client.delete("/admin-api/author/100/", **headers)
        tools.assert_equals(response.status_code, 403)

        self.__logout(headers)

    def test_top_level_schema_auth(self):
        api_key = self.__login("banned_user", "pass2")
        headers = self.__build_headers("banned_user", api_key)

        response = self.client.get("/admin-api/", **headers)
        tools.assert_equals(response.status_code, 403)

        self.__logout(headers)

        api_key = self.__login("admin_user", "pass1")
        headers = self.__build_headers("admin_user", api_key)

        response = self.client.get("/admin-api/", **headers)
        tools.assert_equals(response.status_code, 200)

        self.__logout(headers)

        api_key = self.__login("user", "pass3")
        headers = self.__build_headers("user", api_key)

        grant_permission(Author, self.test_role, self.can_view)
        response = self.client.get("/admin-api/", **headers)
        resources = self.__get_response_json(response)

        tools.assert_equals(response.status_code, 200)
        tools.assert_true("author" in resources)

        grant_permission(Site, self.test_role, self.can_view)
        response = self.client.get("/admin-api/", **headers)
        resources = self.__get_response_json(response)

        tools.assert_equals(response.status_code, 200)
        tools.assert_true("author" in resources)
        tools.assert_true("site" in resources)

        self.__logout(headers)

    def test_schema_auth(self):
        api_key = self.__login("user", "pass3")
        headers = self.__build_headers("user", api_key)

        ModelPermission.objects.all().delete()
        response = self.client.get("/admin-api/author/schema/", **headers)
        tools.assert_equals(response.status_code, 403)

        grant_permission(Author, self.test_role, self.can_view)
        response = self.client.get("/admin-api/author/schema/", **headers)
        tools.assert_equals(response.status_code, 200)

        self.__logout(headers)

    def test_banned_user_authorization(self):
        """
        Banned user has no permissions.
        """
        api_key = self.__login("admin_user", "pass1")
        headers = self.__build_headers("admin_user", api_key)

        TEST_CASES = (
            ("author", self.new_author),
            ("user", self.new_user),
            ("site", self.new_site),
            ("category", self.new_category),
            ("article", self.new_article),
            ("listing", self.new_listing)
        )

        TEST_PHOTOS_CASES = (
            ("format", self.new_format),
            ("formatedphoto", self.new_formatedphoto)
        )

        for (resource_type, new_resource_obj) in TEST_CASES:
            response = self.client.post("/admin-api/%s/" % resource_type,
                data=new_resource_obj, content_type='application/json', **headers)
            tools.assert_equals(response.status_code, 201)

        payload = {
            "attached_object": open(self.photo_filename),
            "resource_data": json.dumps({
                "objects": [self.new_photo]
            })
        }

        response = self.client.patch("/admin-api/photo/", payload, **headers)
        tools.assert_equals(response.status_code, 202)

        response = self.client.post("/admin-api/format/",
                data=self.new_format, content_type='application/json', **headers)
        tools.assert_equals(response.status_code, 201)

        response = self.client.post("/admin-api/formatedphoto/",
                data=self.new_formatedphoto, content_type='application/json', **headers)
        tools.assert_equals(response.status_code, 201)

        self.__logout(headers)

        api_key = self.__login("banned_user", "pass2")
        headers = self.__build_headers("banned_user", api_key)

        for resource_type, new_resource_obj in TEST_CASES:
            response = self.client.get("/admin-api/%s/100/" % resource_type, **headers)
            tools.assert_equals(response.status_code, 403,
                "status %d for %s: %s" % (response.status_code, resource_type, response.content))

            response = self.client.post("/admin-api/%s/" % resource_type,
                data=new_resource_obj, content_type='application/json', **headers)
            tools.assert_equals(response.status_code, 403,
                "status %d for %s: %s" % (response.status_code, resource_type, response.content))

            response = self.client.put("/admin-api/%s/100/" % resource_type,
                data=new_resource_obj, content_type='application/json', **headers)
            tools.assert_equals(response.status_code, 403,
                "status %d for %s: %s" % (response.status_code, resource_type, response.content))

            response = self.client.patch("/admin-api/%s/100/" % resource_type,
                data=new_resource_obj, content_type='application/json', **headers)
            tools.assert_equals(response.status_code, 403,
                "status %d for %s: %s" % (response.status_code, resource_type, response.content))

            response = self.client.delete("/admin-api/%s/100/" % resource_type, **headers)
            tools.assert_equals(response.status_code, 403,
                "status %d for %s: %s" % (response.status_code, resource_type, response.content))

        response = self.client.patch("/admin-api/photo/", payload, **headers)
        tools.assert_equals(response.status_code, 403)

        TEST_FORMAT_CASES =(
            ("format", self.new_format),
            ("formatedphoto", self.new_formatedphoto)
        )

        for (resource_type, new_resource_obj) in TEST_FORMAT_CASES:
            response = self.client.get("/admin-api/%s/" % resource_type, **headers)
            tools.assert_equals(response.status_code, 403)

            response = self.client.post("/admin-api/%s/" % resource_type,
                data=new_resource_obj, content_type='application/json', **headers)
            tools.assert_equals(response.status_code, 403)

            response = self.client.put("/admin-api/%s/100/" % resource_type,
                data=new_resource_obj, content_type='application/json', **headers)
            tools.assert_equals(response.status_code, 403)

            response = self.client.patch("/admin-api/%s/100/" % resource_type,
                data=new_resource_obj, content_type='application/json', **headers)
            tools.assert_equals(response.status_code, 403)

        self.__logout(headers)

    def test_banned_user_schema_authorization(self):
        """
        User with no permissions has no rights to view
        top level and resource-specific schemas.
        """
        api_key = self.__login("banned_user", "pass2")
        headers = self.__build_headers("banned_user", api_key)

        response = self.client.get("/admin-api/", **headers)
        tools.assert_equals(response.status_code, 403)

        RESOURCES = (
            "author", "user", "site", "category",
            "photo", "article", "listing"
        )

        for res in RESOURCES:
            response = self.client.get("/admin-api/%s/schema/" % res, **headers)
            tools.assert_equals(response.status_code, 403)

        self.__logout(headers)

    def test_admin_user_schema_authorization(self):
        """
        Superuser has access to all registered resources.
        """

        api_key = self.__login("admin_user", "pass1")
        headers = self.__build_headers("admin_user", api_key)

        response = self.client.get("/admin-api/", **headers)
        tools.assert_equals(response.status_code, 200)

        RESOURCES = (
            "author", "user", "site", "category",
            "photo", "listing", "article",
        )

        for res in RESOURCES:
            response = self.client.get("/admin-api/%s/schema/" % res, **headers)
            tools.assert_equals(response.status_code, 200)

        self.__logout(headers)

    def test_admin_user_authorization(self):
        """
        Superuser has all permissions.
        """
        api_key = self.__login("admin_user", "pass1")
        headers = self.__build_headers("admin_user", api_key)

        TEST_CASES = (
            ("author", self.new_author),
            ("user", self.new_user),
            ("site", self.new_site),
            ("category", self.new_category),
            ("article", self.new_article),
            ("listing", self.new_listing)
        )

        for (resource_type, new_resource_obj) in TEST_CASES:
            response = self.client.get("/admin-api/%s/" % resource_type, **headers)
            tools.assert_equals(response.status_code, 200,
                "status %d for resource '%s' with error: %s" % (
                    response.status_code, resource_type, response.content))

            response = self.client.post("/admin-api/%s/" % resource_type,
                data=new_resource_obj, content_type='application/json', **headers)
            tools.assert_equals(response.status_code, 201,
                "status %d for resource '%s' with error: %s" % (
                    response.status_code, resource_type, response.content))

            response = self.client.put("/admin-api/%s/100/" % resource_type,
                data=new_resource_obj, content_type='application/json', **headers)
            tools.assert_equals(response.status_code, 202,
                "status %d for resource '%s' with error: %s" % (
                    response.status_code, resource_type, response.content))

            response = self.client.patch("/admin-api/%s/100/" % resource_type,
                data=new_resource_obj, content_type='application/json', **headers)
            tools.assert_equals(response.status_code, 202,
                "status %d for resource '%s' with error: %s" % (
                    response.status_code, resource_type, response.content))

        response = self.client.get("/admin-api/photo/", **headers)
        tools.assert_equals(response.status_code, 200,
            "code %d with error: %s" % (response.status_code, response.content))

        payload = {
            "attached_object": open(self.photo_filename),
            "resource_data": json.dumps({
                "objects": [self.new_photo]
            })
        }

        response = self.client.patch("/admin-api/photo/", payload, **headers)
        tools.assert_equals(response.status_code, 202)

        TEST_FORMAT_CASES =(
            ("format", self.new_format),
            ("formatedphoto", self.new_formatedphoto)
        )

        for (resource_type, new_resource_obj) in TEST_FORMAT_CASES:
            response = self.client.get("/admin-api/%s/" % resource_type, **headers)
            tools.assert_equals(response.status_code, 200)

            response = self.client.post("/admin-api/%s/" % resource_type,
                data=new_resource_obj, content_type='application/json', **headers)
            tools.assert_equals(response.status_code, 201)

            response = self.client.put("/admin-api/%s/100/" % resource_type,
                data=new_resource_obj, content_type='application/json', **headers)
            tools.assert_true(response.status_code in (201, 202))

            response = self.client.patch("/admin-api/%s/100/" % resource_type,
                data=new_resource_obj, content_type='application/json', **headers)
            tools.assert_equals(response.status_code, 202)

        TEST_CASES = list(TEST_CASES)
        TEST_CASES.reverse()

        for (resource_type, new_resource_obj) in TEST_CASES:
            response = self.client.delete("/admin-api/%s/100/" % resource_type, **headers)
            tools.assert_equals(response.status_code, 204)

        response = self.client.delete("/admin-api/formatedphoto/100/", **headers)
        tools.assert_equals(response.status_code, 204)

        response = self.client.delete("/admin-api/format/100/", **headers)
        tools.assert_equals(response.status_code, 204)

        response = self.client.delete("/admin-api/photo/100/", **headers)
        tools.assert_equals(response.status_code, 204)

        self.__logout(headers)

    def __create_tmp_image(self, filename):
        image = Image.new("RGB", (200, 100), "black")
        if not os.path.exists(settings.MEDIA_ROOT):
            os.makedirs(settings.MEDIA_ROOT)
        image.save(settings.MEDIA_ROOT + "/" + filename, format="jpeg")
        return settings.MEDIA_ROOT + "/" + filename

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
        return json.loads(response.content)
