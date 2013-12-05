import re
import json

from django.utils.http import urlunquote_plus
from django.http import HttpResponseForbidden
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.contenttypes.models import ContentType

from tastypie.exceptions import NotFound
from tastypie.resources import ModelResource

from ella_hub.auth import ApiAuthentication as Authentication
from ella_hub.auth import ApiAuthorization as Authorization
from ella_hub.utils import get_resource_model
from ella_hub.utils.perms import has_model_permission, REST_PERMS
from ella_hub.utils.workflow import set_state, get_state
from ella_hub.models import StateObjectRelation


class NOT_HYDRATED(object):
    pass


class ApiModelResource(ModelResource):
    __GENERATED_FIELDS_CACHE = {}

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
        #self.is_authorized(request)
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

        schema['allowed_detail_http_methods'] = allowed_methods
        schema['allowed_list_http_methods'] = allowed_methods

        return self.create_response(request, schema)

    def get_multiple(self, request, **kwargs):
        """
        Returns only serialized list of resources based on the identifiers
        from the URL. Tastypie's version returns some useless metadata.
        """
        self.method_check(request, allowed=['get'])
        self.is_authenticated(request)
        self.throttle_check(request)

        # Rip apart the list then iterate.
        kwarg_name = '%s_list' % self._meta.detail_uri_name
        obj_identifiers = kwargs.get(kwarg_name, '').split(';')
        objects = []


        for identifier in obj_identifiers:
            try:
                obj = self.obj_get(request, **{self._meta.detail_uri_name: identifier})
                bundle = self.build_bundle(obj=obj, request=request)
                bundle = self.full_dehydrate(bundle)
                objects.append(bundle)
            except ObjectDoesNotExist:
                pass

        self.log_throttled_access(request)
        return self.create_response(request, objects)

    def alter_list_data_to_serialize(self, request, bundle):
        """
        Returns only field `objects` with useful data.
        """
        bundle = super(ApiModelResource, self).alter_list_data_to_serialize(request, bundle)
        if isinstance(bundle, dict) and "objects" in bundle:
            bundle['data'] = [self._add_state_fields(one) for one in bundle['objects']]
            del bundle['objects']
        return bundle

    def alter_detail_data_to_serialize(self, request, bundle):
        bundle = super(ApiModelResource, self).alter_detail_data_to_serialize(request, bundle)
        return self._add_state_fields(bundle)

    def _add_state_fields(self, bundle):
        """Adds current state and next allowed states of object."""
        state = get_state(bundle.obj)
        next_states = []

        if state:
            bundle.data["state"] = state.codename
            next_states = [trans.destination for trans in state.transitions.select_related().all()]

        bundle.data["allowed_states"] = dict(
            (state.codename, state.title) for state in next_states
        )
        return bundle

    def full_dehydrate(self, bundle, *args, **kwargs):
        """
        Generates fields that are common for all objects of this resource.
        """
        bundle = super(ApiModelResource, self).full_dehydrate(bundle)
        # cache model permissions because of performance issues
        if not self._is_field_cached("allowed_http_methods"):
            self._fill_fields_pemissions(bundle)

        bundle.data['allowed_http_methods'] = self._get_cached_field("allowed_http_methods")
        bundle.data["read_only_fields"] = self._get_cached_field("read_only_fields")
        for field_name in self._get_cached_field("disabled_fields"):
            del bundle.data[field_name]

        return bundle

    def _fill_fields_pemissions(self, bundle):
        resource_model = self._meta.object_class
        user = bundle.request.user

        disabled_fields = []
        read_only_fields = []
        allowed_http_methods = []

        # set allowed_http_methods also
        for request_str, perm_str in REST_PERMS.items():
            if has_model_permission(resource_model, user,
                REST_PERMS[request_str]):
                allowed_http_methods.append(request_str.lower())

        self._set_cached_field("allowed_http_methods", allowed_http_methods)
        self._set_cached_field("read_only_fields", read_only_fields)
        self._set_cached_field("disabled_fields", tuple(disabled_fields))

    def hydrate(self, bundle, *args, **kwargs):
        """Fills user fields by current logged user."""
        for field_name in getattr(self._meta, "user_fields", ()):
            setattr(bundle.obj, field_name, bundle.request.user)

        if "state" in bundle.data:
            set_state(bundle.obj, bundle.data["state"])

        return bundle

    def full_hydrate(self, bundle):
        """
        Given a populated bundle, distill it and turn it back into
        a full-fledged object instance.
        """
        bundle = super(ApiModelResource, self).full_hydrate(bundle)

        if "photo" in bundle.data:
            if bundle.data["photo"] is None:
                setattr(bundle.obj, "photo", None)

            # we allow to set photo to None, if previous value wasn't None
            # because sometimes we want to remove photo from article
