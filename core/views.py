from django.shortcuts import render, redirect
from django.db.models import Q
from core.models import Notification, UserProfile, Character, ApiKey, CorpMember
from django.contrib.auth.models import User, Group
from core.apireader import validateKey, refreshKeyInfo
from django.utils.text import slugify
from core import postNotification
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseForbidden
from django.contrib.auth.decorators import user_passes_test
from core.tasks import Task 
from django.core.urlresolvers import reverse
from datetime import datetime

# Create your views here.

def isRecruiter(user):
	return user.groups.filter(name='Recruiter').exists()

def isDirector(user):
	return user.groups.filter(name='Director').exists()

def isDropbear(user):
	return user.groups.filter(name='Dropbears').exists()


def dashboard(request):
	titles = ", ".join(request.user.userprofile.mainChar.charactertitle_set.all().values_list('titleName', flat=True))
	context = {
		"mainCharName": unicode(request.user.userprofile),
		"mainCharID": unicode(request.user.userprofile.mainChar.charID),
		"charTitle": unicode(titles)
	}

	context["notifications"] = Notification.objects.filter(Q(targetUsers=request.user) | Q(targetGroup__in=request.user.groups.all())).order_by('-time')[:20]
	context["tasks"] = Task.getList()

	return render(request, 'dashboard.html', context)


def landing(request):
	context = {}
	if request.user.is_authenticated():
		return redirect("core:dashboard")
	return render(request, 'landing.html', context)


from django.contrib.auth import logout as authLogout

def logout(request):
    authLogout(request)
    return redirect("core:landing")

def register(request):
	ctx = {}
	error = None
	recruiterGrp, created = Group.objects.get_or_create(name='Recruiter')
	if request.method == "POST":
		if request.POST.get("action") == "addkey":
			if request.POST.get("keyID") and request.POST.get("vCode"):
				charlist, error = validateKey(request.POST.get("keyID"), request.POST.get("vCode"))
				if not error:
					if request.session.get("characters"):
						request.session["characters"].extend(charlist)
						request.session.modified = True
					else:
						request.session["characters"] = charlist
					if request.session.get("apis"):
						request.session["apis"].append({"id": request.POST.get("keyID"), "vCode": request.POST.get("vCode")})
						request.session.modified = True
					else:
						request.session["apis"] = [{"id": request.POST.get("keyID"), "vCode": request.POST.get("vCode")}]
		elif request.POST.get("action") == "done":
			if request.session.get("characters"):
				charlist = request.session.get("characters")
				mainChar = request.POST.get("mainChar")

				if mainChar and mainChar != "0":
					mainChar = charlist[int(mainChar)-1]
					newUser = User(username=slugify(mainChar["charName"]))
					from django.db import IntegrityError
					try:
						newUser.save()
					except IntegrityError as e:
						return redirect("core:evesso")

					newProfile = UserProfile.objects.get_or_create(user=newUser)[0]
					try:
						newProfile.save()
					except:
						pass
					for api in request.session["apis"]:
						try:
							newKey = ApiKey.objects.get(keyID=api["id"], deleted=True)
							newKey.deleted = False
							newKey.vCode = api["vCode"]
							newKey.profile = newProfile
						except:
							newKey = ApiKey(keyID = api["id"], vCode=api["vCode"], profile=newProfile)
						newKey.save()
						refreshKeyInfo(newKey, full=False)
					newProfile.mainChar = Character.objects.get(charID=mainChar["charID"])
					try:
						newProfile.save()
					except:
						pass
					postNotification(target=newUser, text="You have created your account", cssClass="success")
					postNotification(target=recruiterGrp, text="<a href='"+reverse('core:playerProfile', kwargs={"profileName": slugify(newProfile)})+"'>"+unicode(newProfile)+" created an account.", cssClass="info")
					return redirect("core:evesso")
				else:
					error = "Please Select your main Character (click it)"
			else:
				error = "Please add API Keys to all of your accounts"


	if (request.session.get("characters")):
		ctx["characters"] = request.session.get("characters")
	ctx["error"] = error

	return render(request, 'register.html', ctx)

