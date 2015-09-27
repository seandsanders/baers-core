from django import template
from django.contrib.auth.models import Group 

register = template.Library() 

@register.filter(name='has_group') 
def has_group(user, group_name): 
	group = Group.objects.get_or_create(name=group_name)
	if user == None:
		return False
	return group[0] in user.groups.all()
