from django.shortcuts import render, redirect
from django.conf import settings
import applications as appmodule
from django.db import transaction
from applications.models import Application, Answer, Comment, DoctrineShipGroup
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


def apply(request, token):
	if not request.user.is_authenticated():
		request.session['appToken'] = token
		return redirect("core:register")

	try:
		app = Application.objects.get(token=token)
	except:
		app = False

	if not app:
		return render(request, 'error.html',
					  {'title': '404 - Page not found', 'description': token + ' is not a valid application token.'})

	if (app.status > 0):
		return redirect("applications:mystatus")

	if request.method == "POST":
		count = 1
		answers = []
		for q in appmodule.questions:
			answer = Answer(app=app, question=q["text"], text=request.POST.get("q" + unicode(count)))
			answers.append(answer)
			count += 1
		app.status = 1
		app.timezone = request.POST.get('tz')
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
	for group in DoctrineShipGroup.objects.all():
		g = {
			"group": group.name,
			"ships": []
		}
		for ship in group.doctrineship_set.all():
			chars = profile.character_set
			for skill in ship.shiprequiredskill_set.all():
				chars = chars.filter(characterskill__typeID=skill.skillID, characterskill__level__gte=skill.level)
			g["ships"].append({
				"name": ship.name,
				"shipID": ship.shipID,
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
	os.chdir(settings.BASE_DIR)
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