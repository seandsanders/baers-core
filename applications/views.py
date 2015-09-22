from django.shortcuts import render, redirect
import applications as appmodule
from django.db import transaction
from applications.models import Application, Answer, Comment
from datetime import datetime
from django.http import HttpResponseNotFound, HttpResponse, HttpResponseForbidden
from core.models import CharacterSkill, Character, Notification
from core.views import isRecruiter, isHR
from django.db.models import Count
import random, string
from django.views.decorators.csrf import csrf_exempt
from django.core.urlresolvers import reverse
from django.contrib.auth.models import Group
from django.utils.text import slugify
from xml.etree import ElementTree
import os
# Create your views here.

ships = [
		{
			"group": "Grizzly Fleet",
			"ships": [
				{
					"name": "Augoror",
					"shipID": 625,
					"skills": [(3335, 1), (16069, 1), (3423, 1)]
				},
				{
					"name": "Exequror",
					"shipID": 634,
					"skills": [(3332, 1), (16069, 1)]
				},
				{
					"name": "Prophecy",
					"shipID": 16233,
					"skills": [(33095, 1), (3423, 1)]
				},
				{
					"name": "Vigilant",
					"shipID": 17722,
					"skills": [(3333, 1),(3332, 1), (3435, 1)]
				},
				{
					"name": "Armageddon",
					"shipID": 643,
					"skills": [(3339, 1), (3423, 1)]
				},
				{
					"name": "Bhaalgorn",
					"shipID": 17920,
					"skills": [(3339, 1), (3337, 1), (3423, 1)]
				},
				{
					"name": "ANI",
					"shipID": 29337,
					"skills": [(3335, 1), (3306, 1)]
				},
				{
					"name": "Legion",
					"shipID": 29986,
					"skills": [(3335, 5), (3423, 1), (30650, 1)]
				},
				{
					"name": "Tengu",
					"shipID": 29984,
					"skills": [(3334, 5), (30651, 1), (3427, 1)]
				},
				{
					"name": "Loki",
					"shipID": 29990,
					"skills": [(3333, 5), (3305, 1), (30653, 1)]
				},
				{
					"name": "Proteus",
					"shipID": 29988,
					"skills": [(3332, 5), (3304, 1), (30652, 1)]
				},
				{
					"name": "Guardian",
					"shipID": 11987,
					"skills": [(3335, 5), (16069, 1), (3423, 1), (12096, 4)]
				}
			]
		},
		{
			"group": "Gaytars",
			"ships": [
				{
					"name": "Scythe",
					"shipID": 631,
					"skills": [(3333, 1), (3422, 1)]
				},
				{
					"name": "Gila",
					"shipID": 17715,
					"skills": [(3332, 1),(3334, 1),(3319, 1),(3437,1)]
				},
				{	
					"name": "Caracal",
					"shipID": 621,
					"skills": [(3334, 1), (3319, 1)]
				},
				{	
					"name": "Ishtar",
					"shipID": 12005,
					"skills": [(3332, 5), (23594, 1), (16591, 1)]
				},
				{	
					"name": "Scimitar",
					"shipID": 11978,
					"skills": [(3333, 5), (3422, 1), (12096, 4)]
				},
				{	
					"name": "Cerberus",
					"shipID": 11993,
					"skills": [(3334, 5), (16591, 1), (3319, 1)]
				},
				{	
					"name": "Vagabond",
					"shipID": 11999,
					"skills": [(3333, 5), (16591, 1), (3305, 1)]
				}
			]
		},
		{
			"group": "Utility",
			"ships": [
				{
					"name": "Falcon",
					"shipID": 11957,
					"skills": [(3334, 5), (22761, 1),  (3427, 1)]
				},
				{
					"name": "Rook",
					"shipID": 11959,
					"skills": [(3334, 5), (22761, 1),  (3427, 1)]
				},
				{
					"name": "Curse",
					"shipID": 20125,
					"skills": [(3335, 5), (22761, 1), (3423, 1)]
				},
				{
					"name": "Pilgrim",
					"shipID": 11965,
					"skills": [(3335, 5), (22761, 1), (3423, 1)]
				},
				{
					"name": "Lachesis",
					"shipID": 11971,
					"skills": [(3332, 5), (22761, 1), (3435, 1)]
				},
				{
					"name": "Arazu",
					"shipID": 11969,
					"skills": [(3332, 5), (22761, 1), (3435, 1)]
				},
				{
					"name": "Hugin",
					"shipID": 11961,
					"skills": [(3333, 5), (22761, 1), (3435, 1)]
				},
				{
					"name": "Rapier",
					"shipID": 11963,
					"skills": [(3333, 5), (22761, 1), (3435, 1)]
				},
				{
					"name": "Crow",
					"shipID": 11176,
					"skills": [(3330, 5),(12092, 1)]
				},
				{
					"name": "Raptor",
					"shipID": 11178,
					"skills": [(3330, 5),(12092, 1)]
				},
				{
					"name": "Stiletto",
					"shipID": 11198,
					"skills": [(3329, 5),(12092, 1)]
				},
				{
					"name": "Claw",
					"shipID": 11196,
					"skills": [(3329, 5),(12092, 1)]
				},
				{
					"name": "Ares",
					"shipID": 11202,
					"skills": [(3328, 5),(12092, 1)]
				},
				{
					"name": "Taranis",
					"shipID": 11200,
					"skills": [(3328, 5),(12092, 1)]
				},
				{
					"name": "Crusader",
					"shipID": 11184,
					"skills": [(3331, 5),(12092, 1)]
				},
				{
					"name": "Malediction",
					"shipID": 11186,
					"skills": [(3331, 5),(12092, 1)]
				},
				{
					"name": "Flycatcher",
					"shipID": 22464,
					"skills": [(33092, 5), (12098, 1)]
				},
				{
					"name": "Sabre",
					"shipID": 22456,
					"skills": [(33094, 5), (12098, 1)]
				},
				{
					"name": "Heretic",
					"shipID": 22452,
					"skills": [(33091, 5), (12098, 1)]
				},
				{
					"name": "Eris",
					"shipID": 22460,
					"skills": [(33093, 5), (12098, 1)]
				},
				{
					"name": "Phobos",
					"shipID": 12021,
					"skills": [(3332, 5), (28609, 1)]
				},
				{
					"name": "Devoter",
					"shipID": 12017,
					"skills": [(3335, 5), (28609, 1)]
				},
				{
					"name": "Broadsword",
					"shipID": 12013,
					"skills": [(3333, 5), (28609, 1)]
				},
				{
					"name": "Onyx",
					"shipID": 11995,
					"skills": [(3334, 5), (28609, 1)]
				},
				{
					"name": "Providence",
					"shipID": 20183,
					"skills": [(20524, 1), (20342, 1)]
				},
				{
					"name": "Ark",
					"shipID": 28850,
					"skills": [(20524, 4), (29029, 1), (21611, 1)]
				},
				{
					"name": "Nomad",
					"shipID": 28846,
					"skills": [(20528, 4), (29029, 1), (21611, 1)]
				},
				{
					"name": "Fenrir",
					"shipID": 20189,
					"skills": [(20528, 1), (20342, 1)]
				},
				{
					"name": "Obelisk",
					"shipID": 20187,
					"skills": [(20527, 1), (20342, 1)]
				},
				{
					"name": "Anshar",
					"shipID": 28848,
					"skills": [(20527, 4), (29029, 1), (21611, 1)]
				},
				{
					"name": "Charon",
					"shipID": 20185,
					"skills": [(20526, 1), (20342, 1)]
				},
				{
					"name": "Rhea",
					"shipID": 28844,
					"skills": [(20526, 4), (29029, 1), (21611, 1)]
				}
			]
		},
		{
			"group": "Capitals",
			"ships": [
				{
					"name": "Archon",
					"shipID": 23757,
					"skills": [(24311, 1),(21803, 1), (24568, 1), (24572, 1), (27906, 1)]
				},
				{
					"name": "Revelation",
					"shipID": 19720,
					"skills": [(20525, 1),(21803, 1), (22043, 1), (20327, 1)]
				},
				{
					"name": "Aeon",
					"shipID": 23919,
					"skills": [(24311, 1),(21803, 1), (24568, 1), (32339, 1)]
				},
				{
					"name": "Avatar",
					"shipID": 11567,
					"skills": [(3347, 1), (21803, 1), (20327, 1), (24563, 1)]
				},
				{
					"name": "Thanatos",
					"shipID": 23911,
					"skills": [(24313, 1),(23069, 1), (21803, 1), (24568, 1)]
				},
				{
					"name": "Armor Moros",
					"shipID": 19724,
					"skills": [(20531, 1),(21803, 1), (22043, 1), (21666, 1)]
				},
				{
					"name": "Shield Moros",
					"shipID": 19724,
					"skills": [(20531, 1),(21802, 1),(22043, 1), (21666, 1)]
				},
				{
					"name": "Nyx",
					"shipID": 23913,
					"skills": [(24313, 1),(21803, 1), (24568, 1), (24572, 1), (32339, 1)]
				},
				{
					"name": "Erebus",
					"shipID": 671,
					"skills": [(3344, 1),(21666, 1), (24563, 1)]
				},
				{
					"name": "Nidhoggur",
					"shipID": 24483,
					"skills": [(24314, 1),(27906, 1)]
				},
				{
					"name": "Armor Naglfar",
					"shipID": 19722,
					"skills": [(20532, 1),(21803, 1), (22043, 1), (21667, 1)]
				},
				{
					"name": "Shield Naglfar",
					"shipID": 19722,
					"skills": [(20532, 1),(21802, 1),(22043, 1), (21667, 1)]
				},
				{
					"name": "Hel",
					"shipID": 22852,
					"skills": [(24314, 1),(21803, 1), (24568, 1), (24572, 1), (32339, 1)]
				},
				{
					"name": "Ragnarok",
					"shipID": 23773,
					"skills": [(3345, 1),(21667, 1), (24563, 1)]
				},
				{
					"name": "Chimera",
					"shipID": 23915,
					"skills": [(24312,1),(21802, 1), (27906, 1)]
				},
				{
					"name": "Phoenix",
					"shipID": 19726,
					"skills": [(20530, 1),(21802, 1), (22043, 1)]
				},
				{
					"name": "Wyvern",
					"shipID": 23917,
					"skills": [(24312,1),(21802, 1), (32339, 1)]
				},
				{
					"name": "Leviathan",
					"shipID": 3764,
					"skills": [(3346, 1),(21802, 1), (24563, 1)]
				}
			]
		}
	]

