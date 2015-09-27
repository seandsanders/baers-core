from django.core.management.base import BaseCommand
from django.contrib.auth.models import User,Group
from core.models import UserProfile

class Command(BaseCommand):
    args = ''
    help = 'Adds all groups to the first UserProfile in the database.'

    def handle(self, *args, **options):
    	user = UserProfile.objects.first().user
    	for g in Group.objects.all():
    		user.groups.add(g)

    	print "Added all groups to ", user