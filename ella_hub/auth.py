import re
import datetime
import ella_hub.api

from tastypie.exceptions import ImmediateHttpResponse
from tastypie.http import HttpUnauthorized, HttpForbidden
from django.template import RequestContext
from django.contrib.auth.models import User
from ella.utils import timezone
from tastypie.authentication import ApiKeyAuthentication as Authentication
from tastypie.authorization import Authorization
from tastypie.models import ApiKey

from ella_hub.utils.perms import has_obj_perm


class ApiAuthentication(Authentication):
    def is_authenticated(self, request, **kwargs):
        if super(ApiAuthentication, self).is_authenticated(request, **kwargs) is not True:
            return False
        username, key = self.extract_credentials(request)
        api_key = ApiKey.objects.get(user__username=username, key=key)

        expiration_time = api_key.created + datetime.timedelta(weeks=2)
        return timezone.now() < expiration_time


class ApiAuthorization(Authorization):
    """
    Authorization class that handles basic(class-specific) and advances(object-specific) permissions.
    2 methods are overridden: is_authorized() and (optional) apply_limits()
    """
    # Prefixes of both basic (class-specific) and
    # advanced (object-specidic) permissions based on Request type.
    __perm_prefixes = {"GET":"view_", "POST":"add_", "PUT":"change_",
                       "PATCH":"change_", "DELETE":"delete_"}
    # Regular Expression parsing class name from path,
    # e.g. from /admin-api/author/1/ is author lower-cased Author class.
    __re_objects_class = re.compile(r"/[^/]*/(?P<class_name>[^/]*)/.*")


    def is_authorized(self, request, object=None):
        if request and hasattr(request, 'user') and not request.user.is_authenticated():
            return False

        self.request_method = request.META['REQUEST_METHOD']
        self.objects_class_name = self.__re_objects_class.match(request.path).group("class_name")

        if self.request_method == "POST":
            # e.g. add_article is suffix of articles.add_article
            permission_string = self.__perm_prefixes[request.method] + \
                ella_hub.api.EllaHubApi.get_model_name(self.objects_class_name)
            found_perm = filter(lambda perm: perm.endswith(permission_string),
                request.user.get_all_permissions())
            if not found_perm:
                raise ImmediateHttpResponse(response=HttpForbidden())
        return True

    def apply_limits(self, request, object_list):
        """
        Applying permission limits, this method is NOT called after POST request.

        type(request) == django.core.handlers.wsgi.WSGIRequest
        type(object_list) == django.db.models.query.QuerySet
        """
        user = request.user

        if user.is_superuser:
            return object_list

        allowed_objects = []
        permission_string = self.__perm_prefixes[self.request_method] + \
            ella_hub.api.EllaHubApi.get_model_name(self.objects_class_name)

        for obj in object_list:
            if has_obj_perm(request.user, obj, permission_string):
                allowed_objects.append(obj)

        if not allowed_objects and object_list:
            raise ImmediateHttpResponse(response=HttpForbidden())

        return allowed_objects
