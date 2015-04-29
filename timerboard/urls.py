from django.conf.urls import include, url
from timerboard import views

urlpatterns = [
	url(r'^note$', views.updateNote, name="updatenote"),
	url(r'^$', views.timerboard, name="timerboard"),
]