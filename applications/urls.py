from django.conf.urls import include, url
from applications import views

urlpatterns = [
	url(r'^$', views.applications, name="applications"),
	url(r'^apply/(?P<token>.*)$', views.apply, name="apply"),
	url(r'^myapp$', views.mystatus, name="mystatus"),
	url(r'^new$', views.newApplication, name="newapp"),
	url(r'(?P<app>[A-z0-9]*)$', views.application, name="viewapp"),
]