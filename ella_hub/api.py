import datetime
import ella_hub.resources

from inspect import isclass

from django.conf import settings
from django.conf.urls import url
from django.core.urlresolvers import reverse_lazy
from django.core.exceptions import ImproperlyConfigured
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.utils.importlib import import_module
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.contrib.auth import REDIRECT_FIELD_NAME

from tastypie.api import Api
from tastypie.exceptions import BadRequest, ImmediateHttpResponse
from tastypie.http import HttpUnauthorized
from tastypie.models import ApiKey
from tastypie.resources import Resource, ModelResource
from tastypie.serializers import Serializer
from tastypie.utils import is_valid_jsonp_callback_value
from tastypie.utils.mime import determine_format, build_content_type

from ella.core.models import Publishable
from ella.utils import timezone

from ella_hub.models import PublishableLock
from ella_hub import utils
from ella_hub.decorators import cross_domain_api_post_view
from ella_hub.ella_resources import PublishableResource
from ella_hub.utils.workflow import get_init_states, get_workflow
from ella_hub.utils.timezone import now
from ella_hub.auth import ApiAuthentication
from ella_hub import conf


class HttpJsonResponse(HttpResponse):
    def __init__(self, object, **kwargs):
        payload = Serializer().to_json(object)
        super(HttpJsonResponse, self).__init__(
            payload,
            content_type='application/json',
            **kwargs
        )


