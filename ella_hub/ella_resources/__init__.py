import os

from PIL import Image
from tastypie import fields
from tastypie.resources import ALL, ALL_WITH_RELATIONS

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.files.images import ImageFile
from django.utils.encoding import force_unicode, smart_str

from ella.core.models import Publishable, Listing, Category, Author, Source
from ella.photos.models import Photo, FormatedPhoto, Format
from ella.photos.conf import photos_settings
from ella.utils.timezone import now

from ella_hub.resources import ApiModelResource, MultipartFormDataModelResource
from ella_hub.models import Draft, CommonArticle, Encyclopedia, Recipe
from ella_hub.utils import get_content_type_for_resource


class SiteResource(ApiModelResource):
    class Meta(ApiModelResource.Meta):
        queryset = Site.objects.all()
        filtering = {
            'domain': ('exact',),
            'id': ALL,
            'name': ('exact',),
            'resource_uri': ('exact',),
        }
        public = False


class CategoryResource(ApiModelResource):
    parent_category = fields.ForeignKey('self', 'tree_parent',
        blank=True, null=True)
    site = fields.ForeignKey(SiteResource, 'site', full=True)

    class Meta(ApiModelResource.Meta):
        queryset = Category.objects.all()
        filtering = {
            'id': ALL,
            'resource_uri': ('exact',),
            'slug': ('exact', 'iexact', 'contains', 'icontains', 'startswith', 'endswith',),
            'title': ('exact', 'iexact', 'contains', 'icontains', 'startswith', 'endswith',),
            'description': ('contains', 'icontains', 'startswith', 'endswith',),
            'content': ('contains', 'icontains', 'startswith', 'endswith',),
            'tree_path': ('exact', 'iexact', 'contains', 'icontains', 'startswith', 'endswith',),
            'tree_parent': ALL_WITH_RELATIONS,
            'site': ALL_WITH_RELATIONS,
        }
        public = False


class UserResource(ApiModelResource):
    class Meta(ApiModelResource.Meta):
        queryset = User.objects.all()
        fields = ('id', 'first_name', 'last_name', 'username')
        filtering = {
            'id': ALL,
            'resource_uri': ('exact',),
            'first_name': ('exact', 'iexact', 'contains', 'icontains', 'startswith', 'endswith',),
            'last_name': ('exact', 'iexact', 'contains', 'icontains', 'startswith', 'endswith',),
            'username': ('exact', 'iexact', 'contains', 'icontains', 'startswith', 'endswith',),
        }
        public = False


class AuthorResource(ApiModelResource):
    user = fields.ForeignKey(UserResource, 'user', blank=True, null=True,
        full=True)

    class Meta(ApiModelResource.Meta):
        queryset = Author.objects.all()
        filtering = {
            'id': ALL,
            'resource_uri': ('exact',),
            'user': ALL_WITH_RELATIONS,
            'name': ('exact', 'iexact', 'contains', 'icontains', 'startswith', 'endswith',),
            'slug': ('exact', 'iexact', 'contains', 'icontains', 'startswith', 'endswith',),
            'description': ('contains', 'icontains', 'startswith', 'endswith',),
            'text': ('contains', 'icontains', 'startswith', 'endswith',),
            'email': ('exact', 'iexact', 'contains', 'icontains', 'startswith', 'endswith',),
            'photo': ALL_WITH_RELATIONS,
        }
        public = False


class SourceResource(ApiModelResource):
    class Meta(ApiModelResource.Meta):
        queryset = Source.objects.all()
        filtering = {
            'name': ALL,
            'url': ALL,
        }
        public = False


class PhotoResource(MultipartFormDataModelResource):
    authors = fields.ToManyField(AuthorResource, 'authors', full=True)
    source = fields.ForeignKey(SourceResource, 'source', blank=True, null=True,
        full=True)

    def dehydrate(self, bundle):
        """Adds absolute URL of image."""
        bundle = super(PhotoResource, self).dehydrate(bundle)

        bundle.data['image'] = bundle.obj.image.url[len(settings.MEDIA_URL):]
        bundle.data['public_url'] = bundle.request.build_absolute_uri(
            bundle.obj.image.url)

        return bundle

    def hydrate(self, bundle):
        """Rotates image if possible"""
        bundle = super(PhotoResource, self).hydrate(bundle)

        if 'rotate' in bundle.data:
            uploaded_image = bundle.data['image']

            image = Image.open(uploaded_image)
            angle = int(bundle.data['rotate']) % 360
            image = image.rotate(-angle) # clockwise rotation
            path = self._upload_to(uploaded_image.name)
            image.save(path)

            bundle.data['image'] = ImageFile(open(path, "rb"))
            bundle.obj.image = bundle.data['image']

        return bundle

    def _upload_to(self, filename):
        name, ext = os.path.splitext(filename)
        ext = ext.lower()
        ext = photos_settings.TYPE_EXTENSION.get(ext, ext)

        return os.path.join(
            settings.MEDIA_ROOT,
            force_unicode(now().strftime(smart_str(photos_settings.UPLOAD_TO))),
            name + ext
        )


    class Meta(MultipartFormDataModelResource.Meta):
        queryset = Photo.objects.all()
        filtering = {
            'app_data': ('exact',),
            'created': ALL,
            'description': ('exact',),
            'height': ALL,
            'id': ALL,
            'image': ALL_WITH_RELATIONS,
            'important_bottom': ALL,
            'important_left': ALL,
            'important_right': ALL,
            'important_top': ALL,
            'resource_uri': ('exact',),
            'title': ('exact',),
            'width': ALL,
        }
        public = True


