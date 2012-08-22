import re
import ella_hub.views
import datetime

from inspect import isclass

from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.utils.importlib import import_module
from django.utils import simplejson
from django.core.exceptions import ImproperlyConfigured
from django.conf.urls.defaults import url
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db import models
from tastypie.api import Api
from tastypie.resources import Resource, ModelResource
from tastypie.models import ApiKey
from tastypie.models import create_api_key

from ella_hub.utils import timezone
from ella_hub.decorators import cross_domain_api_post_view
from ella_hub.resources import ApiModelResource

# generate API key for new user
models.signals.post_save.connect(create_api_key, sender=User)


class HttpResponseUnauthorized(HttpResponse):
    def __init__(self):
        super(HttpResponseUnauthorized, self).__init__(status=401)


class EllaHubApi(Api):
    """
    """

    registered_resources = {}

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

        for resource_class in resources:
            resource = resource_class()
            EllaHubApi.registered_resources[resource._meta.resource_name] = resource
            self.register(resource)

    def prepend_urls(self):
        """
        Prepend given URL patterns to all API.
        """
        return [
            url(r"^%s/login/$" % self.api_name, self.wrap_view('login_view')),
            url(r"^(?P<api_name>%s)/logout/$" % self.api_name, self.wrap_view('logout_view')),
            url(r"^%s/validate-api-key/$" % self.api_name, self.wrap_view('validate_api_key_view'))
        ]

    def wrap_view(self, view):
        wrapped_view = super(EllaHubApi, self).wrap_view(view)
        return csrf_exempt(wrapped_view)

    @cross_domain_api_post_view
    def login_view(self, request):
        username = request.POST.get("username", "")
        password = request.POST.get("password", "")
        user = authenticate(username=username, password=password)

        if user is not None and user.is_active:
            try:
                api_key = ApiKey.objects.get(user=user)
            except ApiKey.DoesNotExist:
                api_key = ApiKey.objects.create(user=user)

            login(request, user)
            return HttpResponse(simplejson.dumps({
                "api_key": self.__regenerate_key(api_key),
            }))
        else:
            return HttpResponseUnauthorized()

    @cross_domain_api_post_view
    def logout_view(self, request, api_name):
        if request.user.is_anonymous():
            return HttpResponseUnauthorized()

        try:
            api_key = ApiKey.objects.get(user=request.user)
        except ApiKey.DoesNotExist:
            return HttpResponseUnauthorized()

        self.__regenerate_key(api_key)
        logout(request)

        return HttpResponseRedirect('/%s/' % api_name)

    @cross_domain_api_post_view
    def validate_api_key_view(self, request):
        if request.user.is_anonymous():
            return self.__build_response(False)

        try:
            api_key = ApiKey.objects.get(user=request.user)
        except ApiKey.DoesNotExist:
            return self.__build_response(False)
        else:
            expiration_time = api_key.created + datetime.timedelta(weeks=2)
            return self.__build_response(timezone.now() < expiration_time)

    def __build_response(self, api_key_validity):
        return HttpResponse(simplejson.dumps({
            "api_key_validity": api_key_validity,
        }))

    def __regenerate_key(self, api_key):
        api_key.key = api_key.generate_key()
        api_key.save()
        return api_key.key


def get_resource_by_name(resource_name):
    return EllaHubApi.registered_resources[resource_name]


def get_model_name(resource_name):
    resource = EllaHubApi.registered_resources[resource_name]
    return resource._meta.object_class.__name__.lower()
