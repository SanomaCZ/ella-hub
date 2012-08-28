import ella_hub.api


def get_model_name(resource_name):
    """Returns name of DB model for given resource name."""

    resource = ella_hub.api.EllaHubApi.registered_resources[resource_name]
    return resource._meta.object_class.__name__.lower()
