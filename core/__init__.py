from django.contrib.auth.models import User, Group
from core.models import Notification, ApiKey, Character
from eveapi import eveapi
from core.tasks import Task

def postNotification(target, text, cssClass="info"):
	n = Notification(content = text, cssClass=cssClass)

	n.save()
	if type(target) is User:
		n.targetUsers.add(target)
	elif type(target) is Group:
		n.targetGroup.add(target)
	n.save()

Task("TASKS WILL APPEAR HERE")
#Task("TEST WARNING TASK", cssClass="warning")
#Task("TEST DANGER TASK", cssClass="danger")
#Task("TEST SUCCESS TASK", cssClass="success")

from django import template
from django.contrib.auth.models import Group 

register = template.Library() 

@register.filter(name='has_group') 
def has_group(user, group_name): 
	group = Group.objects.get(name=group_name) 
	return True if group in user.groups.all() else False