class EllaHubApi(Api):
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

    @classmethod
    def collect_resources(cls):
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
                    'Error importing resource module %s, '
                    'check RESOURCE_MODULES '
                    'in your settings: "%s"' % (module, e))
            else:
                resource_modules.append(mod)

        resources = []
        for mod in resource_modules:
            for attr in mod.__dict__:
                resource = getattr(mod, attr)
                if cls._is_resource_subclass(resource) and resource not in resources:
                    utils.save_resource_class(resource)
                    resources.append(resource)
        return resources

    @classmethod
    def _is_resource_subclass(cls, resource):
        if not isclass(resource):
            return False

        if not issubclass(resource, Resource):
            return False

        return resource not in (
            Resource,
            ModelResource,
            ella_hub.resources.ApiModelResource,
            ella_hub.resources.MultipartFormDataModelResource
        )

    def register_resources(self, resources):
        "Register one or more resources"

        for resource_class in resources:
            if hasattr(resource_class, "initialize"):
                resource_class.initialize(tuple(resources))

        for resource_class in resources:
            resource = resource_class()
            self.register(resource)
            utils.save_registered_resource(resource)

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
            url(r"^%s/validate-api-key/$" % self.api_name, self.wrap_view('validate_api_key_view')),

            url(r"^preview/(?P<id>\d+)/$", self.preview_publishable),
        ]

    def wrap_view(self, view):
        wrapped_view = super(EllaHubApi, self).wrap_view(view)
        return csrf_exempt(wrapped_view)

    def ensure_authenticated(self, request):
        authenticator = ApiAuthentication()
        auth_result = authenticator.is_authenticated(request)

        if isinstance(auth_result, HttpResponse):
            raise ImmediateHttpResponse(response=auth_result)

        if auth_result is not True:
            raise ImmediateHttpResponse(response=HttpUnauthorized())

    @cross_domain_api_post_view
    def login_view(self, request):
        username = request.POST.get("username", "")
        password = request.POST.get("password", "")
        user = authenticate(username=username, password=password)

        if user is not None and user.is_active:
            login(request, user)

            api_key, created = ApiKey.objects.get_or_create(user=user,
                                                            defaults={"created": now()})
            return HttpJsonResponse({
                "api_key": self.__regenerate_key(api_key),
                "user_id": api_key.user_id,
                "auth_tree": self.__create_auth_tree(request),
                "system": self.__get_system_info(request),
            })
        else:
            return HttpUnauthorized()

    @cross_domain_api_post_view
    def logout_view(self, request):
        try:
            self.ensure_authenticated(request)
        except ImmediateHttpResponse, e:
            return e.response

        try:
            api_key = ApiKey.objects.get(user=request.user)
        except ApiKey.DoesNotExist:
            return HttpUnauthorized()

        self.__regenerate_key(api_key)
        logout(request)

        return HttpJsonResponse({
            "success": True
        })

    @cross_domain_api_post_view
    def validate_api_key_view(self, request):
        try:
            self.ensure_authenticated(request)
        except:
            return self.__build_response(False)

        try:
            api_key = ApiKey.objects.get(user=request.user)
        except ApiKey.DoesNotExist:
            return self.__build_response(False)
        else:
            expiration_time = api_key.created + datetime.timedelta(
                days=conf.API_KEY_EXPIRATION_IN_DAYS)
            return self.__build_response(timezone.now() < expiration_time)

    def __build_response(self, api_key_validity):
        return HttpJsonResponse({
            "api_key_validity": api_key_validity,
        })

    def __regenerate_key(self, api_key):
        api_key.key = api_key.generate_key()
        api_key.created = timezone.now()
        api_key.save()
        return api_key.key

    @cross_domain_api_post_view
    def lock_publishable(self, request, id):
        try:
            self.ensure_authenticated(request)
        except ImmediateHttpResponse, e:
            return e.response

        publishable = Publishable.objects.get(id=id)
        lock = PublishableLock.objects.lock(publishable, request.user)
        return HttpJsonResponse({"locked": bool(lock)}, status=202)

    @cross_domain_api_post_view
    def unlock_publishable(self, request, id):
        try:
            self.ensure_authenticated(request)
        except ImmediateHttpResponse, e:
            return e.response

        publishable = Publishable.objects.get(id=id)
        PublishableLock.objects.unlock(publishable)
        return HttpResponse(status=202)

    def is_publishable_locked(self, request, id):
        try:
            self.ensure_authenticated(request)
        except ImmediateHttpResponse, e:
            return e.response

        publishable = Publishable.objects.get(id=id)
        lock = PublishableLock.objects.is_locked(publishable)

        payload = {"locked": bool(lock)}
        if lock:
            payload.update({
                "locked_by": "/%s/user/%s/" % (self.api_name, id),
                "locked_at": lock.timestamp,
            })

        return HttpJsonResponse(payload, status=202)

    def __get_system_info(self, request):
        system_info = {}

        system_res_tree = {}
        allowed_private_resources = self.__get_allowed_private_resources(request.user)
        for res_obj in allowed_private_resources:
            system_res_tree.update({
                res_obj._meta.resource_name: self.__create_resource_tree(res_obj, request.user)
            })

        system_info.update({"resources": system_res_tree})
        return system_info

    def __create_auth_tree(self, request):
        """
        Create authorization tree, so no need to crawl top level and
        particular resource schemas.
        """
        auth_tree = {}
        allowed_public_resources = self.__get_allowed_public_resources(request.user)

        for res_obj in allowed_public_resources:
            auth_tree.update({
                res_obj._meta.resource_name: self.__create_resource_tree(res_obj, request.user)
            })

        # covering article types under "articles" node
        article_resources = [
            res_obj for res_name, res_obj in self._registry.items()
            if issubclass(res_obj.__class__, PublishableResource) and
            type(res_obj) is not PublishableResource
        ]

        articles_dict = {}

        for article_obj in article_resources:
            if article_obj in allowed_public_resources:
                article_name = article_obj._meta.resource_name
                articles_dict.update({article_name: auth_tree[article_name]})
                del auth_tree[article_name]

        auth_tree.update({"articles": articles_dict})
        return auth_tree

    def __get_allowed_public_resources(self, user):
        allowed_public_resources = [
            res_obj for res_name, res_obj in self._registry.items()
            if getattr(res_obj._meta, "public", False)
        ]
        return allowed_public_resources

    def __get_allowed_private_resources(self, user):
        allowed_private_resources = [
            res_obj for res_name, res_obj in self._registry.items()
            if not getattr(res_obj._meta, "public", False)
        ]
        return allowed_private_resources

    def __create_resource_tree(self, res_obj, user):
        res_name = res_obj._meta.resource_name
        res_model = res_obj._meta.object_class

        schema = self._registry[res_name].build_schema()
        res_tree = {"allowed_http_methods": [], "fields": {}}

        pub_states = {}
        states = get_init_states(res_model, user)

        if states:
            for state in states:
                pub_states.update({state.codename: unicode(state.title)})
            res_tree.update({"states": pub_states})

        workflow = get_workflow(res_model)

        if workflow:
            workflow.get_initial_state()

        for fn, attrs in schema["fields"].items():
            field_attrs = {"readonly": False, "nullable": False, "disabled": False}
            res_tree["fields"].update({fn: field_attrs})

        res_tree["allowed_http_methods"] = schema["allowed_detail_http_methods"]
        return res_tree

    def preview_publishable(self, request, id):
        item = get_object_or_404(Publishable, pk=id)
        url = item.get_absolute_url(preview=True)
        if not item.is_published():
            if not request.user.is_authenticated():
                url = "%s?%s=%s" % (reverse_lazy("admin:login"), REDIRECT_FIELD_NAME, url,)
        return HttpResponseRedirect(url)
