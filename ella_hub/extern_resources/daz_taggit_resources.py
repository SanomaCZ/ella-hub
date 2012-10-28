"""
Resources for daz-taggit application.
This application is part of DaZ project.
"""

from tastypie import fields
from tastypie.resources import ALL
from daz.daz_taggit.models import Tag
from ella_hub.resources import ApiModelResource
from ella_hub.ella_resources import PublishableResource


class TagResource(ApiModelResource):
    @staticmethod
    def initialize(resources):
        for resource in resources:
            if issubclass(resource, PublishableResource):
                field = fields.ToManyField(TagResource, "tags", blank=True,
                    null=True, full=True)
                # call `contribute_to_class` manually because
                # `DeclarativeMetaclass` already created `Resource` classes
                field.contribute_to_class(resource, "tags")
                resource.base_fields["tags"] = field

    class Meta(ApiModelResource.Meta):
        queryset = Tag.objects.all()
        filtering = {
            "name": ALL,
            "slug": ALL,
        }
        public = False
