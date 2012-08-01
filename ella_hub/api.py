import ella_hub.views

from inspect import isclass

from django.conf import settings
from django.utils.importlib import import_module
from django.core.exceptions import ImproperlyConfigured
from django.conf.urls.defaults import url

from tastypie.resources import Resource, ModelResource
from tastypie.api import Api

from ella_hub.resources import ApiModelResource


class EllaHubApi(Api):
    """
    """

    def collect_resources(self):
        resource_modules = []

        # get resources from installed apps first
        for app in settings.INSTALLED_APPS:
            try:
                mod = import_module('%s.api_resources' % app)
                resource_modules.append(mod)
            except ImportError:
                pass

        # get resources from user defined modules
        for module in getattr(settings, 'RESOURCE_MODULES', ()):
            try:
                mod = import_module(module)
            except ImportError, e:
                raise ImproperlyConfigured(
                    'Error importing resource module %s,'
                    'check RESOURCE_MODULES '
                    'in your settings: "%s"' % (module, e))
            else:
                for attr in mod.__dict__:
                    resource = getattr(mod, attr)
                    if isclass(resource) and issubclass(resource, Resource) \
                            and resource not in (Resource, ModelResource, ApiModelResource):
                        resource_modules.append(resource)

        return resource_modules

    def register_resources(self, resources):
        "Register one or more resources"

        for one in resources:
            self.register(one())

    def override_urls(self):
        """
        Prepend given URL patterns to all API.

        This method is deprecated in repo and should be replaced by
        `prepend_urls` method in v1.0.
        """
        return [
            url(r"^(?P<api_name>)%s/login/$" % self.api_name, ella_hub.views.login_view),
            url(r"^(?P<api_name>)%s/logout/$" % self.api_name, ella_hub.views.logout_view),
        ]