class FormatResource(ApiModelResource):
    sites = fields.ToManyField(SiteResource, 'sites', full=True)

    class Meta(ApiModelResource.Meta):
        queryset = Format.objects.all()
        filtering = {
            'name': ('exact',),
            'max_width': ALL,
            'max_height': ALL,
            'flexible_height': ('exact',),
            'flexible_max_height': ('exact',),
            'stretch': ('exact',),
            'nocrop': ('exact',),
            'resample_quality': ALL,
            'sites': ALL_WITH_RELATIONS,
        }
        public = False


class FormatedPhotoResource(ApiModelResource):
    format = fields.ForeignKey(FormatResource, 'format', full=True)
    photo = fields.ForeignKey(PhotoResource, 'photo', full=True)

    def dehydrate(self, bundle):
        bundle.data['image'] = bundle.obj.image.url[len(settings.MEDIA_URL):]
        return bundle

    class Meta(ApiModelResource.Meta):
        queryset = FormatedPhoto.objects.all()
        filtering = {
            'crop_left': ALL,
            'crop_top': ALL,
            'crop_width': ALL,
            'crop_height': ALL,
            'format': ALL_WITH_RELATIONS,
            'height': ALL,
            'image': ALL,
            'photo': ALL_WITH_RELATIONS,
            'width': ALL,
        }
        public = True


class PublishableResource(ApiModelResource):
    authors = fields.ToManyField(AuthorResource, 'authors', full=True)
    category = fields.ForeignKey(CategoryResource, 'category', full=True)
    photo = fields.ForeignKey(PhotoResource, 'photo', blank=True, null=True,
        full=True)
    source = fields.ForeignKey(SourceResource, 'source', blank=True, null=True,
        full=True)

    def dehydrate(self, bundle):
        bundle = super(PublishableResource, self).dehydrate(bundle)

        bundle.data['url'] = bundle.obj.get_domain_url()
        return bundle

    class Meta(ApiModelResource.Meta):
        queryset = Publishable.objects.all()
        filtering = {
            'id': ALL,
            'title': ('exact', 'iexact', 'contains', 'icontains', 'startswith', 'endswith',),
            'slug': ('exact', 'iexact', 'contains', 'icontains', 'startswith', 'endswith',),
            'published': ALL,
            'static': ('exact',),
            'description': ('contains', 'icontains', 'startswith', 'endswith',),
            'publish_from': ALL,
            'publish_to': ALL,
            'announced': ALL,
            'authors': ALL_WITH_RELATIONS,
            'category': ALL_WITH_RELATIONS,
            'photo': ALL_WITH_RELATIONS,
        }
        ordering = (
            'id',
            'slug',
            'published',
            'static',
            'publish_from',
            'publish_to',
            'category',
        )


class ListingResource(ApiModelResource):
    publishable = fields.ForeignKey(PublishableResource, 'publishable', full=True)
    category = fields.ForeignKey(CategoryResource, 'category', full=True)

    class Meta(ApiModelResource.Meta):
        queryset = Listing.objects.all()
        filtering = {
            'category': ALL_WITH_RELATIONS,
            'commercial': ('exact',),
            'id': ALL,
            'publish_from': ALL,
            'publish_to': ALL,
            'publishable': ALL_WITH_RELATIONS,
            'resource_uri': ('exact',),
        }


class DraftResource(ApiModelResource):
    user = fields.ForeignKey(UserResource, 'user', full=True)

    def build_filters(self, filters=None):
        orm_filters = super(DraftResource, self).build_filters(filters)

        if 'content_type' in filters:
            orm_filters['content_type__model__iexact'] = filters['content_type']

        return orm_filters

    def apply_filters(self, request, applicable_filters):
        """
        Always return only subset of objects that logged `user` owns.
        """
        object_list = super(DraftResource, self).apply_filters(request,
            applicable_filters)
        return object_list.filter(user=request.user)

    def hydrate(self, bundle):
        """
        Translates content_type name into real Django ContentType object.

        Name of content type is case insensitive and correspond to the name
        of resource.
        """
        bundle.obj.content_type = get_content_type_for_resource(
            bundle.data['content_type'])

        return super(DraftResource, self).hydrate(bundle)

    def alter_list_data_to_serialize(self, request, bundle):
        """
        Deserializes `data` JSONField into JSON data.
        """
        bundle = super(DraftResource, self).alter_list_data_to_serialize(request, bundle)

        for object in bundle:
            self.__alter_data_to_serialize(object)
        return bundle

    def alter_detail_data_to_serialize(self, request, bundle):
        """
        Deserializes `data` JSONField into JSON data.
        """
        bundle = super(DraftResource, self).alter_detail_data_to_serialize(request, bundle)
        return self.__alter_data_to_serialize(bundle)

    def __alter_data_to_serialize(self, bundle):
        bundle.data["data"] = bundle.obj.data
        bundle.data['content_type'] = bundle.obj.content_type.name.lower()
        return bundle

    class Meta(ApiModelResource.Meta):
        queryset = Draft.objects.all()
        ordering = ('-timestamp',)
        filtering = {
            'content_type': ('exact',),
            'name': ('exact',),
            'timestamp': ALL_WITH_RELATIONS,
        }
        public = False
        user_fields = ("user",)


class ArticleResource(PublishableResource):
    class Meta(PublishableResource.Meta):
        queryset = CommonArticle.objects.all()
        public = True


class EncyclopediaResource(PublishableResource):
    class Meta(PublishableResource.Meta):
        queryset = Encyclopedia.objects.all()
        public = True


class RecipeResource(PublishableResource):
    class Meta(PublishableResource.Meta):
        queryset = Recipe.objects.all()
        public = True
