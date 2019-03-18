from django.conf.urls import patterns, include, url
import views

urlpatterns = patterns('',
    # Examples:
    # url(r'^interfacedefmanage',views.inDefManage),
     url(r'^login', views.login),
    
)
