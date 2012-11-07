from django.contrib.contenttypes.models import ContentType


__RESOURCE_CLASSES = []
__REGISTERED_RESOURCES = {}


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

def get_all_resource_content_types():
    return tuple(ContentType.objects.get_for_model(r._meta.object_class)
        for r in __REGISTERED_RESOURCES.values())


def get_all_resource_classes():
    return tuple(__RESOURCE_CLASSES)
