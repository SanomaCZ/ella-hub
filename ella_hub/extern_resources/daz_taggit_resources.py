"""
Resources for daz-taggit application.
This application is part of DaZ project.
"""

from django.db.models import Count
from django.conf.urls.defaults import url
from tastypie import fields
from tastypie.resources import ALL
from daz.daz_taggit.models import Tag, TaggedItem, TaggableManager
from ella_hub.resources import ApiModelResource
from ella_hub.ella_resources import PublishableResource
from ella_hub.utils import (get_content_type_for_resource, get_resource_by_name,
    get_resource_model)


class TagResource(ApiModelResource):
    @staticmethod
    def initialize(resources):
        for resource in resources:
            # tag only public objects (articles, photos, ...)
            if not getattr(resource._meta, "public", False):
                continue

            if not hasattr(resource.Meta.object_class, "tags"):
                resource.Meta.object_class.add_to_class("tags",
                    TaggableManager(through=TaggedItem))

            field = fields.ToManyField(TagResource, "tags", blank=True,
                null=True, full=True)
            # call `contribute_to_class` manually because
            # `DeclarativeMetaclass` already created `Resource` classes
            field.contribute_to_class(resource, "tags")
            resource.base_fields["tags"] = field

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

        # select objects sorted according to number of given tags that contain
        objects = TaggedItem.objects.filter(tag__id__in=tag_id_set, content_type=content_type)
        objects = objects.values("object_id").annotate(count=Count("object_id"))
        objects = objects.order_by("-count")[:resource._meta.limit]
        # extract primary keys of selected objects
        object_ids = map(lambda o: o["object_id"], objects)

        # sort bundles according to number of given tags that object contains
        objects = dict((o.id, o,) for o in model_class.objects.filter(pk__in=object_ids))
        bundles = [resource.build_bundle(obj=objects[id], request=request) for id in object_ids]
        bundles = [resource.full_dehydrate(bundle) for bundle in bundles]

        return resource.create_response(request, bundles)

    class Meta(ApiModelResource.Meta):
        queryset = Tag.objects.all()
        filtering = {
            "name": ALL,
            "slug": ALL,
        }
        public = False
