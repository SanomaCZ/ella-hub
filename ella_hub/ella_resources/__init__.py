from tastypie.resources import ALL_WITH_RELATIONS
from tastypie import fields

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.utils import simplejson

from ella_hub.resources import ApiModelResource
from ella.core.models import Publishable, Listing, Category, Author
from ella.photos.models import Photo

from ella_hub.models import Draft, CommonArticle, Encyclopedia, Recipe, PagedArticle


class SiteResource(ApiModelResource):
    class Meta(ApiModelResource.Meta):
        queryset = Site.objects.all()
        filtering = {
            'domain': ALL_WITH_RELATIONS,
            'id' : ALL_WITH_RELATIONS,
            'name' : ALL_WITH_RELATIONS,
            'resource_uri' : ALL_WITH_RELATIONS
        }
        public = False


class CategoryResource(ApiModelResource):
    site = fields.ForeignKey(SiteResource, 'site', full=True)

    class Meta(ApiModelResource.Meta):
        queryset = Category.objects.all()
        filtering = {
            'app_data': ALL_WITH_RELATIONS,
            'content': ALL_WITH_RELATIONS,
            'description': ALL_WITH_RELATIONS,
            'id': ALL_WITH_RELATIONS,
            'resource_uri': ALL_WITH_RELATIONS,
            'site_id': ALL_WITH_RELATIONS,
            'slug': ALL_WITH_RELATIONS,
            'template': ALL_WITH_RELATIONS,
            'title': ALL_WITH_RELATIONS,
            'tree_path': ALL_WITH_RELATIONS,
        }
        public = False


class UserResource(ApiModelResource):
    class Meta(ApiModelResource.Meta):
        queryset = User.objects.all()
        fields = ('id', 'first_name', 'last_name', 'username')
        filtering = {
            'username': ('exact',),
        }
        public = False


class PhotoResource(ApiModelResource):
    class Meta(ApiModelResource.Meta):
        queryset = Photo.objects.all()
        filtering = {
            'app_data': ALL_WITH_RELATIONS,
            'created': ALL_WITH_RELATIONS,
            'description': ALL_WITH_RELATIONS,
            'height': ALL_WITH_RELATIONS,
            'id': ALL_WITH_RELATIONS,
            'image': ALL_WITH_RELATIONS,
            'important_bottom': ALL_WITH_RELATIONS,
            'important_left': ALL_WITH_RELATIONS,
            'important_right': ALL_WITH_RELATIONS,
            'important_top': ALL_WITH_RELATIONS,
            'resource_uri': ALL_WITH_RELATIONS,
            'title': ALL_WITH_RELATIONS,
            'width': ALL_WITH_RELATIONS,
        }
        public = True


class AuthorResource(ApiModelResource):
    class Meta(ApiModelResource.Meta):
        queryset = Author.objects.all()
        filtering = {
            'description': ALL_WITH_RELATIONS,
            'email': ALL_WITH_RELATIONS,
            'id': ALL_WITH_RELATIONS,
            'name': ALL_WITH_RELATIONS,
            'resource_uri': ALL_WITH_RELATIONS,
            'slug': ALL_WITH_RELATIONS,
            'text': ALL_WITH_RELATIONS,
        }
        public = False


class PublishableResource(ApiModelResource):
    photo = fields.ForeignKey(PhotoResource, 'photo', null=True)
    authors = fields.ToManyField(AuthorResource, 'authors', full=True)
    #listings = fields.ToManyField(ListingResource, 'listing_set', full=True)
    category = fields.ForeignKey(CategoryResource, 'category', full=True)

    class Meta(ApiModelResource.Meta):
        queryset = Publishable.objects.all()
        filtering = {
            'announced': ALL_WITH_RELATIONS,
            'app_data': ALL_WITH_RELATIONS,
            'authors': ALL_WITH_RELATIONS,
            'category': ALL_WITH_RELATIONS,
            'description': ALL_WITH_RELATIONS,
            'id': ALL_WITH_RELATIONS,
            'listings': ALL_WITH_RELATIONS,
            'photo': ALL_WITH_RELATIONS,
            'publish_from': ALL_WITH_RELATIONS,
            'publish_to': ALL_WITH_RELATIONS,
            'published': ALL_WITH_RELATIONS,
            'resource_uri': ALL_WITH_RELATIONS,
            'slug': ALL_WITH_RELATIONS,
            'static': ALL_WITH_RELATIONS,
            'title': ALL_WITH_RELATIONS,
        }

    def dehydrate(self, bundle):
        bundle.data['url'] = bundle.obj.get_domain_url()
        return bundle



class ListingResource(ApiModelResource):
    publishable = fields.ForeignKey(PublishableResource, 'publishable', full=True)
    category = fields.ForeignKey(CategoryResource, 'category', full=True)

    class Meta(ApiModelResource.Meta):
        queryset = Listing.objects.all()
        filtering = {
            'category': ALL_WITH_RELATIONS,
            'commercial': ALL_WITH_RELATIONS,
            'id': ALL_WITH_RELATIONS,
            'publish_from': ALL_WITH_RELATIONS,
            'publish_to': ALL_WITH_RELATIONS,
            'publishable': ALL_WITH_RELATIONS,
            'resource_uri': ALL_WITH_RELATIONS,
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
        content_type = ContentType.objects.get(model__iexact=bundle.data['content_type'])
        bundle.obj.content_type = content_type
        return bundle

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
        bundle.data["content_type"] = bundle.obj.content_type.model.lower()
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


class PagedArticleResource(PublishableResource):
    class Meta(PublishableResource.Meta):
        queryset = PagedArticle.objects.all()
        public = True
