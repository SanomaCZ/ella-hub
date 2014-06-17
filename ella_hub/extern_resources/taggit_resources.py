"""
Resources for django-taggit application.
https://github.com/yedpodtrzitko/django-taggit
git://github.com/yedpodtrzitko/django-taggit.git
"""
import logging

from django.db.models import Count
from django.db import IntegrityError
from django.conf.urls import url

from taggit.managers import TaggableManager
from taggit.models import TaggedItem, Tag

from tastypie import fields
from tastypie.exceptions import BadRequest
from tastypie.resources import ALL, ALL_WITH_RELATIONS

from ella.core.models import Publishable

from ella_hub.resources import ApiModelResource
from ella_hub.utils.fields import use_in_clever
from ella_hub.utils import (get_content_type_for_resource, get_resource_by_name,
    get_resource_model)


logger = logging.getLogger(__name__)


class TagResource(ApiModelResource):
    @staticmethod
    def initialize(resources):
        for resource in resources:
            # tag only public objects (articles, photos, ...)
            if not getattr(resource._meta, "public", False):
                continue

            # this may override previous declared attribute with name "tags"
            resource._meta.object_class.add_to_class("tags",
                TaggableManager(through=TaggedItem))

            field = fields.ToManyField(TagResource, "tags", blank=True,
                null=True, full=True, use_in=use_in_clever)
            # call `contribute_to_class` manually because
            # `DeclarativeMetaclass` already created `Resource` classes
            field.contribute_to_class(resource, "tags")
            resource.base_fields["tags"] = field

            # allow filtering
            resource._meta.filtering["tags"] = ALL_WITH_RELATIONS

            # patch methods in resources with attribute `tags`
            # probably better solution is to inherit `ToManyField`
            # but inherited field didn't work for me
            resource.hydrate_m2m = patch_hydrate_m2m(resource.hydrate_m2m)
            resource.save_m2m = patch_save_m2m(resource.save_m2m)
            resource.dehydrate = patch_dehydrate(resource.dehydrate)

    def prepend_urls(self):
        urls = super(TagResource, self).prepend_urls()
        resource_name = self._meta.resource_name

        return [
            url(r"%s/related/(?P<resource_name>[^/]+)/(?P<tag_set>[0-9;]+)/$" % resource_name, self.wrap_view("filter_by_tags"), name="api_filter_by_tags"),
        ] + urls

    def filter_by_tags(self, request, api_name, resource_name, tag_set):
        content_type = get_content_type_for_resource(resource_name)
        resource = get_resource_by_name(resource_name)
        model_class = get_resource_model(resource_name)
        tag_id_set = map(int, tag_set.split(";"))
        try:
            exclude = [int(one) for one in request.GET.getlist('exclude')]
        except Exception, e:
            logger.exception(e)
            exclude = []

        # select objects sorted according to number of given tags that contain
        object_ids = TaggedItem.objects.filter(tag__id__in=tag_id_set, content_type=content_type). \
                        exclude(object_id__in=exclude).values_list("object_id", flat=True). \
                        annotate(count=Count("object_id")).order_by('-count')[:resource._meta.limit]

        objects = model_class.objects.filter(pk__in=list(object_ids))
        # for publishable type use ordering by publish_from
        if issubclass(model_class, Publishable) and len(tag_id_set) == 1:
            objects = objects.order_by('-publish_from')
        bundles = [resource.build_bundle(obj=one, request=request) for one in objects]
        bundles = [resource.full_dehydrate(bundle) for bundle in bundles]
        return resource.create_response(request, bundles)

    def obj_create(self, bundle, request=None, **kwargs):
        try:
            return super(TagResource, self).obj_create(bundle, **kwargs)
        except IntegrityError:
            # duplicate entry for 'name' or 'slug'
            try:
                bundle.obj = Tag.objects.get(name=bundle.data["name"])
                return bundle
            except Tag.DoesNotExist:
                # duplicate entry for 'slug'
                raise BadRequest("Slug '%s' is not unique" % bundle.data["slug"])

    class Meta(ApiModelResource.Meta):
        queryset = Tag.objects.all()
        filtering = {
            "id": ALL,
            "name": ALL,
            "slug": ALL,
        }
        public = False


def patch_hydrate_m2m(hydrate_m2m):
    def patched_hydrate_m2m(self, bundle):
        main_tag_indexes = []
        for index, tag in enumerate(bundle.data.get("tags", ())):
            if isinstance(tag, dict) and "main_tag" in tag:
                # remove and store indexes of main tags
                main_tag_indexes.append(index)
                del tag["main_tag"]

                # translate dictionary to resource URI
                if "resource_uri" in tag:
                    bundle.data["tags"][index] = tag["resource_uri"]

        bundle = hydrate_m2m(self, bundle)

        for index in main_tag_indexes:
            bundle.data["tags"][index].data["main_tag"] = True

        return bundle

    return patched_hydrate_m2m


def patch_save_m2m(save_m2m):
    def patched_save_m2m(self, bundle):
        save_m2m(self, bundle)

        for bundle_m2m in bundle.data.get("tags", ()):
            if bundle_m2m.data.get("main_tag", False):
                #TODO - make 'MAIN' variable and make it cleaner
                if not bundle_m2m.data.get('name', '').upper().startswith('MAIN:'):
                    bundle_m2m.obj.name = 'MAIN:%s' % bundle_m2m.obj.name
                    bundle_m2m.obj.save()

    return patched_save_m2m


def patch_dehydrate(dehydrate):
    def patched_dehydrate(self, bundle):
        bundle = dehydrate(self, bundle)

        if "tags" in bundle.data:
            for index, tag in enumerate(bundle.obj.tags.all()):
                if tag.namespace.upper() == 'MAIN':
                    bundle.data["tags"][index].data["main_tag"] = True
                    break

        return bundle

    return patched_dehydrate
