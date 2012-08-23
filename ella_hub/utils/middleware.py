import re
import datetime

from django.conf import settings
from django.contrib.auth.models import User, AnonymousUser
from tastypie.models import ApiKey

from ella_hub.utils import timezone


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
            header = "Access-Control-Allow-" + header_type
            header_value = getattr(settings, settins_var, default_val)

            if header_type == "Origin" and header_value == "*":
                header_value = request.META.get("HTTP_ORIGIN", "*")

            if isinstance(header_value, (tuple, list)):
                header_value = ",".join(header_value)

            response[header] = header_value

        return response


class AuthenticationMiddleware(object):
    __APIKEY_HEADER_PATTERN = re.compile(r"ApiKey ([^:]+):(.+)", re.IGNORECASE)
    API_KEY_EXPIRATION_IN_DAYS = 14

    def process_request(self, request):
        # ignore authentication to Django admin
        if request.path.startswith("/admin/"):
            return

        try:
            username, key_token = self._extract_credentials(request)
            api_key = ApiKey.objects.get(user__username=username, key=key_token)
            if not self._is_api_key_valid(api_key):
                raise ValueError("API key expired.")
        except (ValueError, ApiKey.DoesNotExist):
            self.__set_anonymous_user(request)
            return None

        self._refresh_api_key_expiration_time(api_key)
        request.user = User.objects.get(username=username)
        return None

    def _extract_credentials(self, request):
        if self._authentication_header_is_set(request):
            match = AuthenticationMiddleware.__APIKEY_HEADER_PATTERN.match(
                request.META["HTTP_AUTHORIZATION"])

            if not match:
                raise ValueError("Incorrect authorization header.")

            username, api_key = match.groups()
        else:
            username = request.GET.get("username") or request.POST.get("username")
            api_key = request.GET.get("api_key") or request.POST.get("api_key")

        return username, api_key

    def _authentication_header_is_set(self, request):
        if not request.META.get("HTTP_AUTHORIZATION"):
            return False
        return request.META["HTTP_AUTHORIZATION"].lower().startswith("apikey ")

    def __set_anonymous_user(self, request):
        request.user = AnonymousUser()

    def _is_api_key_valid(self, api_key):
        expiration_time = api_key.created + datetime.timedelta(
            days=AuthenticationMiddleware.API_KEY_EXPIRATION_IN_DAYS)
        return timezone.now() < expiration_time

    def _refresh_api_key_expiration_time(self, api_key):
        api_key.created = timezone.now()
        api_key.save()
