"""
Resources for ella-galleries application.
https://github.com/ella/ella-galleries
git://github.com/ella/ella-galleries.git
"""

from tastypie import fields
from tastypie.resources import ALL, ALL_WITH_RELATIONS
from ella_galleries.models import Gallery, GalleryItem
from ella_hub.resources import ApiModelResource
from ella_hub.ella_resources import PublishableResource, PhotoResource


class GalleryResource(PublishableResource):
    class Meta(PublishableResource.Meta):
        queryset = Gallery.objects.all()
        filtering = dict(
            PublishableResource.Meta.filtering,
            created=ALL,
        )
        public = False


class GalleryItemResource(ApiModelResource):
    gallery = fields.ForeignKey(GalleryResource, "gallery", full=True)
    photo = fields.ForeignKey(PhotoResource, "photo", full=True)

    class Meta(ApiModelResource.Meta):
        queryset = GalleryItem.objects.all()
        filtering = {
            "photo": ALL_WITH_RELATIONS,
            "order": ALL,
            "title": ALL,
        }
        ordering = ("order",)
        public = False
