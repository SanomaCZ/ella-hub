from django.http import HttpResponse, HttpResponseNotAllowed


def cross_domain_api_post_view(function):
    def decorator(self, request, *args, **kwargs):
        if request.method == "OPTIONS":
            return HttpResponse()
        elif request.method != "POST":
            return HttpResponseNotAllowed(["OPTIONS", "POST"])

        return function(self, request, *args, **kwargs)

    decorator.__name__ = function.__name__
    decorator.__doc__ = function.__doc__
    decorator.__module__ = function.__module__

    return decorator
