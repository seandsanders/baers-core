from django.shortcuts import render, redirect
from django.conf import settings
import applications as appmodule
from django.db import transaction
from applications.models import Application, Answer, Comment, DoctrineShipGroup, ShipRequiredSkill, TrialComment
from datetime import datetime
from django.http import HttpResponseNotFound, HttpResponse, HttpResponseForbidden
from core.models import CharacterSkill, Character, Notification, UserProfile
from core.views import isRecruiter, isHR, isFullMember
from django.db.models import Count
import random, string
from django.views.decorators.csrf import csrf_exempt
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import Group
from django.utils.text import slugify
from xml.etree import ElementTree
import os
# Create your views here.
from models import TrialVote


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

	return apply_common(request, app)


def apply_anonymous(request):
	if not request.user.is_authenticated():
		return redirect("core:register")

	try:
		app = request.user.userprofile.application
		if app.status != Application.OFFERED:
			return redirect("applications:mystatus")
	except ObjectDoesNotExist:
		sample = string.lowercase+string.digits
		token = ''.join(random.sample(sample, 5))
		app = Application(token=token, applicantProfile=request.user.userprofile)
		app.save()
		c = Comment(app=app, author=request.user.userprofile, date=datetime.utcnow(), text="Started Application", auto_generated=True)
		c.save()

	return apply_common(request, app)


def apply_common(request, app):
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
	r = []
	for group in DoctrineShipGroup.objects.all().prefetch_related('doctrineships', 'doctrineships__skills', 'doctrineshipgrouprequiredskill_set'):
		g = {
			"group": group.name,
			"ships": []
		}
		char_set = profile.character_set.all()
		for skill in group.doctrineshipgrouprequiredskill_set.all():
			char_set = char_set.filter(characterskill__typeID=skill.skillID, characterskill__level__gte=skill.level)
		for ship in group.doctrineships.all():
			chars = char_set.all()
			for skill in ship.skills.all():
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

		skills = dict(character.characterskill_set.values_list('typeID', 'level'))
		nSkills=0
		completed=0
		missing = []

		for skill in plan:
			if skill.tag != 'entry':
				continue
			nSkills+=1
			skillID = int(skill.attrib['skillID'])
			if skillID in skills.keys() and skills[skillID] >= int(skill.attrib['level']):
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


def trialList(request):
	if not isFullMember(request.user):
		return render(request, 'error.html', {'title': '403 - Forbidden', 'description': 'Only Full Members can access this page.'})

	ctx = {}
	ctx['current'] = UserProfile.objects.filter(mainChar__charactertitle__titleName=settings.TRIAL_MEMBER_TITLE)
	ctx['past'] = [] #todo

	return render(request, 'triallist.html', ctx)


def trialDetails(request, profileID):
	if not isFullMember(request.user):
		return render(request, 'error.html', {'title': '403 - Forbidden', 'description': 'Only Full Members can access this page.'})

	trial_profile = UserProfile.objects.get(pk=profileID)
	if request.method == "POST":
		if request.POST.get('newComment', False):
			text = request.POST.get('commentbody')
			if text and text.strip():
				c = TrialComment()
				c.text = text.strip()
				c.author = request.user.userprofile
				c.date = datetime.utcnow()
				c.trial_member = trial_profile.user
				c.save()
		elif request.POST.get('yes', False):
			vote, created = TrialVote.objects.get_or_create(voter=request.user, trial_member=trial_profile.user)
			vote.approve = True
			vote.save()
		elif request.POST.get('no', False):
			vote, created = TrialVote.objects.get_or_create(voter=request.user, trial_member=trial_profile.user)
			vote.approve = False
			vote.save()
	ctx = {}
	ctx['trial_user'] = trial_profile
	ctx['user_comments'] = TrialComment.objects.filter(author=request.user.userprofile, trial_member=trial_profile.user)

	try:
		ctx['user_vote'] = TrialVote.objects.get(voter=request.user, trial_member=trial_profile.user)
	except TrialVote.DoesNotExist:
		pass

	if isRecruiter(request.user):
		ctx['admin'] = True
		ctx['yes_votes'] = TrialVote.objects.filter(trial_member=trial_profile.user, approve=True)
		ctx['no_votes'] = TrialVote.objects.filter(trial_member=trial_profile.user, approve=False)
		ctx['all_comments'] = TrialComment.objects.filter(trial_member=trial_profile.user)
	return render(request, 'trialdetails.html', ctx)