from django.conf.urls import include, url
from skillchecker import views

urlpatterns = [
    url(r'^$', views.skillcheck, name="skillcheck")
]