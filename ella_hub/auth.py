import re
import datetime

from tastypie.exceptions import ImmediateHttpResponse
from tastypie.http import HttpUnauthorized, HttpForbidden
from django.template import RequestContext
from django.contrib.auth.models import User
from ella.utils import timezone
from tastypie.authentication import ApiKeyAuthentication as Authentication
from tastypie.authorization import Authorization
from tastypie.models import ApiKey
from ella_hub import utils
from ella_hub.utils.perms import has_obj_perm


API_KEY_EXPIRATION_IN_DAYS = 14


class ApiAuthentication(Authentication):
    def is_authenticated(self, request, **kwargs):
        if super(ApiAuthentication, self).is_authenticated(request, **kwargs) is not True:
            return False
        username, key = self.extract_credentials(request)
        api_key = ApiKey.objects.get(user__username=username, key=key)

        expiration_time = api_key.created + datetime.timedelta(
            days=API_KEY_EXPIRATION_IN_DAYS)
        return timezone.now() < expiration_time


class ApiAuthorization(Authorization):
    """
    Authorization class that handles basic(class-specific) and advances(object-specific) permissions.
    """
    __perm_prefixes = {"GET":"view_",
                       "POST":"add_",
                       "PUT":"change_",
                       "PATCH":"change_",
                       "DELETE":"delete_"}
    # Regular Expression parsing resource name from `request.path`.
    __re_objects_class = re.compile(r"/[^/]*/(?P<resource_name>[^/]*)/.*")

    def is_authorized(self, request, object=None):
        self.request_method = request.META['REQUEST_METHOD']
        self.resource_name = self.__re_objects_class.match(request.path).group("resource_name")

        if self.request_method == "POST":
            # `apply_limits` method is not called for POST requests.
            permission_string = self.__perm_prefixes[request.method] + \
                utils.get_model_name_of_resource(self.resource_name)
            found_perm = filter(lambda perm: perm.endswith(permission_string),
                request.user.get_all_permissions())
            if not found_perm:
                raise ImmediateHttpResponse(response=HttpForbidden())
        return True

    def apply_limits(self, request, object_list):
        """
        Applying permission limits, this method is NOT called by POST requests.
        """
        user = request.user

        if user.is_superuser:
            return object_list

        allowed_objects = []
        permission_string = self.__perm_prefixes[self.request_method] + \
            utils.get_model_name_of_resource(self.resource_name)

        for obj in object_list:
            if has_obj_perm(request.user, obj, permission_string):
                allowed_objects.append(obj)

        if not allowed_objects and object_list:
            raise ImmediateHttpResponse(response=HttpForbidden())

        return allowed_objects
