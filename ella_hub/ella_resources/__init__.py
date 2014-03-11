import logging
import operator
import os

from PIL import Image
from tastypie import fields
from tastypie.resources import ALL, ALL_WITH_RELATIONS

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.files.images import ImageFile
from django.utils.encoding import force_unicode, smart_str
from django.db.models import Q

from ella.core.models import Publishable, Listing, Category, Author, Source, Related
from ella.articles.models import Article
from ella.positions.models import Position
from ella.photos.models import Photo, FormatedPhoto, Format
from ella.photos.conf import photos_settings
from ella.utils.timezone import now

from ella_hub.resources import ApiModelResource, MultipartFormDataModelResource
from ella_hub.models import Draft, State
from ella_hub.utils.workflow import set_state, get_state
from ella_hub.utils import get_content_type_for_resource, get_resource_for_object
from ella_hub.utils.fields import use_in_clever


logger = logging.getLogger(__name__)


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
        blank=True, null=True, use_in=use_in_clever)
    site = fields.ForeignKey(SiteResource, 'site', full=True, use_in=use_in_clever)
    app_data = fields.DictField('app_data')

    def dehydrate(self, bundle, *args, **kwargs):
        """Adds full name of category to the root category."""
        bundle = super(CategoryResource, self).dehydrate(bundle, *args, **kwargs)

        bundle.data['full_title'] = self._get_full_title(bundle.obj)

        return bundle

    def _get_full_title(self, category):
        titles = [category.title]

        while category.tree_parent is not None:
            category = category.tree_parent
            titles.append(category.title)

        titles.reverse()
        return " > ".join(titles)

    class Meta(ApiModelResource.Meta):
        queryset = Category.objects.all().order_by('tree_path')
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
    user = fields.ForeignKey(UserResource, 'user', blank=True, null=True, full=True)

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


class ExcludeItemsMixin(object):
    def build_filters(self, filters=None):
        if filters is None:
            filters = {}
        orm_filters = super(ExcludeItemsMixin, self).build_filters(filters)
        if '__custom' not in orm_filters:
            orm_filters['__custom'] = {'filter': [], 'exclude': []}

        if 'excluded_ids' in filters:
            try:
                exclude = [int(one) for one in filters.getlist('excluded_ids')]
            except Exception, e:
                logger.exception(e)
            else:
                orm_filters['__custom']['exclude'].append([Q(id__in=exclude)])
        return orm_filters

    def apply_filters(self, request, applicable_filters):
        custom = applicable_filters.pop('__custom', {})
        semi_filtered = super(ExcludeItemsMixin, self).apply_filters(request, applicable_filters)

        for act, val in custom.items():
            for or_queries in val:
                if act == 'filter':
                    semi_filtered = semi_filtered.filter(reduce(operator.or_, or_queries))
                elif act == 'exclude':
                    semi_filtered = semi_filtered.exclude(reduce(operator.or_, or_queries))
        return semi_filtered


