# -*- coding: utf-8 -*-

from tastypie.resources import ALL_WITH_RELATIONS
from tastypie import fields

from django.contrib.auth.models import User

from ella_hub.resources import ApiModelResource
from ella.core.models import Publishable, Listing, Category, Author
from ella.photos.models import Photo
from ella.articles.models import Article

from ella_hub.auth import ApiAuthentication as Authentication
from ella_hub.auth import ApiAuthorization as Authorization

from django.contrib.auth.models import User
from django.db import models
from tastypie.models import create_api_key

models.signals.post_save.connect(create_api_key, sender=User)


class CategoryResource(ApiModelResource):
    class Meta:
        authentication = Authentication()
        authorization = Authorization()
        always_return_data = True
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
    class Meta:
        authentication = Authentication()
        authorization = Authorization()
        always_return_data = True
        queryset = User.objects.all()
        resource_name = 'user'
        filtering = {
            'id': ALL_WITH_RELATIONS,
            'username': ALL_WITH_RELATIONS,
        }


class PhotoResource(ApiModelResource):
    class Meta:
        authentication = Authentication()
        authorization = Authorization()
        always_return_data = True
        queryset = Photo.objects.all()
        resource_name = 'photo'
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
    class Meta:
        authentication = Authentication()
        authorization = Authorization()
        always_return_data = True
        queryset = Listing.objects.all()
        filtering = {
            'commercial': ALL_WITH_RELATIONS,
            'id': ALL_WITH_RELATIONS,
            'publish_from': ALL_WITH_RELATIONS,
            'publish_to': ALL_WITH_RELATIONS,
            'resource_uri': ALL_WITH_RELATIONS,
        }


class AuthorResource(ApiModelResource):
    class Meta:
        authentication = Authentication()
        authorization = Authorization()
        always_return_data = True
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

    class Meta:
        authentication = Authentication()
        authorization = Authorization()
        always_return_data = True
        queryset = Publishable.objects.all()
        resource_name = 'publishable'
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
    class Meta:
        authentication = Authentication()
        authorization = Authorization()
        always_return_data = True
        queryset = Article.objects.all()
        resource_name = 'article'
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
