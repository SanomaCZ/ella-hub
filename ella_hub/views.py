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

from django.utils import simplejson
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.views.defaults import permission_denied
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from tastypie.models import ApiKey

# generate API key for new user
from django.contrib.auth.models import User
from django.db import models
from tastypie.models import create_api_key

models.signals.post_save.connect(create_api_key, sender=User)

APIKEY_HEADER_PATTERN = re.compile(r"ApiKey ([^:]+):(.+)", re.IGNORECASE)


class HttpResponseUnauthorized(HttpResponse):
    def __init__(self):
        super(HttpResponseUnauthorized, self).__init__(status=401)


def cross_domain_post_view(function):
    @csrf_exempt
    def decorator(request, *args, **kwargs):
        if request.method == "OPTIONS":
            return HttpResponse()
        elif request.method != "POST":
            return HttpResponseBadRequest("Only POST requests are allowed.")

        return function(request, *args, **kwargs)

    return decorator

def regenerate_key(api_key):
    api_key.key = api_key.generate_key()
    api_key.save()
    return api_key.key

@cross_domain_post_view
def login_view(request):
    username = request.POST.get("username", "")
    password = request.POST.get("password", "")
    user = authenticate(username=username, password=password)

    if user is not None and user.is_active:
        try:
            api_key = ApiKey.objects.get(user=user)
        except ApiKey.DoesNotExist:
            return HttpResponseUnauthorized()
        login(request, user)
        return HttpResponse(simplejson.dumps({
            "api_key": regenerate_key(api_key),
        }))
    else:
        return HttpResponseUnauthorized()

def parse_authorization_header(request):
    authorization_header = request.META.get('HTTP_AUTHORIZATION')
    if authorization_header is None:
        raise ValueError("Authorization header missing")

    match = APIKEY_HEADER_PATTERN.match(authorization_header)
    if not match:
        raise ValueError("Authorization header in wrong format")

    # return username, api_key pair
    return match.groups()

@cross_domain_post_view
def validate_api_key_view(request):
    try:
        user_name, key = parse_authorization_header(request)
        api_key = ApiKey.objects.get(user__username=user_name, key=key)
    except ValueError:
        return HttpResponseBadRequest()
    except ApiKey.DoesNotExist:
        return HttpResponse(simplejson.dumps({
            "api_key_validity": False,
        }))
    else:
        expiration_time = api_key.created + datetime.timedelta(weeks=2)
        return HttpResponse(simplejson.dumps({
            "api_key_validity": datetime_now() < expiration_time,
        }))

@cross_domain_post_view
def logout_view(request, api_name):
    try:
        user_name, key = parse_authorization_header(request)
        api_key = ApiKey.objects.get(user__username=user_name, key=key)
    except ValueError:
        return HttpResponseBadRequest()
    except ApiKey.DoesNotExist:
        return HttpResponseUnauthorized()
    else: # change API key
        regenerate_key(api_key)

    logout(request)
    return HttpResponseRedirect('/%s/' % api_name)