class PhotoResource(ExcludeItemsMixin, MultipartFormDataModelResource):
    authors = fields.ToManyField(AuthorResource, 'authors', full=True, use_in=use_in_clever)
    source = fields.ForeignKey(SourceResource, 'source', blank=True, null=True, full=True, use_in=use_in_clever)
    app_data = fields.DictField('app_data', use_in='detail')

    def dehydrate(self, bundle, *args, **kwargs):
        """Adds absolute URL of image."""
        bundle = super(PhotoResource, self).dehydrate(bundle, *args, **kwargs)

        bundle.data['image'] = bundle.obj.image.url[len(settings.MEDIA_URL):]
        bundle.data['public_url'] = bundle.request.build_absolute_uri(bundle.obj.image.url)

        return bundle

    def hydrate(self, bundle, *args, **kwargs):
        """Rotates image if possible"""
        bundle = super(PhotoResource, self).hydrate(bundle, *args, **kwargs)

        if 'rotate' in bundle.data:
            uploaded_image = bundle.data['image']

            # image already uploaded by previous PATCH
            # image contains only path to uploaded image
            if isinstance(uploaded_image, (basestring,)):
                path = os.path.join(settings.MEDIA_ROOT, uploaded_image)
                image = self._rotate_image(path, bundle.data['rotate'])
                image.save(path)
            else:
                path = self._upload_to(uploaded_image.name)

                # create directory path if neccesary
                directory_path = os.path.dirname(path)
                if not os.path.exists(directory_path):
                    os.makedirs(directory_path)
                image = self._rotate_image(uploaded_image, bundle.data['rotate'])
                image.save(path)

                bundle.data['image'] = ImageFile(open(path, "rb"))
                bundle.obj.image = bundle.data['image']

        return bundle

    def _rotate_image(self, image_file, angle):
        image_file.seek(0)
        image = Image.open(image_file)
        angle = int(angle) % 360
        return image.rotate(-angle) # clockwise rotation

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
            'id': ALL,
            'title': ('exact', 'iexact', 'contains', 'icontains', 'startswith', 'endswith',),
            'description': ('contains', 'icontains', 'startswith', 'endswith',),
            'slug': ('exact', 'iexact', 'contains', 'icontains', 'startswith', 'endswith',),
            'width': ALL,
            'height': ALL,
            'important_top': ALL,
            'important_left': ALL,
            'important_bottom': ALL,
            'important_right': ALL,
            'authors': ALL_WITH_RELATIONS,
            'tags': ALL_WITH_RELATIONS,
            'source': ALL_WITH_RELATIONS,
            'created': ALL,
        }
        ordering = (
            'id',
            'title',
            'slug',
            'width',
            'height',
            'important_top',
            'important_left',
            'important_bottom',
            'important_right',
            'authors',
            'source',
            'created',
        )
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

    def dehydrate(self, bundle, *args, **kwargs):
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


class PublishableResource(ExcludeItemsMixin, ApiModelResource):
    authors = fields.ToManyField(AuthorResource, 'authors', full=True, use_in=use_in_clever)
    category = fields.ForeignKey(CategoryResource, 'category', full=True)
    photo = fields.ForeignKey(PhotoResource, 'photo', blank=True, null=True, full=True)
    source = fields.ForeignKey(SourceResource, 'source', blank=True, null=True, full=True, use_in=use_in_clever)
    app_data = fields.DictField('app_data', use_in=use_in_clever)

    def is_valid(self, bundle):
        bundle.obj.clean()
        return super(PublishableResource, self).is_valid(bundle)

    def dehydrate(self, bundle, *args, **kwargs):
        bundle = super(PublishableResource, self).dehydrate(bundle, *args, **kwargs)

        bundle.data['url'] = bundle.obj.get_domain_url()
        return bundle

    def full_hydrate(self, bundle):
        """
        Given a populated bundle, distill it and turn it back into
        a full-fledged object instance.
        """
        bundle = super(PublishableResource, self).full_hydrate(bundle)

        # hack for reseting Photo
        if "photo" in bundle.data:
            if bundle.data["photo"] is None:
                setattr(bundle.obj, "photo", None)

        return bundle

    def hydrate_app_data(self, bundle):
        """
        update app data, merge each sent namespace w/ existing data
        """
        if bundle.obj and bundle.obj.pk and bundle.data.get('app_data'):
            current_data = bundle.obj.app_data.serialize()
            for key, items in bundle.data['app_data'].items():
                current_data.setdefault(key, {}).update(items)
            bundle.data['app_data'] = current_data
        return bundle

    def _add_state_fields(self, bundle):
        """Adds current state and next allowed states of object."""
        state = get_state(bundle.obj)
        if (((state and state.codename != "published") or not state)
            and bundle.obj and bundle.obj.published):

            set_state(bundle.obj, "published")
            state = get_state(bundle.obj)

        if state:
            bundle.data["state"] = state.codename

        # FIXME: Use correct transition table
        bundle.data["allowed_states"] = State.objects.get_states_choices_as_dict()
        return bundle

    def build_filters(self, filters=None):
        if filters is None:
            filters = {}
        orm_filters = super(PublishableResource, self).build_filters(filters)

        if 'titleslug' in filters:
            titleslug_qs = []
            for bit in filters['titleslug'].split():
                or_queries = [Q(**{orm_lookup: bit}) for orm_lookup in ('title__icontains', 'slug__icontains')]
                titleslug_qs += or_queries

            orm_filters['__custom']['filter'].append(titleslug_qs)

        return orm_filters

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
            'last_updated': ALL,
            'announced': ALL,
            'authors': ALL_WITH_RELATIONS,
            'tags': ALL_WITH_RELATIONS,
            'category': ALL_WITH_RELATIONS,
