import os
import unittest
from urlparse import urlparse, urlsplit

from PIL import Image
from nose import tools
from django.conf import settings
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.db import connection
from django.template import RequestContext
from django.test.client import Client, FakePayload, MULTIPART_CONTENT
import django.utils.simplejson as json

from ella.articles.models import Article

# TODO: Create object-specific permissions' tests.

class PatchClient(Client):
    """
    Construct a test client which can do PATCH requests.
    """
    def patch(self, path, data={}, content_type=MULTIPART_CONTENT, **extra):
        "Construct a PATCH request."
 
        patch_data = self._encode_data(data, content_type)
 
        parsed = urlparse(path)
        r = {
            'CONTENT_LENGTH': len(patch_data),
            'CONTENT_TYPE':   content_type,
            'PATH_INFO':      self._get_path(parsed),
            'QUERY_STRING':   parsed[4],
            'REQUEST_METHOD': 'PATCH',
            'wsgi.input':     FakePayload(patch_data),
        }
        r.update(extra)
        return self.request(**r)


class TestAuthorization(unittest.TestCase):
    def setUp(self):
        self.client = PatchClient()
        (self.admin_user, self.banned_user, self.user) = self.__create_test_users()
        (self.group1,) = self.__create_test_groups()

        self.articleModel_ct = None

        # Creating temporary image.
        self.photoFileName = ".test_image.jpg"
        image = Image.new('RGB', (200, 100), "black")
        
        if not os.path.exists(settings.MEDIA_ROOT):
            os.makedirs(settings.MEDIA_ROOT)

        image.save(settings.MEDIA_ROOT + "/" + self.photoFileName, format="jpeg")

        self.newAuthor = json.dumps({
            'description':"this is descr.", 
            'email':"mail@mail.com", 
            'id':100, 
            'name':"dumb_name", 
            'resource_uri':"/admin-api/author/100/", 
            'slug':"dumb-name", 
            'text':"this is text"})

        self.newUser = json.dumps({
            'email':"user@mail.com", 
            'first_name': "test",
            "id":100,
            "is_staff": True, 
            "is_superuser":True, 
            "last_name": "user", 
            "password": "heslo", 
            "resource_uri": "/admin-api/user/100/",
            "username":"test_user"})

        self.newCategory = json.dumps({
            "app_data": "{}",
            "content": "this is content",
            "description" : "this is a category description",
            "id":100,
            "resource_uri": "/admin-api/category/100/",
            "site": "/admin-api/site/100/",
            "slug":"category1",
            "template": "category.html",
            "title":"category100",
            "tree_path":"category100"})

        self.newArticle = json.dumps({
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
            "content":"this is awesome new-article content",
            "description":"this is awesome description",
            "id":100,
            "publish_from": "2012-08-07T14:51:29",
            "publish_to": "2012-08-15T14:51:35",
            "resource_uri":"/admin-api/article/100/",
            "slug": "test-article",
            "title":"test_article"})

        self.newPhoto = json.dumps({
            "title":"photo1",
            "image":self.photoFileName,
            "authors":"{}",
            "created": "2012-08-07T14:51:29",
            "id":100,
            "resource_uri":"/admin-api/photo/100/",
            "description":"this is description"
            })

        self.newSite = json.dumps({
            "domain":"test_domain.com",
            "id":100,
            "name": "test_domain.com",
            "resource_uri": "/admin-api/site/100/"
            })

        self.newListing = json.dumps({
            "category": "/admin-api/category/100/",
            "commercial": "false",
            "id": 100,
            "publish_from": "2012-08-07T14:51:29",
            "publish_to": "2012-08-15T14:51:35",
            "resource_uri": "/admin-api/listing/100/",
            "publishable": "/admin-api/article/100/"})

    def tearDown(self):
        self.admin_user.delete()
        self.banned_user.delete()
        self.user.delete()
        self.group1.delete()
        os.remove(settings.MEDIA_ROOT + "/" + self.photoFileName)
        connection.close()

    def __create_test_groups(self):
    	# Group 1 - can handle articles
    	group1 = Group.objects.create(name="group1")
        GROUP1_PERMISSIONS = ("change_author", "add_author", "delete_author")

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

    def test_user_with_specified_permissions(self):
        """
        User has rights only to add, change, delete authors.
        """
        api_key = self.__login("user", "pass3")
        headers = self.__build_headers("user", api_key)

        self.articleModel_ct = ContentType.objects.get(app_label='core', model='author')
        
        PERMS = ("add", "change", "delete")

        for perm in PERMS:
            perm_article = Permission.objects.get(codename="%s_article" % perm)
            self.group1.permissions.add(perm_article)
 
        self.user.groups.add(self.group1)

        # POST
        response = self.client.post("/admin-api/author/", data=self.newAuthor, 
                                    content_type='application/json', **headers)
        tools.assert_equals(response.status_code, 201)
        # GET
        response = self.client.get("/admin-api/author/100/", **headers)
        tools.assert_equals(response.status_code, 200)
        # PUT
        response = self.client.put("/admin-api/author/100/", data=self.newAuthor, 
                                   content_type='application/json', **headers)
        tools.assert_equals(response.status_code, 202)
        # PATCH
        response = self.client.patch("/admin-api/author/100/", data=self.newAuthor, 
                                   content_type='application/json', **headers)
        tools.assert_true(response.status_code, 202)   

        # Can't handle other resources, f.e. site.
        response = self.client.post("/admin-api/site/", data=self.newSite, 
                                    content_type='application/json', **headers)
        tools.assert_equals(response.status_code, 401)
        
        self.__logout(headers)


    def test_banned_user_authorization(self):
        """
        Banned user has no permissions.
        """
        api_key = self.__login("admin_user", "pass1")
        headers = self.__build_headers("admin_user", api_key)

        TEST_CASES = (
            ("author", self.newAuthor),
            ("user", self.newUser),
            ("site", self.newSite),
            ("category", self.newCategory),
            ("photo", self.newPhoto),
            ("article", self.newArticle),
            ("listing", self.newListing)
        )

        for (resourceType, newResourceObj) in TEST_CASES:
            response = self.client.post("/admin-api/%s/" % resourceType, data=newResourceObj, 
                                        content_type='application/json', **headers)
            tools.assert_equals(response.status_code, 201)

        self.__logout(headers)

        api_key = self.__login("banned_user", "pass2")
        headers = self.__build_headers("banned_user", api_key)    

        for (resourceType, newResourceObj) in TEST_CASES:
            # GET
            response = self.client.get("/admin-api/%s/100/" % resourceType, **headers)
            tools.assert_equals(response.status_code, 200)
            # POST
            response = self.client.post("/admin-api/%s/" % resourceType, data=newResourceObj, 
                                        content_type='application/json', **headers)
            tools.assert_equals(response.status_code, 401)
            # PUT
            response = self.client.put("/admin-api/%s/100/" % resourceType, data=newResourceObj, 
                                       content_type='application/json', **headers)
            tools.assert_equals(response.status_code, 403)
            # PATCH
            response = self.client.patch("/admin-api/%s/100/" % resourceType, data=newResourceObj, 
                                       content_type='application/json', **headers)
            tools.assert_true(response.status_code, 403)   
            # DELETE
            response = self.client.delete("/admin-api/%s/100/" % resourceType, **headers)
            tools.assert_equals(response.status_code, 403)           

        self.__logout(headers)

    def test_superuser_authorization(self):
        """
        Superuser has all permissions.
        """

        api_key = self.__login("admin_user", "pass1")
        headers = self.__build_headers("admin_user", api_key)

        TEST_CASES = (
            ("author", self.newAuthor),
            ("user", self.newUser),
            ("site", self.newSite),
            ("category", self.newCategory),
            ("photo", self.newPhoto),
            ("article", self.newArticle),
            ("listing", self.newListing)
        )

        for (resourceType, newResourceObj) in TEST_CASES:
            # GET
            response = self.client.get("/admin-api/%s/" % resourceType, **headers)
            tools.assert_equals(response.status_code, 200)
            # POST
            response = self.client.post("/admin-api/%s/" % resourceType, data=newResourceObj, 
                                        content_type='application/json', **headers)
            tools.assert_equals(response.status_code, 201)
            # PUT
            response = self.client.put("/admin-api/%s/100/" % resourceType, data=newResourceObj, 
                                       content_type='application/json', **headers)
            #tools.assert_true(response.status_code in (201,202))            
            tools.assert_equals(response.status_code, 202)            
            # PATCH
            response = self.client.patch("/admin-api/%s/100/" % resourceType, data=newResourceObj, 
                                       content_type='application/json', **headers)
            tools.assert_true(response.status_code, 202)   
        
        TEST_CASES = list(TEST_CASES)
        TEST_CASES.reverse()    

        for (resourceType, newResourceObj) in TEST_CASES:
            # DELETE
            response = self.client.delete("/admin-api/%s/100/" % resourceType, **headers)
            tools.assert_equals(response.status_code, 204)

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
        return json.loads(response.content)