def apiKeys(request):
	if not (request.user.is_authenticated()):
		return redirect("core:landing")
	error = None
	recruiterGrp, created = Group.objects.get_or_create(name='Recruiter')
	if request.method == "POST":
		action = request.POST.get('action')
		if action and action == "makemain":
			charID = request.POST.get('characterID')
			if charID:
				try:
					c = Character.objects.get(charID=charID)
					if request.user == c.profile.user:
						c.profile.mainChar = c
						c.profile.save()
				except:
					pass
		elif action and action == "delkey":
			keyID = request.POST.get('keyID')
			if keyID:
				try:
					k = ApiKey.objects.get(keyID=keyID)
					if request.user == k.profile.user:
						k.deleted = True
						k.save()
						postNotification(target=recruiterGrp, text=unicode(request.user.userprofile)+" has deleted an API key.", cssClass="warning")
				except:
					pass
		elif action and action == "addkey":
			keyID = request.POST.get('keyID')
			vCode = request.POST.get('vCode')
			if keyID and vCode:
				charlist, error = validateKey(keyID, vCode)
				if not error:
					try:
						newKey = ApiKey.objects.get(keyID=keyID, deleted=True)
						newKey.deleted = False
						newKey.profile=request.user.userprofile
						newKey.vCode=vCode
					except:
						newKey = ApiKey(keyID = keyID, vCode=vCode, profile=request.user.userprofile)
					newKey.save()
					refreshKeyInfo(newKey, full=False)
					recruiterGrp, created = Group.objects.get_or_create(name='Recruiter')
					postNotification(target=recruiterGrp, text=unicode(newKey.profile)+" has added a new API key.", cssClass="info")
			else:
				error = "Please enter a Key ID and a verification Code"

	apis = request.user.userprofile.apikey_set.filter(deleted=False)
	ctx = {"apis": apis, "error": error}

	return render(request, 'keys.html', ctx)

def myProfile(request):
	if not (request.user.is_authenticated()):
		return redirect("core:landing")
	return profile(request, request.user.userprofile)

def playerProfile(request, profileName):
	if not isDropbear(request.user):
		return HttpResponseForbidden("<h1>Only for current members</h1>")
	def unslugify(name):
		return name.replace("-", " ") 
	try:
		c = Character.objects.get(charName__iexact = unslugify(profileName))
	except:
		return HttpResponseNotFound('<h1>Page not found</h1>')
	return profile(request, c.profile, mark=c)

def searchProfile(request):
	error = None
	searchTerm = request.POST.get('searchterm')
	if not searchTerm or len(searchTerm) < 3:
		error="Your search term has to be at least 3 characters long."
		results = []
	elif not isDropbear(request.user):
		error="You are not part of the corporation"
		results = []
	else:
		try:
			results = list(Character.objects.filter(charName__icontains=searchTerm))
		except:
			results = []

		if len(results) == 0:
			error="No characters named '"+searchTerm+"' found."
		if len(results) == 1:
			return redirect("core:playerProfile", profileName=slugify(unicode(results[0])))

	return render(request, "searchResults.html", {"results": results, 'searchTerm': searchTerm, 'error': error})


def profile(request, profile, mark=None):	
	director = isDirector(request.user)
	if request.POST.get("updategroups") and director:
		for grp in Group.objects.all():
			print request.POST.get(slugify(grp.name))
			if request.POST.get(slugify(grp.name)) == "on":
				profile.user.groups.add(grp)
			else:
				profile.user.groups.remove(grp)

	titles = ", ".join(profile.mainChar.charactertitle_set.all().values_list('titleName', flat=True))
	grouplist = []
	for grp in Group.objects.all():
		if profile.user in grp.user_set.all():
			grouplist.append({"name": grp.name, "checked": True})
		elif director:
			grouplist.append({"name": grp.name, "checked": False})
	ctx = {"profile": profile, "titles": titles, "mark": mark, "isRecruiter": isRecruiter(request.user), "isDirector": director, "grouplist": grouplist}
	return render(request, "profile.html", ctx)


def memberList(request):
	if not isRecruiter(request.user):
		return HttpResponseForbidden("<h1>You do not have the permission to view this page.</h1>")	
	ctx = {}
	corpchars = CorpMember.objects.all()
	chars = Character.objects.all()
	ctx["validCharacters"] = []
	ctx["invalidCharacters"] = []
	for char in corpchars:
		c = chars.filter(charID=char.characterID).first()
		inactiveDays = (datetime.now().replace(tzinfo=None) - char.logoffDate.replace(tzinfo=None)).days
		if not (c and c.api.valid):
			ctx["invalidCharacters"].append({"valid": False, "charName": char.characterName, "joinDate":  char.joinDate, "charID": char.characterID, "logoffDate": char.logoffDate, "location": char.location, "mainChar": "", "inactiveTime": inactiveDays})
		else:
			ctx["validCharacters"].append({"valid": True, "charName": char.characterName, "joinDate":  char.joinDate, "charID": char.characterID, "logoffDate": char.logoffDate, "location": char.location, "slug": slugify(char.characterName), "mainChar": c.profile.mainChar, "inactiveTime": inactiveDays})
		


	return render(request, "memberlist.html", ctx)