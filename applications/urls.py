from django.conf.urls import include, url
from applications import views
from django.conf import settings

urlpatterns = [
	url(r'^$', views.applications, name="applications"),
	url(r'^myapp$', views.mystatus, name="mystatus"),
	url(r'^checkplan/(?P<characterID>.*)$', views.checkPlan, name="ajaxskillplan"),
	url(r'^triallist$', views.trialList, name="triallist"),
	url(r'^trial/(?P<profileID>.*)$', views.trialDetails, name="trialdetails")
]

if settings.ALLOW_ANONYMOUS_APP:
	urlpatterns.append(url(r'^apply$', views.apply_anonymous, name="apply"))
else:
	urlpatterns.append(url(r'^apply/(?P<token>.*)$', views.apply, name="apply"))
	urlpatterns.append(url(r'^new$', views.newApplication, name="newapp"))

urlpatterns.append(url(r'(?P<app>[A-z0-9]*)$', views.application, name="viewapp"))