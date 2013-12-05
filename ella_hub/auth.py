import re
import datetime

from django.contrib.auth.models import AnonymousUser

from tastypie.authentication import ApiKeyAuthentication as Authentication
from tastypie.authorization import Authorization
from tastypie.exceptions import ImmediateHttpResponse, Unauthorized
from tastypie.http import HttpForbidden
from tastypie.models import ApiKey

from ella.utils import timezone

from ella_hub import utils
from ella_hub import conf
from ella_hub.utils.perms import has_model_state_permission, has_object_permission, REST_PERMS


class ApiAuthentication(Authentication):
    def is_authenticated(self, request, **kwargs):
        response = super(ApiAuthentication, self).is_authenticated(request, **kwargs)
        if response is not True:
            return response

        username, key = self.extract_credentials(request)
        try:
            api_key = ApiKey.objects.get(user__username=username, key=key)
        except ApiKey.DoesNotExist:
            return False

        if self.is_api_key_expired(api_key):
            request.user = AnonymousUser()
            return False
        else:
            self.refresh_api_key_expiration_time(api_key)
            request.user = api_key.user
            return True

    def is_api_key_expired(self, api_key):
        expiration_time = api_key.created + datetime.timedelta(
            days=conf.API_KEY_EXPIRATION_IN_DAYS)
        return expiration_time <= timezone.now()

    def refresh_api_key_expiration_time(self, api_key):
        api_key.created = timezone.now()
        api_key.save()


class ApiAuthorization(Authorization):
    """
    Authorization class that handles basic(class-specific) and advances(object-specific) permissions.
    """
    # Regular Expression parsing resource name from `request.path`.
    __re_objects_class = re.compile(r"/[^/]*/(?P<resource_name>[^/]*)/.*")

    def read_list(self, object_list, bundle):
        user = bundle.request.user
        if user.is_superuser:
            return object_list

        if not object_list:
            raise Unauthorized('nada')

        for obj in object_list:
            if not has_object_permission(obj, user, REST_PERMS[bundle.request.method]):
                raise Unauthorized('nada')

        return object_list

    def read_detail(self, object_list, bundle):
        user = bundle.request.user
        if user.is_superuser:
            return True

        obj = object_list[0]
        if has_object_permission(obj, user, REST_PERMS[bundle.request.method]):
            return True

        raise Unauthorized("nope")

    def _common_create(self, request):
        self.resource_name = self.__re_objects_class.match(request.path).group("resource_name")

    def create_list(self, object_list, bundle):
        self._common_create(bundle.request)
        if bundle.request.user.is_superuser:
            return object_list
        return object_list

    def create_detail(self, object_list, bundle):
        self._common_create(bundle.request)
        user = bundle.request.user
        if user.is_superuser:
            return True

        obj = object_list[0] if object_list else False
        if not obj:
            raise Unauthorized("nope")

        if has_object_permission(obj, user, REST_PERMS[bundle.request.method]):
            return True

        raise Unauthorized("nope")

    def update_list(self, object_list, bundle):
        allowed = []

        # Since they may not all be saved, iterate over them.
        for obj in object_list:
            if obj.user == bundle.request.user or bundle.request.user.is_superuser:
                allowed.append(obj)

        return allowed

    def update_detail(self, object_list, bundle):
        if bundle.request.user.is_superuser:
            return True
        return bundle.obj.user == bundle.request.user

    def delete_list(self, object_list, bundle):
        self._common_create(bundle.request)

        user = bundle.request.user
        if user.is_superuser:
            return True

        if not object_list:
            raise Unauthorized('nada')

        for obj in object_list:
            if not has_object_permission(obj, user, REST_PERMS[bundle.request.method]):
                raise Unauthorized('nada')

        raise Unauthorized("nada")

    def delete_detail(self, object_list, bundle):
        self._common_create(bundle.request)

        user = bundle.request.user
        if user.is_superuser:
            return True

        if has_object_permission(object_list[0], user, REST_PERMS[bundle.request.method]):
            return True

        raise Unauthorized("nope")
