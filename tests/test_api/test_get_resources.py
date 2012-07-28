#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import django.utils.simplejson as json

from nose import tools
from django.test.client import Client
from ella.utils.test_helpers import create_basic_categories, create_and_place_a_publishable


class TestGetResources(unittest.TestCase):
    def setUp(self):
        self.client = Client()
        create_basic_categories(self)
        create_and_place_a_publishable(self)

    def test_ella_resources_present(self):
        response = self.client.get("/admin-api/")
        resources = self.__get_response_json(response)

        tools.assert_true("user" in resources)
        tools.assert_true("list_endpoint" in resources["user"])
        tools.assert_true("schema" in resources["user"])

        tools.assert_true("article" in resources)
        tools.assert_true("list_endpoint" in resources["article"])
        tools.assert_true("schema" in resources["article"])

        tools.assert_true("author" in resources)
        tools.assert_true("list_endpoint" in resources["author"])
        tools.assert_true("schema" in resources["author"])

        tools.assert_true("category" in resources)
        tools.assert_true("list_endpoint" in resources["category"])
        tools.assert_true("schema" in resources["category"])

        tools.assert_true("photo" in resources)
        tools.assert_true("list_endpoint" in resources["photo"])
        tools.assert_true("schema" in resources["photo"])

        tools.assert_true("listing" in resources)
        tools.assert_true("list_endpoint" in resources["listing"])
        tools.assert_true("schema" in resources["listing"])

        tools.assert_true("publishable" in resources)
        tools.assert_true("list_endpoint" in resources["publishable"])
        tools.assert_true("schema" in resources["publishable"])

    def test_check_modified_resource_structure(self):
        """
        Meta informations from returned JSON should be removed.
        """
        response = self.client.get("/admin-api/article/")
        resources = self.__get_response_json(response)

        tools.assert_true(isinstance(resources, list))
        for object in resources:
            tools.assert_true(isinstance(object, dict))

    def test_url_filed_in_publishables_present(self):
        """
        URL field should be added in every publishable object.
        """
        response = self.client.get("/admin-api/publishable/")
        resources = self.__get_response_json(response)

        for object in resources:
            tools.assert_true("url" in object)

        # article should inherit every publishable field
        response = self.client.get("/admin-api/article/")
        resources = self.__get_response_json(response)

        for object in resources:
            tools.assert_true("url" in object)

    def __get_response_json(self, response):
        return json.loads(response.content)
