import unittest

from nose import tools
from django.contrib.auth.models import User, AnonymousUser
from django.test.client import RequestFactory
from django.conf import settings
from tastypie.models import ApiKey

from ella_hub.utils.middleware import CrossDomainAccessMiddleware, AuthenticationMiddleware


class DummyResponse(dict):
    pass


class TestCrossDomainAccessMiddleware(unittest.TestCase):
    def setUp(self):
        self.request_factory = RequestFactory()
        self.middleware = CrossDomainAccessMiddleware()

    def test_default_headers_properly_set(self):
        request = self.request_factory.get("/admin-api/")
        response = DummyResponse()
        response = self.middleware.process_response(request, response)

        tools.assert_true("Access-Control-Allow-Origin" in response)
        tools.assert_equals(response["Access-Control-Allow-Origin"], "*")

        tools.assert_true("Access-Control-Allow-Methods" in response)
        tools.assert_equals(response["Access-Control-Allow-Methods"], "POST,GET,OPTIONS,PUT,PATCH,DELETE")

        tools.assert_true("Access-Control-Allow-Headers" in response)
        tools.assert_equals(response["Access-Control-Allow-Headers"], "Content-Type,X-Requested-With,Authorization")

        tools.assert_true("Access-Control-Allow-Credentials" in response)
        tools.assert_equals(response["Access-Control-Allow-Credentials"], "true")

    def test_own_headers_properly_set(self):
        request = self.request_factory.get("/admin-api/")
        response = DummyResponse()

        settings.XS_SHARING_ALLOWED_METHODS = ("GET", "POST")
        settings.XS_SHARING_ALLOWED_CREDENTIALS = "false"
        response = self.middleware.process_response(request, response)

        tools.assert_true("Access-Control-Allow-Origin" in response)
        tools.assert_equals(response["Access-Control-Allow-Origin"], "*")

        tools.assert_true("Access-Control-Allow-Methods" in response)
        tools.assert_equals(response["Access-Control-Allow-Methods"], "GET,POST")

        tools.assert_true("Access-Control-Allow-Headers" in response)
        tools.assert_equals(response["Access-Control-Allow-Headers"], "Content-Type,X-Requested-With,Authorization")

        tools.assert_true("Access-Control-Allow-Credentials" in response)
        tools.assert_equals(response["Access-Control-Allow-Credentials"], "false")

        del settings.XS_SHARING_ALLOWED_METHODS
        del settings.XS_SHARING_ALLOWED_CREDENTIALS

    def test_set_multivalue_header_with_single_value(self):
        request = self.request_factory.get("/admin-api/")
        response = DummyResponse()

        settings.XS_SHARING_ALLOWED_METHODS = "GET"
        response = self.middleware.process_response(request, response)

        tools.assert_true("Access-Control-Allow-Methods" in response)
        tools.assert_equals(response["Access-Control-Allow-Methods"], "GET")

        del settings.XS_SHARING_ALLOWED_METHODS


class TestAuthenticationMiddleware(unittest.TestCase):
    def setUp(self):
        self.request_factory = RequestFactory()
        self.middleware = AuthenticationMiddleware()
        self.user = User.objects.create_user("user", "pass")

    def tearDown(self):
        self.user.delete()

    def test_right_credentials(self):
        api_key = ApiKey.objects.get(user=self.user)
        request = self.request_factory.get("/admin-api/login/",
            HTTP_AUTHORIZATION="ApiKey user:" + api_key.key)

        response = self.middleware.process_request(request)
        tools.assert_equals(response, None)
        tools.assert_is_instance(request.user, User)
        tools.assert_true(request.user.is_authenticated())

    def test_header_in_wrong_format(self):
        api_key = ApiKey.objects.get(user=self.user)
        request = self.request_factory.get("/admin-api/login/",
            HTTP_AUTHORIZATION="ApiKey user#" + api_key.key)

        response = self.middleware.process_request(request)
        tools.assert_equals(response, None)
        tools.assert_is_instance(request.user, AnonymousUser)
