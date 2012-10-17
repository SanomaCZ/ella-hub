import re
import datetime

from django.template import RequestContext
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType

from tastypie.authentication import ApiKeyAuthentication as Authentication
from tastypie.authorization import Authorization
from tastypie.exceptions import ImmediateHttpResponse
from tastypie.http import HttpUnauthorized, HttpForbidden
from tastypie.models import ApiKey
from ella.utils import timezone

from ella_hub import utils
from ella_hub.models import ModelPermission
from ella_hub.utils.perms import has_permission, has_model_permission, REST_PERMS


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
    # Regular Expression parsing resource name from `request.path`.
    __re_objects_class = re.compile(r"/[^/]*/(?P<resource_name>[^/]*)/.*")

    def is_authorized(self, request, object=None):
        self.request_method = request.META['REQUEST_METHOD']
        self.resource_name = self.__re_objects_class.match(request.path).group("resource_name")
        content_type = utils.get_content_type_for_resource(self.resource_name)

        if self.request_method == "POST":
            resource_model = utils.get_resource_model(self.resource_name)
            if not has_model_permission(resource_model, request.user, REST_PERMS[self.request_method]):
                raise ImmediateHttpResponse(response=HttpForbidden())
        return True

    def apply_limits(self, request, object_list):
        """
        Applying permission limits, this method is NOT called by POST requests.
        TODO: object-level permissions
        """
        user = request.user
        content_type = utils.get_content_type_for_resource(self.resource_name)

        if user.is_superuser:
            return object_list

        resource_model = utils.get_resource_model(self.resource_name)

        allowed_ids = []
        for obj in object_list:
            if has_permission(obj, request.user, REST_PERMS[self.request_method]):
                allowed_ids.append(obj.id)

        if self.request_method == "GET":
            if not has_model_permission(resource_model, request.user, REST_PERMS[self.request_method]):
                raise ImmediateHttpResponse(response=HttpForbidden())
            return object_list.filter(id__in=allowed_ids).all()

        if not allowed_ids:
            raise ImmediateHttpResponse(response=HttpForbidden())

        return object_list.filter(id__in=allowed_ids).all()
