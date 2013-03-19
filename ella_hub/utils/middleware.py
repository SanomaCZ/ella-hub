from django.conf import settings
from django.db import connection


class CrossDomainAccessMiddleware(object):
    """
    This middleware allows cross-domain XHR using the html5 postMessage API.

    Access-Control-Allow-Origin: http://foo.example
    Access-Control-Allow-Methods: POST, GET, OPTIONS, PUT, DELETE

    Based on https://gist.github.com/1369619
    """

    __OPTIONS = (
        # (header type, settings variable, default value)
        ("Origin", "XS_SHARING_ALLOWED_ORIGINS", "*"),
        ("Methods", "XS_SHARING_ALLOWED_METHODS", (
            "POST",
            "GET",
            "OPTIONS",
            "PUT",
            "PATCH",
            "DELETE",
        )),
        ("Headers", "XS_SHARING_ALLOWED_HEADERS", (
            "Content-Type",
            "X-Requested-With",
            "Authorization",
            "X-Mime-Type",
            "X-File-Name",
        )),
        ("Credentials", "XS_SHARING_ALLOWED_CREDENTIALS", "true"),
    )

    def process_response(self, request, response):
        for header_type, settins_var, default_val in CrossDomainAccessMiddleware.__OPTIONS:
            header = "Access-Control-Allow-" + header_type
            header_value = getattr(settings, settins_var, default_val)

            if header_type == "Origin" and header_value == "*":
                header_value = request.META.get("HTTP_ORIGIN", "*")

            if isinstance(header_value, (tuple, list)):
                header_value = ",".join(header_value)

            response[header] = header_value

        return response

class SQLMiddleware(object):

    def process_response(self, request, response):
        print "\n" * 10
        print len(connection.queries)
        return response
