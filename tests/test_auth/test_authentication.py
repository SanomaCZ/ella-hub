#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import unittest
import django.utils.simplejson as json

from nose import tools
from django.test.client import Client
from django.contrib.auth.models import User
from tastypie.models import ApiKey


class TestAuthentication(unittest.TestCase):
    def setUp(self):
        self.user = self.__create_test_user("user", "pass")
        self.client = Client()

    def tearDown(self):
        self.user.delete()

    def __create_test_user(self, username, password, is_admin=False):
        user = User.objects.create_user(username=username, password=password)
        user.is_staff = True
        user.is_superuser = is_admin
        user.save()
        return user

    def test_options_crossdomain_request(self):
        """
        Browser sends OPTIONS request before crossdomain request.
        """
        URLS = (
            "/admin-api/login/",
            "/admin-api/logout/",
            "/admin-api/validate-api-key/",
        )

        for url in URLS:
            request = self.client.options(url)
            tools.assert_equals(request.status_code, 200)

    def test_only_post_requests_allowed(self):
        """
        Only POST requests are allowed for API views.
        """
        URLS = (
            "/admin-api/login/",
            "/admin-api/logout/",
            "/admin-api/validate-api-key/",
        )

        for url in URLS:
            request = self.client.get(url)
            tools.assert_equals(request.status_code, 400)

    def test_unauthorized_when_not_login(self):
        """
        Return "401 Unauthorized" header to anonymous user.
        """
        response = self.client.get("/admin-api/article/")
        tools.assert_equals(response.status_code, 401)

    def test_unauthorized_in_wrong_format(self):
        api_key = self.__login("user", "pass")
        headers = {"HTTP_AUTHORIZATION": "ApiHey %s:%s" % ("user", api_key)}

        response = self.client.get("/admin-api/article/", **headers)
        tools.assert_equals(response.status_code, 401)

        response = self.client.post("/admin-api/logout/", **headers)
        tools.assert_equals(response.status_code, 400)

    def test_unauthorized_for_wrong_api_key(self):
        api_key = self.__login("user", "pass")

        TEST_CASES = (
            # username, API key
            ("use", api_key), # wrong username
            ("user", api_key[:-1]), # wrong API key
            ("pepek", "spinach"), # wrong username and API key
        )

        for username, api_key in TEST_CASES:
            headers = self.__build_headers(username, api_key)
            response = self.client.post("/admin-api/logout/", **headers)
            tools.assert_equals(response.status_code, 401)

    def test_missing_authorization_header(self):
        """
        Return "400 Bad Request" if header with API key is missing.
        """
        for url in ("/admin-api/logout/", "/admin-api/validate-api-key/"):
            response = self.client.post(url)
            tools.assert_equals(response.status_code, 400)

    def test_api_key_validity(self):
        """
        Return information about API key expiration validity.
        """
        api_key = self.__login("user", "pass")

        TEST_CASES = (
            # username, API key, expected validity
            ("user", api_key, True),
            ("use", api_key, False), # wrong username
            ("user", api_key[:-1], False), # wrong API key
            ("pepek", "spinach", False), # wrong username and API key
        )

        for username, api_key, expected in TEST_CASES:
            headers = self.__build_headers(username, api_key)
            response = self.client.post('/admin-api/validate-api-key/', **headers)
            resources = self.__get_response_json(response)

            tools.assert_true("api_key_validity" in resources)
            tools.assert_equals(resources["api_key_validity"],
                expected, "Header pair %s:%s>" % (username, api_key))

    def test_api_key_expiration(self):
        api_key = self.__login("user", "pass")
        headers = self.__build_headers("user", api_key)

        response = self.client.get("/admin-api/article/", **headers)
        tools.assert_equals(response.status_code, 200)

        api_key = ApiKey.objects.get(user=self.user)
        api_key.created = api_key.created - datetime.timedelta(weeks=2)
        api_key.save()

        response = self.client.get("/admin-api/article/", **headers)
        tools.assert_equals(response.status_code, 401)

        self.__logout(headers)

    def test_unauthorized_with_wrong_credentials(self):
        """
        Return "401 Unauthorized" header to user with wrong credetials.
        """
        TEST_CASES = (
            # username, password
            ("pepek", "spinach"), # wrong username and password
            ("use", "pas"), # wrong username and password
            ("use", "pass"), # wrong username
            ("user", "pas"), # wrong password
        )

        for username, password in TEST_CASES:
            response = self.client.post("/admin-api/login/",
                data={"username": username, "password": password})
            tools.assert_equals(response.status_code, 401)

    def test_unauthorized_after_logout(self):
        """
        Return "401 Unauthorized" header to user after logout.
        """
        api_key = self.__login("user", "pass")
        headers = self.__build_headers("user", api_key)

        response = self.client.get("/admin-api/article/", **headers)
        tools.assert_equals(response.status_code, 200)

        self.__logout(headers)

        response = self.client.get("/admin-api/article/", **headers)
        tools.assert_equals(response.status_code, 401)

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
