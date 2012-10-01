"""
Resources for ella-wikipages application.
gitolite@git.smdev.cz:ella-wikipages
"""

from tastypie import fields
from ella_wikipages.models import Wikipage
from ella_hub.ella_resources import PublishableResource


class WikipageResource(PublishableResource):
    publishables = fields.ToManyField(PublishableResource, "publishables",
        full=True)

    class Meta(PublishableResource.Meta):
        queryset = Wikipage.objects.all()
        public = True