def apply(request, token):
	if not request.user.is_authenticated():
		request.session['appToken'] = token
		return redirect("core:register")

	try:
		app = Application.objects.get(token=token)
	except:
		app = False

	if not app:
		return render(request, 'error.html', {'title': '404 - Page not found', 'description': token+' is not a valid application token.'})

	if (app.status > 0):
		return redirect("applications:mystatus")

	if request.method == "POST":
		count = 1
		answers = []
		for q in appmodule.questions:
			answer = Answer(app=app, question=q["text"], text=request.POST.get("q"+unicode(count)))
			answers.append(answer)
			count+=1
		app.status = 1
		app.timezone=request.POST.get('tz')
		app.applicantProfile = request.user.userprofile		
		app.applicationDate = datetime.utcnow()
		app.save()
		recruiter = Group.objects.filter(name="Recruiter").first()
		note = Notification(cssClass="success")
		note.content="New Application from <a href='"+reverse('applications:viewapp', kwargs={"app": app.token})+"'>"+unicode(request.user.userprofile)+"</a>."
		note.save()
		note.targetGroup.add(recruiter)

		Answer.objects.bulk_create(answers)

		return redirect("applications:mystatus")


	else:
		return render(request, "apply.html", {"questions": appmodule.questions})


def mystatus(request):
	c = {"app": request.user.userprofile.application, "pos": len(Application.objects.filter(status=Application.UNPROCESSED, id__lte=request.user.userprofile.application.id))}
	if c["app"].status == Application.UNPROCESSED:
		if c["app"].tag in [Application.CLEAN, Application.SUSPICIOUS, Application.NOTES]:
			c["status"] = "In Progress"
		elif c["app"].tag in [Application.INTERVIEW]:
			c["status"] = "Ready for Interview"

	return render(request, 'appstatus.html', c)

