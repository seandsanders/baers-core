from django import template
from applications.models import Application
from srp.models import SRPRequest
from timerboard.models import Timer
from datetime import datetime, timedelta
from django.conf import settings as djsettings
from applications.views import compareSkillplans

register = template.Library() 

@register.simple_tag(name='get_apps') 
def get_apps(): 
	l = len(Application.objects.filter(status=Application.UNPROCESSED))
	return "" if l==0 else l

@register.simple_tag(name='get_srps') 
def get_srps(): 
	l = len(SRPRequest.objects.filter(status=SRPRequest.PENDING))
	return "" if l==0 else l

@register.simple_tag(name='get_timers')
def get_timers():
	l = len(Timer.objects.filter(time__gte=datetime.utcnow()))
	return "" if l==0 else l

@register.inclusion_tag("tags/linklist.html", name="get_links")
def get_links():
	return {'links': djsettings.USEFUL_LINKS}

@register.inclusion_tag("tags/skillplans.html", name="skillplans")
def skillplans(character):
	return {'result': compareSkillplans(character), 'character': character}

@register.inclusion_tag("tags/timezones.html", name="timezones")
def timezones():
	return {'ustz': datetime.utcnow()-timedelta(hours=7), 'eutz': datetime.utcnow(), 'autz': datetime.utcnow()+timedelta(hours=10)}

@register.inclusion_tag("tags/plot.html", name="plot")
def plot(name, data):
	return {'name': name, 'data': data}
