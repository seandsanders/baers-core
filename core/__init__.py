from django.contrib.auth.models import User, Group
from core.models import Notification, ApiKey, Character
import eveapi
from core.tasks import Task

def postNotification(target, text, cssClass="info"):
	n = Notification(content = text, cssClass=cssClass)
	n.save()

	if type(target) is User:
		n.targetUsers.add(target)
	elif type(target) is Group:
		n.targetGroup.add(target)

#Task("TEST WARNING TASK", cssClass="warning")
#Task("TEST DANGER TASK", cssClass="danger")
#Task("TEST SUCCESS TASK", cssClass="success")

