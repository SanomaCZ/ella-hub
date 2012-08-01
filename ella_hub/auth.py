#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime
try:
    # try import offset-aware datetime from Django >= 1.4
    from django.utils.timezone import now as datetime_now
except ImportError:
    # backward compatibility with Django < 1.4 (offset-naive datetimes)
    datetime_now = datetime.now

from tastypie.authentication import ApiKeyAuthentication as Authentication
from tastypie.authorization import Authorization as ApiAuthorization
from tastypie.models import ApiKey


class ApiAuthentication(Authentication):
    def is_authenticated(self, request, **kwargs):
        if super(ApiAuthentication, self).is_authenticated(request, **kwargs) is not True:
            return False

        try:
            username, key = self.extract_credentials(request)
        except ValueError:
            return self._unauthorized()

        try:
            api_key = ApiKey.objects.get(user__username=username, key=key)
        except ApiKey.DoesNotExist:
            return self._unauthorized()

        expiration_time = api_key.created + datetime.timedelta(weeks=2)
        return datetime_now() < expiration_time
