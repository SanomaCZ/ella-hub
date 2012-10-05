"""
Resources for ella-taggit application.
https://github.com/ella/ella-taggit
git://github.com/ella/ella-taggit.git
"""

from tastypie import fields
from tastypie.resources import ALL
from ella_taggit.models import PublishableTag
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
        queryset = PublishableTag.objects.all()
        filtering = {
            "name": ALL,
            "slug": ALL,
        }
        public = False
