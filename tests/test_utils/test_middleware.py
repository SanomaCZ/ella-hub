from nose import tools
from django.conf import settings
from django.contrib.auth.models import User, AnonymousUser
from django.test.client import RequestFactory
from django.test import TestCase
from tastypie.models import ApiKey
from ella_hub.utils.middleware import CrossDomainAccessMiddleware


class DummyResponse(dict):
    pass


class TestCrossDomainAccessMiddleware(TestCase):
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
        tools.assert_equals(response["Access-Control-Allow-Methods"],
            "POST,GET,OPTIONS,PUT,PATCH,DELETE")

        tools.assert_true("Access-Control-Allow-Headers" in response)
        tools.assert_equals(response["Access-Control-Allow-Headers"],
            "Content-Type,X-Requested-With,Authorization,X-Mime-Type,X-File-Name")

        tools.assert_true("Access-Control-Allow-Credentials" in response)
        tools.assert_equals(response["Access-Control-Allow-Credentials"], "true")

    def test_origin_set_to_origin_url(self):
        request = self.request_factory.get("/admin-api/", HTTP_ORIGIN="http://origin.org/")
        response = DummyResponse()
        response = self.middleware.process_response(request, response)

        tools.assert_true("Access-Control-Allow-Origin" in response)
        tools.assert_equals(response["Access-Control-Allow-Origin"], "http://origin.org/")

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
        tools.assert_equals(response["Access-Control-Allow-Headers"],
            "Content-Type,X-Requested-With,Authorization,X-Mime-Type,X-File-Name")

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
