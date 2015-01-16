from django.conf.urls import include, url
from core import views, evesso

urlpatterns = [
	url(r'^$', views.landing, name="landing"),
	url(r'^dashboard/$', views.dashboard, name="dashboard"),
	url(r'^evesso.*', evesso.ssologin, name="evesso"),
]