def application(request, app):
	if not isRecruiter(request.user):
		return render(request, 'error.html', {'title': '403 - Forbidden', 'description': 'You are not a recruiter.'})

	hr = isHR(request.user)
	app = Application.objects.filter(token=app).first()

	if app.status == Application.ACCEPTED and not hr:
		return render(request, 'error.html', {'title': '403 - Forbidden', 'description': 'For privacy reasons, only HR officers can view accepted applications.'})

	if request.method == "POST":
		if request.POST.get('newComment'):
			c = Comment()
			c.text = request.POST.get('commentbody')
			c.author = request.user.userprofile
			c.date = datetime.utcnow()
			c.auto_generated = False
			c.app = app
			c.save()
			recruiter = Group.objects.filter(name="Recruiter").first()
			note = Notification(cssClass="info")
			note.content="<a href='"+reverse('core:playerProfile', kwargs={"profileName": slugify(request.user.userprofile)})+"'>"+unicode(c.author)+"</a> commented on <a href='"+reverse('applications:viewapp', kwargs={"app": app.token})+"'>"+unicode(app.applicantProfile)+"'s Application</a>."
			note.save()
			note.targetGroup.add(recruiter)
		if request.POST.get('updatestatus'):
			newStatus = int(request.POST.get('status'))
			newTag = int(request.POST.get('tag'))
			if app.status != newStatus and app.STATUS_CHOICES[newStatus]:
				c = Comment(auto_generated=True, date=datetime.utcnow(), app=app, author=request.user.userprofile)
				oldstatus = app.get_status_display()
				app.status = newStatus 
				c.text = "changed Status from '"+oldstatus+"' to '"+app.get_status_display()+"'"
				c.save()
				if newStatus == Application.ACCEPTED:
					Group.objects.get(name='Member').user_set.add(app.applicantProfile.user)
				else:
					Group.objects.get(name='Member').user_set.remove(app.applicantProfile.user)
			if app.tag != newTag and app.TAG_CHOICES[newTag]:
				c = Comment(auto_generated=True, date=datetime.utcnow(), app=app, author=request.user.userprofile)
				oldtag = app.get_tag_display()
				app.tag = newTag
				c.text = "changed Tag from '"+oldtag+"' to '"+app.get_tag_display()+"'"
				c.save()
			app.save()


	profile = app.applicantProfile
	keys = profile.apikey_set.all()
	characters = profile.character_set.all()
	answers = app.answer_set.all()

	r = getFlyable(profile)
	c = {
		"app": app,
		"profile": profile,
		"keys": keys,
		"answers": answers,
		"ships": r,
		"skills": compareSkillplans(profile.mainChar)
	}
	return render(request, "application.html", c)

