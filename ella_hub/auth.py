import re
import datetime
import ella_hub

from tastypie.exceptions import ImmediateHttpResponse
from tastypie.http import HttpUnauthorized, HttpForbidden
from django.template import RequestContext
from django.contrib.auth.models import User
from tastypie.authentication import ApiKeyAuthentication as Authentication
from tastypie.authorization import Authorization
from tastypie.models import ApiKey

from ella_hub.utils import timezone


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
    # Prefixes of both basic (class-specific) and advanced (object-specidic) permissions based on Request type.
    __permPrefixes = {"GET":"view_", "POST":"add_", "PUT":"change_", "PATCH":"change_", "DELETE":"delete_"}
    # Suffix of advanced (object-specific) permissions.
    __permObjectSuffix = "_object"
    # Regular Expression parsing class name from path,
    # e.g. from /admin-api/author/1/ is author lower-cased Author class.
    __reGetObjectClass = re.compile(r"/[^/]*/(?P<class_name>[^/]*)/.*")

    def is_authorized(self, request, object=None):
        if request and hasattr(request, 'user') and not request.user.is_authenticated():
            return False

        # TODO multiple query, check tastypie doc!
        objectsClassName = self.__reGetObjectClass.match(request.path).group("class_name")

        # No need to apply object specific permissions to POST requests
        # Remark: apply_limits method is NOT called in POST requests
        # Q: return 403 instead of 401 ?
        if request.method == "POST":
            # e.g. add_article is suffix of articles.add_article
            permission_string = self.__permPrefixes[request.method] + \
                ella_hub.api.get_model_name(objectsClassName)
            foundPerm = filter(lambda perm: perm.endswith(permission_string),
                request.user.get_all_permissions())
            if not foundPerm:
                return False

        return True

    def apply_limits(self, request, object_list):
        """
        Applying permission limits, this method is NOT called after POST request.

        type(request) == django.core.handlers.wsgi.WSGIRequest
        type(object_list) == django.db.models.query.QuerySet
        """
        # TODO: permissions on Category/Article objects
        user = request.user

        if user.is_superuser:
            return object_list

        # Request method - one of GET, PUT, PATCH, DELETE (except POST)
        objectsClassName = self.__reGetObjectClass.match(request.path).group("class_name")

        allowedObjects = []

        # TODO: add class&object-specific permissions for GET request method.
        if request.method != "GET":
            for obj in object_list.all():
                permission_string = self.__permPrefixes[request.method] + \
                    ella_hub.api.get_model_name(objectsClassName)
                objPermission = permission_string + self.__permObjectSuffix

                foundPerm = filter(lambda perm: perm.endswith(permission_string),
                    request.user.get_all_permissions())

                if (foundPerm or user.has_perm(objPermission, obj)):
                    allowedObjects.append(obj.id)

        else:
            return object_list

        if not allowedObjects and object_list:
            raise ImmediateHttpResponse(response=HttpForbidden())

        # Filtering allowed objects.
        object_list = object_list.filter(id__in=allowedObjects)

        return object_list
