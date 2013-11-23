from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^files/', include('filestore.urls', namespace='filestore')),
    url(r'^admin/', include(admin.site.urls)),
)
