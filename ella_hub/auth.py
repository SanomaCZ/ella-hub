import re
import datetime

from django.contrib.auth.models import AnonymousUser

from tastypie.authentication import ApiKeyAuthentication as Authentication
from tastypie.authorization import DjangoAuthorization
from tastypie.exceptions import Unauthorized
from tastypie.models import ApiKey

from ella.utils import timezone

from ella_hub import conf


class ApiAuthentication(Authentication):
    def is_authenticated(self, request, **kwargs):
        response = super(ApiAuthentication, self).is_authenticated(request, **kwargs)
        if response is not True:
            return response

        username, key = self.extract_credentials(request)
        try:
            api_key = ApiKey.objects.get(user__username=username, key=key)
        except ApiKey.DoesNotExist:
            return False

        if self.is_api_key_expired(api_key):
            request.user = AnonymousUser()
            return False
        else:
            self.refresh_api_key_expiration_time(api_key)
            request.user = api_key.user
            return True

    def is_api_key_expired(self, api_key):
        expiration_time = api_key.created + datetime.timedelta(
            days=conf.API_KEY_EXPIRATION_IN_DAYS)
        return expiration_time <= timezone.now()

    def refresh_api_key_expiration_time(self, api_key):
        api_key.created = timezone.now()
        api_key.save()


class ApiAuthorization(DjangoAuthorization):
    """
    Authorization class that handles basic(class-specific) based on DjangoAuthorization.
    """
    # Regular Expression parsing resource name from `request.path`.
    __re_objects_class = re.compile(r"/[^/]*/(?P<resource_name>[^/]*)/.*")

    def read_list(self, object_list, bundle):
        klass = self.base_checks(bundle.request, object_list.model)

        if klass is False:
            return []

        permission = '%s.change_%s' % (klass._meta.app_label, klass._meta.module_name)

        if not bundle.request.user.has_perm(permission):
            raise Unauthorized("You are not allowed to access that resource - %s" % (permission,))

        return object_list

    def read_detail(self, object_list, bundle):
        klass = self.base_checks(bundle.request, bundle.obj.__class__)

        if klass is False:
            raise Unauthorized("You are not allowed to access that resource.")

        permission = '%s.change_%s' % (klass._meta.app_label, klass._meta.module_name)

        if not bundle.request.user.has_perm(permission):
            raise Unauthorized("You are not allowed to access that resource - %s" % (permission,))

        return True