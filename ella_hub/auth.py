import re
import datetime

from django.contrib.auth.models import AnonymousUser

from tastypie.authentication import ApiKeyAuthentication as Authentication
from tastypie.authorization import Authorization
from tastypie.exceptions import ImmediateHttpResponse
from tastypie.http import HttpForbidden
from tastypie.models import ApiKey

from ella.utils import timezone

from ella_hub import utils
from ella_hub import conf
from ella_hub.utils.perms import has_model_state_permission, has_object_permission, REST_PERMS


class ApiAuthentication(Authentication):
    def is_authenticated(self, request, **kwargs):
        if super(ApiAuthentication, self).is_authenticated(request, **kwargs) is not True:
            return False

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

    def is_authorized(self, request, object=None):
        self.resource_name = self.__re_objects_class.match(request.path).group("resource_name")

        if request.user.is_superuser:
            return True

        if request.method == "POST":
            resource_model = utils.get_resource_model(self.resource_name)
            if not has_model_state_permission(resource_model, request.user, REST_PERMS[request.method]):
                raise ImmediateHttpResponse(response=HttpForbidden())

        return True

    def apply_limits(self, request, object_list):
        """
        Applying permission limits, this method is NOT called by POST requests.
        TODO: object-level permissions
        """
        user = request.user

        if user.is_superuser:
            return object_list

        resource_model = utils.get_resource_model(self.resource_name)

        allowed_ids = []
        for obj in object_list:
            if has_object_permission(obj, user, REST_PERMS[request.method]):
                allowed_ids.append(obj.id)

        if request.method == "GET":
            if not has_model_state_permission(resource_model, user, REST_PERMS[request.method]):
                raise ImmediateHttpResponse(response=HttpForbidden())
            return object_list.filter(id__in=allowed_ids).all()

        if not allowed_ids:
            raise ImmediateHttpResponse(response=HttpForbidden())

        return object_list.filter(id__in=allowed_ids).all()
