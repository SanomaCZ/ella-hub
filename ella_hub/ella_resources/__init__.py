# -*- coding: utf-8 -*-

from tastypie.resources import ALL_WITH_RELATIONS
from tastypie import fields

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.utils import simplejson

from ella_hub.resources import ApiModelResource
from ella.core.models import Publishable, Listing, Category, Author
from ella.photos.models import Photo
from ella.articles.models import Article

from ella_hub.models import Draft


class CategoryResource(ApiModelResource):
    class Meta(ApiModelResource.Meta):
        queryset = Category.objects.all()
        filtering = {
            'app_data': ALL_WITH_RELATIONS,
            'content': ALL_WITH_RELATIONS,
            'description': ALL_WITH_RELATIONS,
            'id': ALL_WITH_RELATIONS,
            'resource_uri': ALL_WITH_RELATIONS,
            'slug': ALL_WITH_RELATIONS,
            'template': ALL_WITH_RELATIONS,
            'title': ALL_WITH_RELATIONS,
            'tree_path': ALL_WITH_RELATIONS,
        }


class UserResource(ApiModelResource):
    class Meta(ApiModelResource.Meta):
        queryset = User.objects.all()
        filtering = {
            'id': ALL_WITH_RELATIONS,
            'username': ALL_WITH_RELATIONS,
        }


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


class ListingResource(ApiModelResource):
    class Meta(ApiModelResource.Meta):
        queryset = Listing.objects.all()
        filtering = {
            'commercial': ALL_WITH_RELATIONS,
            'id': ALL_WITH_RELATIONS,
            'publish_from': ALL_WITH_RELATIONS,
            'publish_to': ALL_WITH_RELATIONS,
            'resource_uri': ALL_WITH_RELATIONS,
        }


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


class DraftResource(ApiModelResource):
    author = fields.ForeignKey(AuthorResource, 'author', full=True)

    def build_filters(self, filters=None):
        orm_filters = super(DraftResource, self).build_filters(filters)

        if 'content_type' in filters:
            orm_filters['content_type__name__iexact'] = filters['content_type']

        return orm_filters

    def hydrate(self, bundle):
        """
        Translates content_type name into real Django ContentType object.

        Name of content type is case insensitive and correspond to the name
        of resource.
        """
        content_type = ContentType.objects.get(name__iexact=bundle.data['content_type'])
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
        return bundle

    class Meta(ApiModelResource.Meta):
        queryset = Draft.objects.all()
        filtering = {
            'content_type': ['exact'],
            'name': ['exact'],
            'author': ALL_WITH_RELATIONS,
            'timestamp': ALL_WITH_RELATIONS,
        }


class PublishableResource(ApiModelResource):
    photo = fields.ForeignKey(PhotoResource, 'photo', null=True)
    authors = fields.ToManyField(AuthorResource, 'authors', full=True)
    listings = fields.ToManyField(ListingResource, 'listing_set', full=True)
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


class ArticleResource(PublishableResource):
    class Meta(ApiModelResource.Meta):
        queryset = Article.objects.all()
        filtering = {
            'announced': ALL_WITH_RELATIONS,
            'app_data': ALL_WITH_RELATIONS,
            'authors': ALL_WITH_RELATIONS,
            'category': ALL_WITH_RELATIONS,
            'content': ALL_WITH_RELATIONS,
            'created': ALL_WITH_RELATIONS,
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
            'updated': ALL_WITH_RELATIONS,
            'upper_title': ALL_WITH_RELATIONS,
        }
