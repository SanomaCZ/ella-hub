# -*- coding: utf-8 -*-

from tastypie.resources import ALL_WITH_RELATIONS
from tastypie import fields

from django.contrib.auth.models import User

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
