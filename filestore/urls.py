from django.conf.urls import patterns, url

from filestore import views

urlpatterns = patterns('',
    url(r'^login/$', views.login, name='login'),
    url(r'^do_login/$', views.do_login, name='do_login'),
    url(r'^userinfo/$', views.user_key, name='userinfo')
)
