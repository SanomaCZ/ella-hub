#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseBadRequest


def cross_domain_post_view(function):
    @csrf_exempt
    def decorator(request, *args, **kwargs):
        if request.method == "OPTIONS":
            return HttpResponse()
        elif request.method != "POST":
            return HttpResponseBadRequest("Only POST requests are allowed.")

        return function(request, *args, **kwargs)

    decorator.__name__ = function.__name__
    decorator.__doc__ = function.__doc__
    decorator.__module__ = function.__module__

    return decorator
