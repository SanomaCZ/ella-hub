import re
import datetime
import ella_hub.signals

from inspect import isclass
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import (HttpResponse, HttpResponseBadRequest,
    HttpResponseRedirect, HttpResponseForbidden)
from django.utils.importlib import import_module
from django.core.exceptions import ImproperlyConfigured
from django.conf.urls.defaults import url
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType
from ella.core.models import Publishable
from tastypie.api import Api
from tastypie.http import HttpUnauthorized
from tastypie.exceptions import BadRequest
from tastypie.resources import Resource, ModelResource
from tastypie.models import ApiKey
from tastypie.serializers import Serializer
from tastypie.utils.mime import determine_format, build_content_type
from ella_hub.models import PublishableLock
from ella_hub.utils import timezone
from ella_hub.utils.perms import has_user_model_perm, is_resource_allowed
from ella_hub.decorators import cross_domain_api_post_view
from ella_hub.resources import ApiModelResource


class HttpJsonResponse(HttpResponse):
    def __init__(self, object, **kwargs):
        payload = Serializer().to_json(object)
        super(HttpJsonResponse, self).__init__(payload,
            content_type='application/json', **kwargs)


class EllaHubApi(Api):
    """
    """

    registered_resources = {}

    @classmethod
    def get_model_name(cls, resource_name):
        """Returns name of DB model for given resource name."""
        resource = cls.registered_resources[resource_name]
        return resource._meta.object_class.__name__.lower()

    def top_level(self, request, api_name=None):
        """
        Overriding top_level method to serialize only resources
        that user has rights to use.
        """
        serializer = Serializer()
        available_resources = {}

        if api_name is None:
            api_name = self.api_name

        for resource_name in sorted(self._registry.keys()):
            model_name = EllaHubApi.get_model_name(resource_name)
            if not is_resource_allowed(request.user, model_name):
                continue

            available_resources[resource_name] = {
                'list_endpoint': self._build_reverse_url("api_dispatch_list", kwargs={
                    'api_name': api_name,
                    'resource_name': resource_name,
                }),
                'schema': self._build_reverse_url("api_get_schema", kwargs={
                    'api_name': api_name,
                    'resource_name': resource_name,
                }),
            }

        if not available_resources:
            return HttpResponseForbidden()

        desired_format = determine_format(request, serializer)
        options = {}

        if 'text/javascript' in desired_format:
            callback = request.GET.get('callback', 'callback')

            if not is_valid_jsonp_callback_value(callback):
                raise BadRequest('JSONP callback name is invalid.')

            options['callback'] = callback

        serialized = serializer.serialize(available_resources, desired_format, options)
        return HttpResponse(content=serialized, content_type=build_content_type(desired_format))

    def register_view_model_permission(self):
        """
        Register view model permission for all resource classes.
        - view_<className>
        """
        for resource_name in EllaHubApi.registered_resources.keys():
            resource = ella_hub.api.EllaHubApi.registered_resources[resource_name]
            model_name = resource._meta.object_class.__name__.lower()
            ct = ContentType.objects.get(model=model_name)

            perm = Permission.objects.get_or_create(codename='view_%s' % model_name,
                name='View %s.' % model_name, content_type=ct)
            if not isinstance(perm, tuple):
                perm.save()

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
            url(r"^%s/lock-publishable/(?P<id>\d+)/$" % self.api_name, self.wrap_view('lock_publishable')),
            url(r"^%s/unlock-publishable/(?P<id>\d+)/$" % self.api_name, self.wrap_view('unlock_publishable')),
            url(r"^%s/is-publishable-locked/(?P<id>\d+)/$" % self.api_name, self.wrap_view('is_publishable_locked')),

            url(r"^%s/login/$" % self.api_name, self.wrap_view('login_view')),
            url(r"^%s/logout/$" % self.api_name, self.wrap_view('logout_view')),
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
            return HttpJsonResponse({
                "api_key": self.__regenerate_key(api_key),
                "auth_tree": self.__create_auth_tree(request),
            })
        else:
            return HttpUnauthorized()

    @cross_domain_api_post_view
    def logout_view(self, request):
        if request.user.is_anonymous():
            return HttpUnauthorized()

        try:
            api_key = ApiKey.objects.get(user=request.user)
        except ApiKey.DoesNotExist:
            return HttpUnauthorized()

        self.__regenerate_key(api_key)
        logout(request)

        return HttpResponseRedirect('/%s/' % self.api_name)

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
        return HttpJsonResponse({
            "api_key_validity": api_key_validity,
        })

    def __regenerate_key(self, api_key):
        api_key.key = api_key.generate_key()
        api_key.save()
        return api_key.key

    @cross_domain_api_post_view
    def lock_publishable(self, request, id):
        publishable = Publishable.objects.get(id=id)
        lock = PublishableLock.objects.lock(publishable, request.user)
        return HttpJsonResponse({"locked": bool(lock)}, status=202)

    @cross_domain_api_post_view
    def unlock_publishable(self, request, id):
        publishable = Publishable.objects.get(id=id)
        lock = PublishableLock.objects.unlock(publishable)
        return HttpResponse(status=202)

    def is_publishable_locked(self, request, id):
        publishable = Publishable.objects.get(id=id)
        lock = PublishableLock.objects.is_locked(publishable)

        payload = {"locked": bool(lock)}
        if lock:
            payload.update({
                "locked_by": "/%s/user/%s/" % (self.api_name, id),
                "locked_at": lock.timestamp,
            })

        return HttpJsonResponse(payload, status=202)

    def __create_auth_tree(self, request):
        """
        self._registry - dict{res_name: <res_obj>}
        return:
            dict{resource_name: {"allowed_http_methods":["get","post",...],
                                 "fields": {attr1:{"readonly": boolean, "nullable":boolean}}}}
        """

        auth_tree = {}
        allowed_resources = [res for res in self._registry.keys()
            if has_user_model_perm(request.user, EllaHubApi.get_model_name(res))]

        for res_name in allowed_resources:
            schema = self._registry[res_name].build_schema()
            res_tree = {"allowed_http_methods":[], "fields":{}}

            for fn, attrs in schema['fields'].items():
                field_attrs = {"readonly": False, "nullable": False}
                field_attrs["readonly"] = attrs["readonly"]
                field_attrs["nullable"] = attrs["nullable"]
                res_tree["fields"].update({fn:field_attrs})

            res_tree["allowed_http_methods"] = schema["allowed_detail_http_methods"]
            auth_tree.update({res_name:res_tree})
        return auth_tree
