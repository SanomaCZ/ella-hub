from django.test import TestCase

from nose import tools
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from ella_hub.api import EllaHubApi


class TestApi(TestCase):
    @tools.raises(ImproperlyConfigured)
    def test_load_fake_resource_module(self):
        original_resources = settings.RESOURCE_MODULES
        settings.RESOURCE_MODULES = ("some_fake_module_name",)

        api = EllaHubApi(api_name='some-api-name')
        try:
            api.collect_resources()
        finally:
            settings.RESOURCE_MODULES = original_resources
