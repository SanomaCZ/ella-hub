from django.contrib import admin
from django.conf.urls.defaults import patterns, include, url, handler404, handler500
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.generic.simple import direct_to_template

from ella_hub.api import EllaHubApi

admin.autodiscover()

# admin API setup
admin_api = EllaHubApi("admin-api")
resources = admin_api.collect_resources()
admin_api.register_resources(resources)
admin_api.register_view_model_permission()


urlpatterns = patterns('',
    # enable admin
    url(r'^admin/', include(admin.site.urls)),

    (r'^', include(admin_api.urls)),
    (r'^admin-hope/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': 'admin-hope',
        'show_indexes': True,
    }),

    (r'^', include('ella.core.urls')),
) + staticfiles_urlpatterns()
