import os
import django.utils.simplejson as json

from PIL import Image
from urlparse import urlparse, urlsplit
from nose import tools
from django.conf import settings
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.db import connection
from django.template import RequestContext
from django.test import TestCase
from django.test.client import Client, FakePayload, MULTIPART_CONTENT
from ella.articles.models import Article
from ella.core.models import Author
from ella_hub import utils


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
        self.__register_view_model_permission()

        (self.admin_user, self.banned_user, self.user) = self.__create_test_users()
        (self.group1,) = self.__create_test_groups()

        self.article_model_ct = None

        # Creating temporary image.
        self.photo_filename = self.__create_tmp_image(".test_image.jpg")

        self.new_author = json.dumps({
            "description": "this is descr.",
            "email": "mail@mail.com",
            "id": 100,
            "name": "dumb_name",
            "resource_uri": "/admin-api/author/100/",
            "slug": "dumb-name",
            "text": "this is text"
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
            "username": "test_user"
            })

        self.new_category = json.dumps({
            "app_data": "{}",
            "content": "this is content",
            "description": "this is a category description",
            "id": 100,
            "resource_uri": "/admin-api/category/100/",
            "site": "/admin-api/site/100/",
            "slug": "category1",
            "template": "category.html",
            "title": "category100",
            "tree_path": "category100"
            })

        self.new_article = json.dumps({
            "authors": [
                {
                    "description": "this is descr.",
                    "email": "mail@mail.com",
                    "id": 100,
                    "name": "dumb_name",
                    "resource_uri": "/admin-api/author/100/",
                    "slug": "dumb-name",
                    "text": "this is text"
                }],
            "category": "/admin-api/category/100/",
            "content": "this is awesome new-article content",
            "description": "this is awesome description",
            "id": 100,
            "publish_from": "2012-08-07T14:51:29",
            "publish_to": "2012-08-15T14:51:35",
            "resource_uri": "/admin-api/article/100/",
            "slug": "test-article",
            "title": "test_article"
            })

        self.new_photo = json.dumps({
            "title": "photo1",
            "image": self.photo_filename,
            "authors": ["/admin-api/author/100/"],
            "created": "2012-08-07T14:51:29",
            "id": 100,
            "resource_uri": "/admin-api/photo/100/",
            "description": "this is description"
            })

        self.new_site = json.dumps({
            "domain": "test_domain.com",
            "id": 100,
            "name": "test_domain.com",
            "resource_uri": "/admin-api/site/100/"
            })

        self.new_format = json.dumps({
            "flexible_height": False,
            "flexible_max_height": None,
            "max_height": 200,
            "max_width": 200,
            "name": "format_name",
            "nocrop": True,
            "resample_quality": 95,
            "sites": [
                {
                    "domain": "test_domain.com",
                    "id": 100,
                    "name": "test_domain.com",
                    "resource_uri": "/admin-api/site/100/"
                }],
            "stretch": True
            })

        self.new_formatedphoto = json.dumps({
            "resource_uri": "/admin-api/formatedphoto/100/",
            "crop_height": 0,
            "crop_left": 0,
            "crop_top": 0,
            "crop_width": 0,
            "id": 100,
            "format": "/admin-api/format/1/",
            "height": 200,
            "photo": "/admin-api/photo/100/",
            "width": 200
            })

        self.new_listing = json.dumps({
            "category": "/admin-api/category/100/",
            "commercial": "false",
            "id": 100,
            "publish_from": "2012-08-07T14:51:29",
            "publish_to": "2012-08-15T14:51:35",
            "resource_uri": "/admin-api/listing/100/",
            "publishable": "/admin-api/article/100/"
            })

    def tearDown(self):
        self.admin_user.delete()
        self.banned_user.delete()
        self.user.delete()
        self.group1.delete()
        os.remove(self.photo_filename)
        connection.close()

    def __create_test_groups(self):
        # Group 1 - can handle articles
        group1 = Group.objects.create(name="group1")
        GROUP1_PERMISSIONS = ("view_author", "change_author",
                              "add_author", "delete_author")

        for perm in GROUP1_PERMISSIONS:
            group1.permissions.add(Permission.objects.get(codename=perm))
        group1.save()
        return (group1,)

    def __create_test_users(self):
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

        # Create user with specified permissions
        user = User.objects.create_user(username="user", password="pass3")
        user.is_staff = True
        user.is_superuser = False
        user.save()
        return (admin_user, banned_user, user)

    def test_registered_object_level_permissions(self):
        """
        Proper user authorization based on new
        object level permissions.
        """
        # perms are registered in __init__.py file
        api_key = self.__login("user", "pass3")
        headers = self.__build_headers("user", api_key)

        # grant only change permission to author object
        changable_author = Author(name="awesome_name", slug="awesome-name",
            email="mail@mail.com", text="like a boss", description="what can i say", id=100)
        changable_author.save()
        self.user.grant('change_author', changable_author)

        # grant only view permission to author object
        viewable_author = Author(name="viewable_name", slug="viewable-name",
            email="mailik@m.com", text="this is text", description="what should i say", id=101)
        viewable_author.save()
        self.user.grant('view_author', viewable_author)


        # User can change changable_author,
        response = self.client.put("/admin-api/author/100/", data=self.new_author,
            content_type='application/json', **headers)
        tools.assert_equals(response.status_code, 202)

        # but can't change viewable_author
        response = self.client.put("/admin-api/author/101/",
            data=json.dumps({'email':"mail@mail.com"}), content_type='application/json', **headers)
        tools.assert_equals(response.status_code, 403)

        # can't delete these objects also
        response = self.client.delete("/admin-api/author/100/", **headers)
        tools.assert_equals(response.status_code, 403)
        response = self.client.delete("/admin-api/author/101/", **headers)
        tools.assert_equals(response.status_code, 403)

        # can get only viewable_author
        response = self.client.get("/admin-api/author/", **headers)
        tools.assert_equals(response.status_code, 200)

        resources = self.__get_response_json(response)
        tools.assert_equals(len(resources), 1)

        self.__logout(headers)

    def test_delete_and_patch_obj_attributes(self):
        """
        """
        api_key = self.__login("user", "pass3")
        headers = self.__build_headers("user", api_key)

        author = Author(name="viewable_name", slug="viewable-name", email="mailik@m.com",
                                 text="this is text", description="what should i say", id=101)
        author.save()
        self.user.grant('view_author', author)

        response = self.client.get("/admin-api/author/101/", **headers)
        resource = self.__get_response_json(response)
        tools.assert_equals(resource['_delete'], False)
        tools.assert_equals(resource['_patch'], False)

        self.user.grant('change_author', author)
        response = self.client.get("/admin-api/author/101/", **headers)
        resource = self.__get_response_json(response)
        tools.assert_equals(resource['_delete'], False)
        tools.assert_equals(resource['_patch'], True)

        self.user.grant('delete_author', author)
        response = self.client.get("/admin-api/author/101/", **headers)
        resource = self.__get_response_json(response)
        tools.assert_equals(resource['_delete'], True)
        tools.assert_equals(resource['_patch'], True)

        self.__logout(headers)

    def test_registered_model_level_permissions(self):
        """
        Proper user authorization based on new
        model level permission.
        """
        api_key = self.__login("user", "pass3")
        headers = self.__build_headers("user", api_key)

        # create some model-level permissions
        author_ct = ContentType.objects.get(app_label='core', model='author')

        PERM_PREFIXES = ('view_',)

        author = Author.objects.create(id=200, name="author200", email="200@e.mail")
        author.save()

        # delete perms if registered
        for PREFIX in PERM_PREFIXES:
            matching_query = Permission.objects.filter(codename="%sauthor" % PREFIX,
                content_type=author_ct)
            if matching_query:
                matching_query.delete()

        response = self.client.get("/admin-api/author/", **headers)
        tools.assert_equals(response.status_code, 403)

        response = self.client.get("/admin-api/author/200/", **headers)
        tools.assert_equals(response.status_code, 403)

        for PREFIX in PERM_PREFIXES:
            author_perm = Permission(codename="%sauthor" % PREFIX, name="%s author" % PREFIX,
                content_type=author_ct)
            author_perm.save()
            # grant permission
            self.user.user_permissions.add(author_perm)

        response = self.client.get("/admin-api/author/", **headers)
        tools.assert_equals(response.status_code, 200)

        response = self.client.get("/admin-api/author/200/", **headers)
        tools.assert_equals(response.status_code, 200)

        self.__logout(headers)

    def test_user_with_specified_permissions(self):
        """
        User has rights only to add, change, delete authors.
        """
        api_key = self.__login("user", "pass3")
        headers = self.__build_headers("user", api_key)

        self.article_model_ct = ContentType.objects.get(app_label='core', model='author')

        PERMS = ("view", "add", "change", "delete")

        for perm in PERMS:
            perm_author = Permission.objects.get(codename="%s_author" % perm)
            self.group1.permissions.add(perm_author)

        self.user.groups.add(self.group1)

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
        tools.assert_true(response.status_code, 202)

        # Can't handle other resources, f.e. site.
        response = self.client.post("/admin-api/site/", data=self.new_site,
                                    content_type='application/json', **headers)
        tools.assert_equals(response.status_code, 403)

        self.__logout(headers)

    def test_user_with_specified_perms_schema(self):
        """
        Check if author who can only view, add, change and delete authors,
        can view only author resource.
        """
        PERMS = ("view", "add", "change", "delete")

        for perm in PERMS:
            perm_article = Permission.objects.get(codename="%s_author" % perm)
            self.group1.permissions.add(perm_article)
        self.user.groups.add(self.group1)

        api_key = self.__login("user", "pass3")
        headers = self.__build_headers("user", api_key)

        response = self.client.get("/admin-api/", **headers)
        tools.assert_equals(response.status_code, 200)

        resources = self.__get_response_json(response)
        tools.assert_equals(len(resources), 1)

        tools.assert_true("author" in resources)
        tools.assert_true("list_endpoint" in resources["author"])
        tools.assert_true("schema" in resources["author"])

        self.__logout(headers)

    def test_user_schema_with_specified_obj_permissions(self):
        """
        """
        api_key = self.__login("user", "pass3")
        headers = self.__build_headers("user", api_key)

        author = Author(name="dumb_name", slug="dumb-name", email="mail@mail.com",
                   text="dasdasd", description="dsadasd", id=100)
        author.save()

        PERMISSIONS = ("view_author", "change_author", "delete_author")
        for PERM in PERMISSIONS:
            self.user.revoke_all(author)
            response = self.client.get("/admin-api/", **headers)
            tools.assert_equals(response.status_code, 403)

            self.user.grant(PERM, author)

            response = self.client.get("/admin-api/", **headers)
            tools.assert_equals(response.status_code, 200)

            resources = self.__get_response_json(response)
            tools.assert_equals(len(resources), 1)

            tools.assert_true("author" in resources)
            tools.assert_true("list_endpoint" in resources["author"])
            tools.assert_true("schema" in resources["author"])

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
            ("photo", self.new_photo),
            # TODO: can't add format objects with custom ID
            #("format", self.new_format),
            #("formatedphoto", self.new_formatedphoto),
            ("article", self.new_article),
            ("listing", self.new_listing)
        )

        for (resource_type, new_resource_obj) in TEST_CASES:
            response = self.client.post("/admin-api/%s/" % resource_type,
                data=new_resource_obj, content_type='application/json', **headers)
            tools.assert_equals(response.status_code, 201)

        self.__logout(headers)

        api_key = self.__login("banned_user", "pass2")
        headers = self.__build_headers("banned_user", api_key)

        for (resource_type, new_resource_obj) in TEST_CASES:
            response = self.client.get("/admin-api/%s/100/" % resource_type, **headers)
            tools.assert_equals(response.status_code, 403)

            response = self.client.post("/admin-api/%s/" % resource_type,
                data=new_resource_obj, content_type='application/json', **headers)
            tools.assert_equals(response.status_code, 403)

            response = self.client.put("/admin-api/%s/100/" % resource_type,
                data=new_resource_obj, content_type='application/json', **headers)
            tools.assert_equals(response.status_code, 403)

            response = self.client.patch("/admin-api/%s/100/" % resource_type,
                data=new_resource_obj, content_type='application/json', **headers)
            tools.assert_true(response.status_code, 403)

            response = self.client.delete("/admin-api/%s/100/" % resource_type, **headers)
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

        RESOURCES = ("author", "user", "site", "category",
                     "photo", "article", "listing")

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

        RESOURCES = ("author", "user", "site", "category",
                     "photo", "listing", "article",
                     #"commonarticle", "encyclopedia", "recipe", "pagedarticle",
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
            ("photo", self.new_photo),
            ("article", self.new_article),
            ("listing", self.new_listing)
        )

        for (resource_type, new_resource_obj) in TEST_CASES:
            response = self.client.get("/admin-api/%s/" % resource_type, **headers)
            tools.assert_equals(response.status_code, 200)

            response = self.client.post("/admin-api/%s/" % resource_type,
                data=new_resource_obj, content_type='application/json', **headers)
            tools.assert_equals(response.status_code, 201)

            response = self.client.put("/admin-api/%s/100/" % resource_type,
                data=new_resource_obj, content_type='application/json', **headers)
            tools.assert_equals(response.status_code, 202)

            response = self.client.patch("/admin-api/%s/100/" % resource_type,
                data=new_resource_obj, content_type='application/json', **headers)
            tools.assert_true(response.status_code, 202)

        TEST_CASES = list(TEST_CASES)
        TEST_CASES.reverse()

        for (resource_type, new_resource_obj) in TEST_CASES:
            response = self.client.delete("/admin-api/%s/100/" % resource_type, **headers)
            tools.assert_equals(response.status_code, 204)

        self.__logout(headers)

    def __create_tmp_image(self, filename):
        image = Image.new("RGB", (200, 100), "black")
        if not os.path.exists(settings.MEDIA_ROOT):
            os.makedirs(settings.MEDIA_ROOT)
        image.save(settings.MEDIA_ROOT + "/" + filename, format="jpeg")
        return settings.MEDIA_ROOT + "/" + filename

    def __register_view_model_permission(self):
        for model_name in utils.get_all_resource_model_names():
            ct = ContentType.objects.get(model=model_name)

            perm = Permission.objects.get_or_create(codename='view_%s' % model_name,
                name='Can view %s.' % model_name, content_type=ct)
            if not isinstance(perm, tuple):
                perm.save()

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
