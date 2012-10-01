__REGISTERED_RESOURCES = {}


def save_registered_resource(resource):
    __REGISTERED_RESOURCES[resource._meta.resource_name] = resource


def get_model_name_of_resource(resource_name):
    """Returns name of DB model for given resource name."""
    resource = __REGISTERED_RESOURCES[resource_name]
    return resource._meta.object_class.__name__.lower()


def get_all_resource_model_names():
    return tuple(r._meta.object_class.__name__.lower()
        for r in __REGISTERED_RESOURCES.values())
