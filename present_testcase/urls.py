from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^detail/$', views.detail, name='detail'),
    url(r'^about/$', views.about, name='about'),
    url(r'^predict/$', views.predict, name='predict'),
    url(r'^$', views.index, name='index'),
]