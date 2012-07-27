from django.conf import settings


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
        ("Methods", "XS_SHARING_ALLOWED_METHODS", ("POST", "GET", "OPTIONS", "PUT", "DELETE")),
        ("Headers", "XS_SHARING_ALLOWED_HEADERS", ("Content-Type", "*")),
        ("Credentials", "XS_SHARING_ALLOWED_CREDENTIALS", "true"),
    )

    def process_response(self, request, response):
        for header_type, settins_var, default_val in CrossDomainAccessMiddleware.__OPTIONS:
            header_type = "Access-Control-Allow-" + header_type
            header_value = getattr(settings, settins_var, default_val)

            if isinstance(header_value, (tuple, list)):
                header_value = ",".join(header_value)

            response[header_type] = header_value

        return response
