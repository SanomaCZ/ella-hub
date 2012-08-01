#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tastypie.authentication import DigestAuthentication as Authentication
from tastypie.authorization import Authorization as ApiAuthorization


class ApiAuthentication(Authentication):
    def is_authenticated(self, request, **kwargs):
        return request.user.is_authenticated()

    def get_identifier(self, request):
        return request.user.username
