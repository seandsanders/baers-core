from django.conf.urls import include, url
from subreddit import views

urlpatterns = [
	url(r'^$', views.reddit, name="reddit"),
]