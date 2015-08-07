from django.conf.urls import include, url
from corpmarket import views

urlpatterns = [
	url(r'typeid$', views.resolveTypeID, name="resolveTypeID"),
	url(r'^$', views.list, name="cmlist"),
	url(r'add$', views.add, name="add"),
]