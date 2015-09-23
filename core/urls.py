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
	url(r'^memberlist$', views.memberList, name="memberlist"),
	url(r'^pos$', views.starbases, name="poslist"),
	url(r'^pos/update$', views.updateNote, name="updatepos"),
	url(r'^pos/updateowner$', views.updateOwner, name="updateowner"),
	url(r'^listgroups', views.groupList, name="grouplist"),
	url(r'^capcensus', views.capCensus, name="capcensus"),
	url(r'^updatetz', views.updateTZ, name='updateTZ'),
	url(r'^theme', views.changeTheme, name="changeTheme"),
	url(r'^accounting', views.accounting, name="accounting"),
	url(r'^assetscan/(?P<itemID>[0-9]*)$', views.assetScan, name="assetexpand"),
	url(r'^assetscan', views.assetScan, name="assetscan"),
	url(r'^iskoverview', views.iskOverview, name="iskoverview")
]