#            if field_object.instance_name == "photo":
#
#                print "d: name ", field_object.instance_name, field_object
#                print "d: name ", bundle.requset, field_object
#
#                if getattr(bundle.obj, field_object.attribute, None) is not None:
#                    setattr(bundle.obj, field_object.attribute, None)

        return bundle

    def _is_field_cached(self, name):
        """Resource class cache for generated fields."""
        cached_fields = ApiModelResource.__GENERATED_FIELDS_CACHE
        return name in cached_fields.get(self._meta.resource_name, {})

    def _set_cached_field(self, name, value):
        """Resource class cache for generated fields."""
        cached_fields = ApiModelResource.__GENERATED_FIELDS_CACHE
        fields = cached_fields.setdefault(self._meta.resource_name, {})
        fields[name] = value

    def _get_cached_field(self, name):
        """Resource class cache for generated fields."""
        assert self._is_field_cached(name)

        cached_fields = ApiModelResource.__GENERATED_FIELDS_CACHE
        return cached_fields[self._meta.resource_name][name]

    def resolve_resource_uri(self, uri):
        """
        Converts standard format resource URI into corresponding object.
        """
        pattern = r"/%s/(?P<resource_name>[^/]+)/(?P<pk>\d+)/$" % self._meta.api_name
        match = re.match(pattern, uri)
        if not match:
            raise NotFound("The URL provided '%s' was not a link to a valid resource." % uri)

        model_class = get_resource_model(match.group('resource_name'))
        return model_class.objects.get(pk=match.group('pk'))

    def build_filters(self, filters=None):
        """Tastypie has too strict validation for filtering."""
        state = None
        if filters and "state" in filters:
            state = filters["state"]
            del filters["state"]

        filters = super(ApiModelResource, self).build_filters(filters)

        if state:
            filters["state"] = state

        return filters

    def apply_filters(self, request, applicable_filters):
        # get object IDs of resource type in exact state
        if "state" in applicable_filters:
            content_type = ContentType.objects.get_for_model(self._meta.object_class)
            state_object_relations = StateObjectRelation.objects.filter(
                state__codename=applicable_filters["state"], content_type=content_type)
            object_ids = state_object_relations[:self._meta.limit].values_list("content_id", flat=True)
            applicable_filters["id__in"] = object_ids
            del applicable_filters["state"]

        return super(ApiModelResource, self).apply_filters(request, applicable_filters)

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
            data = urlunquote_plus(request.POST['resource_data'])
            data = json.loads(data, strict=False)
            for object in data['objects']:
                for key, value in object.items():
                    self.__attach_object(attached_objects, object, key, value)

            return data

        return super(MultipartFormDataModelResource, self).deserialize(
            request, data, format)

    def __attach_object(self, attached_objects, object, key, value):
        if not isinstance(value, unicode):
            return False

        if value.startswith('attached_object_id:'):
            parts = value.split(':')
            if len(parts) != 2:
                raise ValueError("Invalid format in field '%s' with attachment: %s" % (key, value))

            attached_object_id = parts[1]
            if attached_object_id not in attached_objects:
                raise ValueError("Attached object with ID '%s' not found." % attached_object_id)

            object[key] = attached_objects[attached_object_id]
            return True

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
