
from django.conf.urls.defaults import patterns, include

from ella_hub.api import EllaHubApi
api = EllaHubApi(api_name='admin-api')
collected_resources = api.collect_resources()
api.register_resources(collected_resources)
api.register_view_model_permission()

urlpatterns = patterns('',
    (r'^', include(api.urls)),
    (r'^', include('ella.core.urls')),
)
