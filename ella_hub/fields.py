from django.utils import six

from tastypie import fields
from tastypie.bundle import Bundle
from tastypie.exceptions import ApiFieldError


class BackportedForeignKey(fields.ForeignKey):
    """
    Used ForeignKey with fixed implementation of build_related_resource
    from tastypie 0.13 version
    """

    def build_related_resource(self, value, request=None, related_obj=None, related_name=None):
            """
            Returns a bundle of data built by the related resource, usually via
            ``hydrate`` with the data provided.
            Accepts either a URI, a data dictionary (or dictionary-like structure)
            or an object with a ``pk``.
            """
            fk_resource = self.to_class()
            kwargs = {
                'request': request,
                'related_obj': related_obj,
                'related_name': related_name,
            }

            if isinstance(value, Bundle):
                # Already hydrated, probably nested bundles. Just return.
                return value
            elif isinstance(value, six.string_types):
                # We got a URI. Load the object and assign it.
                return self.resource_from_uri(fk_resource, value, **kwargs)
            elif isinstance(value, dict):
                # We've got a data dictionary.
                # Since this leads to creation, this is the only one of these
                # methods that might care about "parent" data.
                return self.resource_from_data(fk_resource, value, **kwargs)
            elif hasattr(value, 'pk'):
                # We've got an object with a primary key.
                return self.resource_from_pk(fk_resource, value, **kwargs)
            else:
                raise ApiFieldError("The '%s' field was given data that was not a URI, not a dictionary-alike and does not have a 'pk' attribute: %s." % (self.instance_name, value))
