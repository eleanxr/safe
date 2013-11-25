from django.conf.urls import patterns, url

from filestore import views

urlpatterns = patterns('',
    url(r'^$', views.list_files, name="list_files"),
    url(r'^login/$', views.loginpage, name='login'),
    url(r'^do_login/$', views.do_login, name='do_login'),
    url(r'^userinfo/$', views.userinfo, name='userinfo'),
    url(r'^add', views.addkey, name='addkey'),
    url(r'^upload$', views.upload_file, name='upload')
)
