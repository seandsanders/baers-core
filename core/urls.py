from django.conf.urls import include, url
from core import views, evesso

urlpatterns = [
	url(r'^$', views.landing, name="landing"),
	url(r'^dashboard/$', views.dashboard, name="dashboard"),
	url(r'^evesso.*', evesso.ssologin, name="evesso"),
	url(r'^logout$', views.logout, name="logout"),
	url(r'^register$', views.register, name="register"),
	url(r'^keys$', views.apiKeys, name="keys"),
	url(r'^profile/(?P<profileName>.*)$', views.playerProfile, name="playerProfile"),
	url(r'^profile', views.myProfile, name="myProfile"),
	url(r'^search$', views.searchProfile, name="searchProfile"),
]