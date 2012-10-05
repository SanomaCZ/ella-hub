"""
Resources for ella-taggit application.
https://github.com/ella/ella-taggit
git://github.com/ella/ella-taggit.git
"""

from tastypie import fields
from tastypie.resources import ALL
from ella_hub.resources import ApiModelResource
from ella_hub.ella_resources import PublishableResource
from ella_taggit.models import PublishableTag


class TagResource(ApiModelResource):
    class Meta(ApiModelResource.Meta):
        queryset = PublishableTag.objects.all()
        filtering = {
            "name": ALL,
            "slug": ALL,
        }
        public = False


