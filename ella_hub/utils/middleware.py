import re
import datetime
try:
    # try import offset-aware datetime from Django >= 1.4
    from django.utils.timezone import now as datetime_now
except ImportError:
    # backward compatibility with Django < 1.4 (offset-naive datetimes)
    datetime_now = datetime.datetime.now

from django.conf import settings
from tastypie.models import ApiKey

APIKEY_HEADER_PATTERN = re.compile(r"ApiKey ([^:]+):(.+)", re.IGNORECASE)


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
        ("Methods", "XS_SHARING_ALLOWED_METHODS", ("POST", "GET", "OPTIONS", "PUT", "PATCH", "DELETE")),
        ("Headers", "XS_SHARING_ALLOWED_HEADERS", ("Content-Type", "X-Requested-With", "Authorization")),
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


class APIKeyRefresherMiddleware(object):
    def process_request(self, request):
        api_key = self.__get_api_key(request)
        if not api_key:
            return

        expiration_time = api_key.created + datetime.timedelta(weeks=2)
        if datetime_now() < expiration_time:
            api_key.created = datetime_now()
            api_key.save()

    def __get_api_key(self, request):
        authorization_header = request.META.get('HTTP_AUTHORIZATION')
        if authorization_header is None:
            return None

        match = APIKEY_HEADER_PATTERN.match(authorization_header)
        if not match:
            return None

        username, api_key = match.groups()
        try:
            return ApiKey.objects.get(user__username=username, key=api_key)
        except ApiKey.DoesNotExist:
            return None
