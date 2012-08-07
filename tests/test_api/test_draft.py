#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import django.utils.simplejson as json

from nose import tools
from django.test.client import Client
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from ella.core.models import Author
from ella_hub.models import Draft


class TestDraft(unittest.TestCase):
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

    def test_no_drafts(self):
        api_key = self.__login("user", "pass")
        headers = self.__build_headers("user", api_key)

        response = self.client.get("/admin-api/draft/", **headers)
        tools.assert_equals(response.status_code, 200)

        resources = self.__get_response_json(response)
        tools.assert_equals(resources, [])

        self.__logout(headers)

    def test_draft_inserted(self):
        api_key = self.__login("user", "pass")
        headers = self.__build_headers("user", api_key)

        response = self.client.get("/admin-api/draft/", **headers)
        tools.assert_equals(response.status_code, 200)
        resources = self.__get_response_json(response)
        tools.assert_equals(resources, [])

        draft_count = 11
        self.__insert_article_drafts(draft_count)

        response = self.client.get("/admin-api/draft/?limit=%d" % draft_count, **headers)
        tools.assert_equals(response.status_code, 200)
        resources = self.__get_response_json(response)
        tools.assert_equals(len(resources), draft_count)

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
        tools.assert_equals(len(resources), draft_count)

        response = self.client.get(
            "/admin-api/draft/?content_type=author&limit=100", **headers)
        tools.assert_equals(response.status_code, 200)
        resources = self.__get_response_json(response)
        tools.assert_equals(len(resources), 0)

        self.__logout(headers)
        self.__delete_article_drafts()

    def __test_draft_inserted_via_post_method(self):
        api_key = self.__login("user", "pass")
        headers = self.__build_headers("user", api_key)

        response = self.client.post("/admin-api/draft/", **headers)
        tools.assert_equals(response.status_code, 200)
        resources = self.__get_response_json(response)
        tools.assert_equals(len(resources), draft_count)

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

    def __insert_article_drafts(self, count):
        article_content_type = ContentType.objects.get(name__iexact="article")
        self.author = Author.objects.create(user=self.user)

        for i in range(count):
            Draft.objects.create(content_type=article_content_type,
                name="draft_%d" % i , author=self.author,
                data='{id: %d, "field": "value", "another_field": true}' % i)

    def __delete_article_drafts(self):
        self.author.delete()
        Draft.objects.all().delete()
