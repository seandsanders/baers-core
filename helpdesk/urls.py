from django.conf.urls import include, url
from helpdesk import views

urlpatterns = [
    url(r'add$', views.ticketSubmit, name="ticketsubmit"),
    url(r'admin$', views.ticketAdmin, name="ticketadmin"),
    url(r'^$', views.ticketList, name="ticketlist"),
    url(r'(?P<token>[0-9a-z]*)$', views.viewTicket, name="viewticket"),
]