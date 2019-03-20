from django.conf.urls import *#patterns, include, url
import views

urlpatterns = [
    # url(r'^admin/', include(admin.site.urls)),
    url(r'^login/', views.login),
    url(r'', views.checkSignature)
]
