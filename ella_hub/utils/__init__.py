import os
import logging

from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from ella.photos.models import Format

from ella_hub import conf


logger = logging.getLogger(__name__)

__RESOURCE_CLASSES = []
__REGISTERED_RESOURCES = {}


# get format for thumbnail
THUMB_FORMAT = None
if conf.THUMBNAIL_FORMAT is not None:
    try:
        THUMB_FORMAT = Format.objects.get_for_name(conf.THUMBNAIL_FORMAT)
    except Format.DoesNotExist:
        logger.warning("Format for thumbnail with name: %s does not exist" % conf.THUMBNAIL_FORMAT)


def save_resource_class(cls):
    __RESOURCE_CLASSES.append(cls)


def save_registered_resource(resource):
    __REGISTERED_RESOURCES[resource._meta.resource_name] = resource


def get_resource_by_name(resource_name):
    return __REGISTERED_RESOURCES[resource_name]


def get_content_type_for_resource(resource_name):
    resource = __REGISTERED_RESOURCES[resource_name]
    return ContentType.objects.get_for_model(resource._meta.object_class)


def get_resource_model(resource_name):
    """Returns DB model for give resource name."""
    resource = __REGISTERED_RESOURCES[resource_name]
    return resource._meta.object_class


def get_resource_for_object(instance):
    """
    Returns resource for given model or `None` if resource is not found.
    """
    for resource in __REGISTERED_RESOURCES.values():
        if isinstance(instance, resource._meta.object_class):
            return resource


def get_all_resource_content_types():
    return tuple(
        ContentType.objects.get_for_model(r._meta.object_class)
        for r in __REGISTERED_RESOURCES.values()
    )


def get_all_resource_classes():
    return tuple(__RESOURCE_CLASSES)


def get_model_name_from_class(cls):
    opts = cls._meta
    return hasattr(opts, 'model_name') and opts.model_name or opts.module_name


def get_media_drafts_root():
    return os.path.join(
        settings.MEDIA_ROOT,
        conf.MEDIA_DRAFTS_DIR
    )
