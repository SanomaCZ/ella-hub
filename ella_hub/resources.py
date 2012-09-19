import re
import ella_hub.api

from tastypie import fields
from tastypie.resources import ModelResource
from django.utils import simplejson
from django.http import HttpResponse, HttpResponseForbidden
from django.contrib.contenttypes.models import ContentType

from ella_hub.auth import ApiAuthentication as Authentication
from ella_hub.auth import ApiAuthorization as Authorization
from ella_hub.utils.perms import has_user_model_perm, has_obj_perm



class MultipartResource(object):
    def deserialize(self, request, data, format=None):
        if not format:
            format = request.META.get('CONTENT_TYPE', 'application/json')

        if format.startswith('multipart'):
            data = request.POST.copy()
            data.update(request.FILES)
            data['photo'] = simplejson.loads(data['photo'])
            return data
        return super(MultipartResource, self).deserialize(request, data, format)

    def put_detail(self, request, **kwargs):
        if request.META.get('CONTENT_TYPE').startswith('multipart') and \
            not hasattr(request, '_body'):
            request._body = ''
        return super(MultipartResource, self).put_detail(request, **kwargs)

    def patch_detail(self, request, **kwargs):
        if request.META.get('CONTENT_TYPE').startswith('multipart'):
            request.body

        return super(MultipartResource, self).patch_detail(request, **kwargs)


class ApiModelResource(ModelResource):

    _patch = fields.BooleanField(attribute="PATCH", help_text="Can change resource.", default=True)
    _delete = fields.BooleanField(attribute="DELETE", help_text="Can delete resource.", default=True)

    @classmethod
    def get_fields(cls, fields=None, excludes=None):
        """
        Given any explicit fields to include and fields to exclude, add
        additional fields based on the associated model.

        Fixes #377 at https://github.com/toastdriven/django-tastypie/issues/377
        This method should be removed when issue #377 will be fixed in PyPI.
        """
        final_fields = {}
        fields = fields or []
        excludes = excludes or []

        if not cls._meta.object_class:
            return final_fields

        for f in cls._meta.object_class._meta.fields:
            # If the field name is already present, skip
            if f.name in cls.base_fields:
                continue

            # If field is not present in explicit field listing, skip
            if fields and f.name not in fields:
                continue

            # If field is in exclude list, skip
            if excludes and f.name in excludes:
                continue

            if cls.should_skip_field(f):
                continue

            api_field_class = cls.api_field_from_django_field(f)

            kwargs = {
                'attribute': f.name,
                'help_text': f.help_text,
                'blank': f.blank,
            }

            if f.null is True:
                kwargs['null'] = True

            kwargs['unique'] = f.unique

            if not f.null and f.blank is True:
                kwargs['default'] = ''

            if f.get_internal_type() == 'TextField':
                kwargs['default'] = ''

            if f.has_default():
                kwargs['default'] = f.default

            if getattr(f, 'auto_now', False):
                kwargs['default'] = f.auto_now

            if getattr(f, 'auto_now_add', False):
                kwargs['default'] = f.auto_now_add

            final_fields[f.name] = api_field_class(**kwargs)
            final_fields[f.name].instance_name = f.name

        return final_fields

    def get_schema(self, request, **kwargs):
        """
        Overriding get_schema method because of altering resource schema
        based on user permissions.
        """
        self.method_check(request, allowed=['get'])
        self.is_authenticated(request)
        self.is_authorized(request)
        self.throttle_check(request)
        self.log_throttled_access(request)
        schema = self.build_schema()

        methods_prefixes = (
            ("view_", "get"),
            ("add_", "post"),
            ("change_", "put"),
            ("change_", "patch"),
            ("delete_", "delete"),
        )

        user_perms = request.user.get_all_permissions()

        (objects_class_name,) = re.match(r"/[^/]*/([^/]*)/.*", request.path).groups()
        model_name = ella_hub.api.EllaHubApi.get_model_name(objects_class_name)
        ct = ContentType.objects.get(model=model_name)

        allowed_methods = []

        for (prefix, method) in methods_prefixes:
            permission_string = prefix + model_name
            if (ct.app_label + '.' + permission_string) in user_perms:
                allowed_methods.append(method)

        if not allowed_methods:
            return HttpResponseForbidden()

        schema['allowed_detail_http_methods'] = allowed_methods
        schema['allowed_list_http_methods'] = allowed_methods
        # applying only fields allowed for logged user,
        #del schema['fields']['app_data']
        # plus specifying readonly attribute
        #schema['fields']['app_data']['readonly'] = True
        return self.create_response(request, schema)

    def alter_list_data_to_serialize(self, request, bundle):
        """
        Returns only field `objects` with useful data.
        """
        bundle = super(ApiModelResource, self).alter_list_data_to_serialize(request, bundle)
        if isinstance(bundle, dict) and "objects" in bundle:
            bundle = bundle["objects"]

        for object in bundle:
            self.__filter_according_to_perms(request, object)
        return bundle

    def alter_detail_data_to_serialize(self, request, bundle):
        bundle = super(ApiModelResource, self).alter_detail_data_to_serialize(request, bundle)
        return self.__filter_according_to_perms(request, bundle)

    def __filter_according_to_perms(self, request, bundle):
        model_name = ella_hub.api.EllaHubApi.get_model_name(
            self._meta.resource_name)

        if (not has_user_model_perm(request.user, model_name, 'change') and not
            has_obj_perm(request.user, bundle.obj, 'change_%s' % model_name)):
            bundle.data['_patch'] = False

        if (not has_user_model_perm(request.user, model_name, 'delete') and not
            has_obj_perm(request.user, bundle.obj, 'delete_%s' % model_name)):
            bundle.data['_delete'] = False

        #filter according to user's permissions, f.e.:
        #   del object.data['content']
        return bundle

    def hydrate(self, bundle):
        """Fills user fields by current logged user."""
        for field_name in getattr(self._meta, "user_fields", ()):
            setattr(bundle.obj, field_name, bundle.request.user)

        return bundle

    class Meta:
        authentication = Authentication()
        authorization = Authorization()
        always_return_data = True
