from django.conf.urls import include, url
from srp import views

urlpatterns = [
	url(r'^$', views.submit, name="submit"),
	url(r'admin$', views.srpadmin, name="srpadmin"),
	url(r'list$', views.srplist, name="srplist"),
	url(r'(?P<killID>[0-9]*)$', views.viewsrp, name="viewsrp"),
]