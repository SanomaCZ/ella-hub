from django.conf.urls.defaults import patterns, include, url

from ella_hub.api import EllaHubApi
from ella_hub.utils.workflow import init_ella_workflow

# admin API setup
admin_api = EllaHubApi('admin-api')
resources = admin_api.collect_resources()
admin_api.register_resources(resources)
init_ella_workflow(resources)


urlpatterns = patterns('',
    url(r'^', include(admin_api.urls)),
    url(r'^', include('ella.core.urls')),
)
