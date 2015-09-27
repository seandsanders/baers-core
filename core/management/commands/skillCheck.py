from django.core.management.base import BaseCommand

from core.models import UserProfile
from django.utils.text import slugify

class Command(BaseCommand):
    args = ''
    help = 'Prints out a list of people that have not yet completed the skill plans'

    def handle(self, *args, **options):
		skillCheck()

def skillCheck():
	from applications.views import compareSkillplans	


	nostage1 = []
	nostage0 = []
	profiles = UserProfile.objects.filter(user__groups__name="Member")

	for p in profiles:
		highest0 = 0
		highest1 = 0
		for c in p.character_set.all():
			sp = compareSkillplans(c)
			for skillplan in sp:
				if skillplan["name"] == "Stage 0":
					if skillplan["prct"] > highest0:
						highest0 = skillplan["prct"]
				elif skillplan["name"] == "Stage 1":
					if skillplan["prct"] > highest1:
						highest1 = skillplan["prct"]
		if highest0 < 100:
			nostage0.append([p, highest0])
		if highest1 < 100:
			nostage1.append([p, highest1])

	print "Users that do not have Stage 0"
	for u in nostage0:
		print str(u[1])+"%	"+str(u[0])+"	"+"http://dropbearsanonymo.us/profile/"+slugify(u[0])

	print "Users that do not have Stage 1"	
	for u in nostage1:
		print str(u[1])+"%	"+str(u[0])+"	"+"http://dropbearsanonymo.us/profile/"+slugify(u[0])