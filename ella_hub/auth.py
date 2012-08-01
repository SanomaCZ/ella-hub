#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tastypie.authentication import ApiKeyAuthentication as Authentication
from tastypie.authorization import Authorization as ApiAuthorization


class ApiAuthentication(Authentication):
    pass # TODO: ceck API key expiration date