#            'photo': ALL_WITH_RELATIONS,
            'photo': ALL,
        }
        ordering = (
            'id',
            'title',
            'slug',
            'category',
            'authors',
            'source',
            'published',
            'publish_from',
            'publish_to',
            'static',
            'last_updated',
            'announced',
        )
        public = False


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
        public = False


class RelatedResource(ApiModelResource):
    publishable = fields.ForeignKey(PublishableResource, 'publishable', full=True)
    related = fields.ForeignKey(PublishableResource, 'related', full=True, use_in='detail')

    def hydrate(self, bundle, *args, **kwargs):
        bundle = super(RelatedResource, self).hydrate(bundle, *args, **kwargs)

        parts = bundle.data['related'].split('/')
        bundle.obj.related_ct = get_content_type_for_resource(parts[-3])
        bundle.obj.related_id = int(parts[-2])
        del bundle.data['related']

        return bundle

    class Meta(ApiModelResource.Meta):
        queryset = Related.objects.all()
        # excludes = ('related_id',)
        filtering = {
            'id': ALL,
            'publishable': ALL_WITH_RELATIONS,
            'related': ALL_WITH_RELATIONS,
        }
        public = False


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

    def hydrate(self, bundle, *args, **kwargs):
        """
        Translates content_type name into real Django ContentType object.

        Name of content type is case insensitive and correspond to the name
        of resource.
        """
        bundle.obj.content_type = get_content_type_for_resource(bundle.data['content_type'])

        return super(DraftResource, self).hydrate(bundle, *args, **kwargs)

    def alter_list_data_to_serialize(self, request, bundle):
        """
        Deserializes `data` JSONField into JSON data.
        """
        bundle = super(DraftResource, self).alter_list_data_to_serialize(request, bundle)

        bundle['data'] = [self.__alter_data_to_serialize(one) for one in bundle['data']]
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
        queryset = Article.objects.all()
        public = True


class PositionResource(ApiModelResource):
    category = fields.ForeignKey(CategoryResource, 'category', full=True)

    def full_hydrate(self, bundle):
        """
        Implements support for upload of generic field 'target'.
        Tastypie's support for generic relations is not working now.
        """
        bundle = super(PositionResource, self).full_hydrate(bundle)

        bundle.obj.target = self.resolve_resource_uri(bundle.data['target'])

        return bundle

    def full_dehydrate(self, bundle):
        """
        Implements support for download of generic field 'target'.
        Tastypie's support for generic relations is not working now.
        """
        resource = get_resource_for_object(bundle.obj.target)
        target_bundle = resource.build_bundle(obj=bundle.obj.target,
            request=bundle.request)
        bundle.data['target'] = resource.full_dehydrate(target_bundle)

        return super(PositionResource, self).full_dehydrate(bundle)

    class Meta(ApiModelResource.Meta):
        queryset = Position.objects.all()
        public = False
        filtering = {
            'id': ALL,
            'name': ('exact', 'iexact', 'contains', 'icontains', 'startswith', 'endswith',),
            'category': ALL_WITH_RELATIONS,
            'target': ALL_WITH_RELATIONS,
            'text': ('contains', 'icontains', 'startswith', 'endswith',),
            'box_type': ('exact', 'iexact', 'contains', 'icontains', 'startswith', 'endswith',),
            'active_from': ALL,
            'active_till': ALL,
            'disabled': ALL,
        }
        ordering = (
            'id',
            'name',
            'category',
            'target',
            'box_type',
            'active_from',
            'active_till',
        )
