#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

from nose import tools
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from ella_hub.api import EllaHubApi


class TestApi(unittest.TestCase):
    def test_load_fake_resource_module(self):
        original_resources = settings.RESOURCE_MODULES
        settings.RESOURCE_MODULES = ("some_fake_module_name",)

        api = EllaHubApi(api_name='some-api-name')
        try:
            api.collect_resources()
        except ImproperlyConfigured:
            pass
        finally:
            settings.RESOURCE_MODULES = original_resources
