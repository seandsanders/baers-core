from django.conf.urls import include, url
from hipchat import views

urlpatterns = [
	url(r'^$', views.hipchat, name="hipchat"),
	url(r'^list$', views.hipchatlist, name="hipchatlist"),
]