def getFlyable(profile):
	skills = CharacterSkill.objects.all()
	r = []
	for group in ships:
		g = {
			"group": group["group"],
			"ships": []
		}
		for ship in group["ships"]:
			chars = profile.character_set
			for skill in ship["skills"]:
				chars = chars.filter(characterskill__typeID=skill[0], characterskill__level__gte=skill[1])
			g["ships"].append({
				"name": ship["name"],
				"shipID": ship["shipID"],
				"pilots": chars.all()
			})
		r.append(g)
	
	return r	

def applications(request):
	if not isRecruiter(request.user):
		return render(request, 'error.html', {'title': '403 - Forbidden', 'description': 'You are not a recruiter.'})
	apps = Application.objects.all()
	unp = apps.filter(status=Application.UNPROCESSED).order_by('applicationDate')
	hld = apps.filter(status=Application.HOLD).order_by('-applicationDate')
	dnd = apps.filter(status=Application.DENIED).order_by('-applicationDate')
	yes = apps.filter(status=Application.ACCEPTED).order_by('-applicationDate')

	c = {
		"unprocessed": unp,
		"hold": hld,
		"denied": dnd,
		"accepted": yes
	}
	return render(request, "applications.html", c)

@csrf_exempt
def newApplication(request):
	if not isRecruiter(request.user):
		return render(request, 'error.html', {'title': '403 - Forbidden', 'description': 'You are not a recruiter.'})
	sample = string.lowercase+string.digits
	token = ''.join(random.sample(sample, 5))

	app = Application(token=token)
	app.save()
	c = Comment(app=app, author=request.user.userprofile, date=datetime.utcnow(), text="Generated the Token", auto_generated=True)
	c.save()
	return HttpResponse(request.build_absolute_uri(reverse('applications:apply', kwargs={'token':token})))

def compareSkillplans(character):
	result = []

	for filename in sorted(os.listdir('applications/skillplans/')): 

		t = ElementTree.parse('applications/skillplans/'+filename)

		plan = t.getroot()

		skills = character.characterskill_set.filter(owner=character)
		nSkills=0
		completed=0
		missing = []

		for skill in plan:
			if skill.tag != 'entry':
				continue
			nSkills+=1
			skillID = skill.attrib['skillID']
			cskill = skills.filter(typeID=skillID, level__gte=skill.attrib['level'])
			if cskill.exists():
				completed+=1
			else:
				missing.append(skill.attrib)

		result.append({"name": plan.attrib['name'], "completed": completed, "nSkills": nSkills, "missing": missing, "prct": int(100*completed/nSkills)})

	return result

def checkPlan(request, characterID):
	try:
		c = Character.objects.get(charID=characterID)
	except:
		c = False

	if c:
		if not (isRecruiter(request.user) or c.profile.user == request.user):
			return HttpResponseForbidden('<h1>You do not have the permissions to view this character\'s skillplans</h1>')

		return render(request, 'tags/skillplans.html', {'result': compareSkillplans(c), 'character': c})