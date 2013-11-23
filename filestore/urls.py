from django.conf.urls import patterns, url

from filestore import views

urlpatterns = patterns('',
    url(r'^userinfo/$', views.user_key, name='userinfo')
)
