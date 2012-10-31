from urlparse import urlparse, urlsplit

from nose import tools
from django.test.client import Client, FakePayload, MULTIPART_CONTENT
from django.contrib.auth.models import User
from django.test import TestCase
import django.utils.simplejson as json

from ella.core.models import Author

from ella_hub.utils.test_helpers import create_basic_workflow, delete_basic_workflow
from ella_hub.utils.workflow import set_state, get_state


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



class TestLoginResponse(TestCase):
    def setUp(self):
        self.user = self.__create_test_user("user", "pass", True)
        self.client = PatchClient()
        create_basic_workflow(self)
        self.author = Author.objects.create(id=100, name="Test author",
            slug="1st")
        self.author_two = Author.objects.create(id=101, name="2nd author",
            slug="2nd")

    def tearDown(self):
        self.user.delete()
        self.author.delete()

    def test_set_state_of_two_models(self):
        """
        This shoudn't failed with `MultipleObjectsReturned`.
        """
        api_key = self.__login("user", "pass")
        headers = self.__build_headers("user", api_key)

        self.workflow.set_to_model(Author)
        set_state(self.author, self.state1)
        set_state(self.author_two, self.state1)

        author_patch = json.dumps({
            "state": self.state2.codename
        })

        response = self.client.patch("/admin-api/author/100/", data=author_patch,
            content_type='application/json', **headers)
        tools.assert_equals(response.status_code, 202)
        tools.assert_equals(get_state(self.author), self.state2)

        response = self.client.patch("/admin-api/author/101/", data=author_patch,
            content_type='application/json', **headers)
        tools.assert_equals(response.status_code, 202)
        tools.assert_equals(get_state(self.author_two), self.state2)

        response = self.client.get("/admin-api/author/", **headers)
        tools.assert_equals(response.status_code, 200)

        self.__logout(headers)

    def test_set_state_via_api(self):
        api_key = self.__login("user", "pass")
        headers = self.__build_headers("user", api_key)

        self.workflow.set_to_model(Author)
        set_state(self.author, self.state1)

        author_patch = json.dumps({
            "state": self.state2.codename
        })
        response = self.client.patch("/admin-api/author/100/", data=author_patch,
            content_type='application/json', **headers)
        tools.assert_equals(get_state(self.author), self.state2)

        self.__logout(headers)

    def __create_test_user(self, username, password, is_admin=False):
        user = User.objects.create_user(username=username, password=password)
        user.is_staff = True
        user.is_superuser = is_admin
        user.save()
        return user

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




