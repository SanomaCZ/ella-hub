#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.utils import simplejson
from django.http import HttpResponse, HttpResponseRedirect
from django.views.defaults import permission_denied
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout


@csrf_exempt
def login_view(request, api_name):
    if request.method != "POST":
        return permission_denied(request)

    json_data = simplejson.loads(request.raw_post_data)
    username = json_data.get("username", "")
    password = json_data.get("password", "")
    user = authenticate(username=username, password=password)

    if user is not None and user.is_active:
        login(request, user)
        return HttpResponseRedirect('/%s/' % api_name)
    else:
        return HttpResponse(status=401)

@csrf_exempt
def logout_view(request, api_name):
    if request.method != "POST":
        return permission_denied(request)

    logout(request)
    return HttpResponseRedirect('/%s/' % api_name)
