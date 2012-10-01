from django.conf.urls.defaults import patterns, include

from ella_hub.api import EllaHubApi
from ella_hub.utils.workflow import init_ella_workflow

# admin API setup
admin_api = EllaHubApi("admin-api")
resources = admin_api.collect_resources()
admin_api.register_resources(resources)
admin_api.register_view_model_permission()
init_ella_workflow(resources)


urlpatterns = patterns('',
    (r'^', include(admin_api.urls)),
    (r'^', include('ella.core.urls')),
)
