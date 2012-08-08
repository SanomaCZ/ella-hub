#!/usr/bin/env python
# -*- coding: utf-8 -*-


import re
import datetime
try:
    # try import offset-aware datetime from Django >= 1.4
    from django.utils.timezone import now as datetime_now
except ImportError:
    # backward compatibility with Django < 1.4 (offset-naive datetimes)
    datetime_now = datetime.datetime.now

from django.template import RequestContext
from django.contrib.auth.models import User
from tastypie.authentication import ApiKeyAuthentication as Authentication
from tastypie.authorization import Authorization
from tastypie.models import ApiKey

from ella.core.models import Category

from guardian.shortcuts import assign


class ApiAuthentication(Authentication):
    def is_authenticated(self, request, **kwargs):
        if super(ApiAuthentication, self).is_authenticated(request, **kwargs) is not True:
            return False
        username, key = self.extract_credentials(request)
        api_key = ApiKey.objects.get(user__username=username, key=key)

        expiration_time = api_key.created + datetime.timedelta(weeks=2)
        return datetime_now() < expiration_time




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
        requestMethod = request.META['REQUEST_METHOD']
        objectsClassName = self.__reGetObjectClass.match(request.path).group("class_name")

        # No need to apply object specific permissions to POST requests
        # Remark: apply_limits method is NOT called in POST requests 
        if requestMethod == "POST":
            # e.g. add_article is suffix of articles.add_article
            foundPerm = filter(lambda perm: perm.endswith(self.__permPrefixes[requestMethod] + objectsClassName), 
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
        requestMethod = request.META['REQUEST_METHOD']
        objectsClassName = self.__reGetObjectClass.match(request.path).group("class_name")
        
        allowedObjects = []
        
        # TODO: add class&object-specific permissions for GET request method ? 
        if requestMethod != "GET":
            for obj in object_list.all():
                objPermission = self.__permPrefixes[requestMethod] + objectsClassName + self.__permObjectSuffix            

                if (self.__permPrefixes[requestMethod] + objectsClassName in request.user.get_all_permissions() or
                    user.has_perm(objPermission, obj)):    
                    allowedObjects.append(obj.id)
        else:
            return object_list

        # Filtering allowed objects.
        object_list = object_list.filter(id__in=allowedObjects)

        return object_list
