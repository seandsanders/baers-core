from django import template
from applications.models import Application
from srp.models import SRPRequest

register = template.Library() 

@register.simple_tag(name='get_apps') 
def get_apps(): 
	return len(Application.objects.filter(status=Application.UNPROCESSED))

@register.simple_tag(name='get_srps') 
def get_srps(): 
	return len(SRPRequest.objects.filter(status=Application.PENDING))
