from django import template
from django.conf import settings
from django.contrib.auth.models import Group 

register = template.Library() 

@register.filter(name='has_group') 
def has_group(user, group_name): 
	group = Group.objects.get_or_create(name=group_name)
	if user is None:
		return False
	return group[0] in user.groups.all()

@register.filter(name='is_full_member')
def is_full_member(user):
	return user.groups.filter(name='Member').exists() and \
			user.userprofile.mainChar.charactertitle_set.filter(titleName=settings.FULL_MEMBER_TITLE).exists()