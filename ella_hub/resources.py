import re

from tastypie import fields
from tastypie.resources import ModelResource

from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse, HttpResponseForbidden
from django.utils import simplejson

from ella_hub.auth import ApiAuthentication as Authentication
from ella_hub.auth import ApiAuthorization as Authorization
from ella_hub import utils
from ella_hub.utils.perms import has_model_permission, REST_PERMS
from ella_hub.utils.workflow import get_states, get_user_states


class ApiModelResource(ModelResource):

    #_patch = fields.BooleanField(attribute="PATCH", help_text="Can change resource.", default=True)
    #_delete = fields.BooleanField(attribute="DELETE", help_text="Can delete resource.", default=True)

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

        allowed_methods = []
        res_model = self._meta.object_class

        for request_str, perm_str in REST_PERMS.items():
            if has_model_permission(res_model, request.user,
                REST_PERMS[request_str]):
                allowed_methods.append(request_str.lower())

        if not allowed_methods:
            return HttpResponseForbidden()

        for fn, attrs in schema["fields"].items():
            if has_model_permission(res_model, request.user, "readonly_" + fn):
                schema["fields"][fn]["readonly"] = True

            schema["fields"][fn]["disabled"] = has_model_permission(res_model,
                request.user, "disabled_" + fn)

        schema['allowed_detail_http_methods'] = allowed_methods
        schema['allowed_list_http_methods'] = allowed_methods

        return self.create_response(request, schema)

    def alter_list_data_to_serialize(self, request, bundle):
        """
        Returns only field `objects` with useful data.
        """
        bundle = super(ApiModelResource, self).alter_list_data_to_serialize(request, bundle)
        if isinstance(bundle, dict) and "objects" in bundle:
            bundle = bundle["objects"]

        for object in bundle:
            self.__set_allowed_states(request, object)
        return bundle

    def alter_detail_data_to_serialize(self, request, bundle):
        bundle = super(ApiModelResource, self).alter_detail_data_to_serialize(request, bundle)
        return self.__set_allowed_states(request, bundle)

    def __set_allowed_states(self, request, bundle):
        bundle.data["allowed_states"] = get_user_states(self._meta.object_class, request.user)
        return bundle

    def __has_user_perm(self, user, content_type, permission, object):
        if has_user_model_perm(user, content_type.model_class(), permission):
            return True

        permission_string = '%s_%s' % (permission, content_type.model)
        return has_obj_perm(user, object, permission_string)

    def hydrate(self, bundle):
        """Fills user fields by current logged user."""
        for field_name in getattr(self._meta, "user_fields", ()):
            setattr(bundle.obj, field_name, bundle.request.user)

        return bundle

    class Meta:
        authentication = Authentication()
        authorization = Authorization()
        always_return_data = True


class MultipartFormDataModelResource(ApiModelResource):
    def deserialize(self, request, data, format=None):
        if not format:
            format = request.META.get('CONTENT_TYPE', 'application/json')

        attached_objects = {}
        for file in request.FILES.getlist('attached_object'):
            assert file.name not in attached_objects, "Uploaded 2 files with the same name."
            attached_objects[file.name] = file

        if format.lower().startswith('multipart/form-data'):
            data = simplejson.loads(request.POST['resource_data'])
            for object in data['objects']:
                for key, value in object.items():
                    self.__attach_object(attached_objects, object, key, value)

            return data

        return super(MultipartFormDataModelResource, self).deserialize(
            request, data, format)

    def __attach_object(self, attached_objects, object, key, value):
        if not isinstance(value, unicode):
            return

        if value.startswith('attached_object_id:'):
            parts = value.split(':')
            if len(parts) != 2:
                raise ValueError("Invalid format in field '%s' with attachment: %s" % (key, value))

            attached_object_id = parts[1]
            if attached_object_id not in attached_objects:
                raise ValueError("Attached object with ID '%s' not found." % attached_object_id)

            object[key] = attached_objects[attached_object_id]

    def put_detail(self, request, **kwargs):
        """
        Hack for problem with error message: "You cannot access body
        after reading from request's data stream".

        Related issue:
        https://github.com/toastdriven/django-tastypie/issues/42#issuecomment-6069008
        """
        content_type = request.META.get('CONTENT_TYPE', '').lower()
        if (content_type.startswith('multipart/form-data') and
            not hasattr(request, '_body')):
            request._body = ''

        return super(MultipartFormDataModelResource, self).put_detail(
            request, **kwargs)

    def patch_detail(self, request, **kwargs):
        """
        Hack for problem with error message: "You cannot access body
        after reading from request's data stream".
        """
        content_type = request.META.get('CONTENT_TYPE', '').lower()
        if content_type.startswith('multipart/form-data'):
            request.body

        return super(MultipartFormDataModelResource, self).patch_detail(
            request, **kwargs)

    def patch_list(self, request, **kwargs):
        """
        Hack for problem with error message: "You cannot access body
        after reading from request's data stream".
        """
        content_type = request.META.get('CONTENT_TYPE', '').lower()
        if content_type.startswith('multipart/form-data'):
            request.body

        return super(MultipartFormDataModelResource, self).patch_list(
            request, **kwargs)

    class Meta(ApiModelResource.Meta):
        pass
