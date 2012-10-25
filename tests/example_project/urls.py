from django.contrib import admin
from django.conf import settings
from django.conf.urls.defaults import patterns, include, url
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from ella_hub.api import EllaHubApi
from ella_hub.utils.workflow import init_ella_workflow

admin.autodiscover()

# admin API setup
admin_api = EllaHubApi('admin-api')
resources = admin_api.collect_resources()
admin_api.register_resources(resources)
init_ella_workflow(resources)


urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include(admin_api.urls)),
    url(r'^', include('ella.core.urls')),
)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += staticfiles_urlpatterns()
