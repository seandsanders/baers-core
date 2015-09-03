from django.db import connection
from django.db.models import Q

from django.conf import settings

from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import user_passes_test

from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseForbidden
from django.utils.text import slugify
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

from datetime import datetime, timedelta
from json import dumps as jsonify
import random

from core import postNotification
from core.models import Notification, UserProfile, Character, ApiKey, CorpMember, CorpStarbase, CorpStarbaseFuel, StarbaseNote, StarbaseOwner, CharacterSkill, Haiku, AccountingEntry, CharacterAsset, CorpAsset, CCPinvType
from core.apireader import validateKey, refreshKeyInfo, retrieveItemNames
from core.tasks import Task 
from core.evedata import STARBASE_TYPES

from applications.models import Application, Answer

from srp.models import SRPRequest

import time

# Create your views here.

def isRecruiter(user):
	return user.groups.filter(name='Recruiter').exists()

def isHR(user):
	return user.groups.filter(name='HR').exists()

def isDirector(user):
	return user.groups.filter(name='Director').exists()

def isDropbear(user):
	return user.groups.filter(name='Dropbears').exists()

def isFinance(user):
	return user.groups.filter(name='Finance').exists()

def isPOS(user):
	return user.groups.filter(name="POS").exists()

def updateTZ(request):
	up = request.user.userprofile
	up.tzoffset = request.POST.get('tzoffset', None)
	up.save()
	return HttpResponse("")

def dashboard(request):
	titles = ", ".join(request.user.userprofile.mainChar.charactertitle_set.all().values_list('titleName', flat=True))
	context = {
		"mainCharName": unicode(request.user.userprofile),
		"mainCharID": unicode(request.user.userprofile.mainChar.charID),
		"charTitle": unicode(titles)
	}

	tasklist = []

	try:
		app = request.user.userprofile.application
		hasapp = app.status == Application.UNPROCESSED or app.status == Application.HOLD or app.status == Application.DENIED
		appstatus = app.get_status_display()
		if app.status == Application.UNPROCESSED:
			if app.tag in [Application.CLEAN, Application.SUSPICIOUS, Application.NOTES]:
				appstatus = "In Progress"
			elif app.tag in [Application.INTERVIEW]:
				appstatus = "Ready for Interview"

	except:
		hasapp = False

	if hasapp:
		tasklist.append(Task("Your <a href='"+reverse("applications:mystatus")+"'>application status</a>: "+appstatus+"", cssClass="success"))

	if isDropbear(request.user):
		c = CorpStarbase.objects.filter(state=3)
		if len(c) > 0:
			tasklist.append(Task("<b>IMPORTANT: We have <a href='"+reverse("core:poslist")+"'>"+unicode(len(c))+" reinforced POSes!</a></b>", cssClass="danger"))

	if isDropbear(request.user):
		try:
			a = request.user.userprofile.redditaccount
		except:
			tasklist.append(Task("You do not have a <a href='"+reverse("subreddit:reddit")+"'>Reddit account</a> connected.", cssClass="danger"))

	if isRecruiter(request.user):
		c = len(Application.objects.filter(status=Application.UNPROCESSED))
		if c != 0:
			tasklist.append(Task("There are <a href='"+reverse("applications:applications")+"'>"+unicode(c)+" unprocessed applications.</a>", cssClass="warning"))

	if isFinance(request.user):
		c = len(SRPRequest.objects.filter(status=SRPRequest.PENDING))
		if c != 0:
			tasklist.append(Task("There are <a href='"+reverse("srp:srpadmin")+"'>"+unicode(c)+" pending SRP requests.</a>", cssClass="warning"))

	if isDropbear(request.user):
		haikus = Answer.objects.filter(question__contains="haiku")
		oldhaikus = Haiku.objects.all()
		index = random.randint(0, haikus.count()-1+oldhaikus.count())
		if index < haikus.count():
			h = {"authorProfile": haikus[index].app.applicantProfile, "author": unicode(haikus[index].app.applicantProfile), "text": haikus[index].text.strip()}
		else:
			index -= haikus.count()

			h = {"author": oldhaikus[index].author, "text": oldhaikus[index].text.strip()}
			
			c = Character.objects.filter(charName__icontains=h["author"]).first()
			if c:
				h["authorProfile"] = c.profile

		context["haiku"] = h

		
	c = CorpStarbase.objects.filter(itemID__in=request.user.userprofile.starbaseowner_set.values_list('starbaseID')).filter(state__gte=3)
	if c.exists():
		from evedata import STARBASE_TYPES
		for pos in c:
			try:
				fuels = pos.corpstarbasefuel_set.exclude(typeID=16275)
				if len(fuels) > 1:
					print "WARNING: FOUND MULTIPLE FUEL BLOCK TYPES!"

				if len(fuels) == 0:
					pos.fuel = 0
				else:
					pos.fuel = fuels.first().quantity
			except CorpStarbaseFuel.DoesNotExist:
				pos.fuel = 0

			pos.info = STARBASE_TYPES[pos.typeID]

			pos.fuelpercent = int(100*float(pos.fuel)/float(pos.info["maxFuel"]))

			if pos.fuelpercent < 20:

				cur = connection.cursor()

				cur.execute('SELECT itemName FROM mapDenormalize WHERE itemID = "' + unicode(pos.moonID)+ '";')

				tup = cur.fetchone()

				if tup:
					pos.location = tup[0]
				else:
					pos.location = "[API Error]"

				tasklist.append(Task("Your POS at  <a href='"+reverse("core:poslist")+"'>"+pos.location+"</a> has only "+unicode(pos.fuelpercent)+"% fuel remaining.", cssClass="warning"))


	if len(tasklist) == 0:
		tasklist.append(Task("No active tasks."))

	context["tasks"] = tasklist
	context["notifications"] = Notification.objects.filter(Q(targetUsers=request.user) | Q(targetGroup__in=request.user.groups.all())).order_by('-time')[:20]

	return render(request, 'dashboard.html', context)


def changeTheme(request):
	request.user.userprofile.theme = request.POST.get('theme', 'Flatly')
	request.user.userprofile.save()
	return HttpResponse('')

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
				if int(request.POST.get("keyID")) > 4325693:
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
				else:
					error = "Please do not re-use old API keys"
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
					postNotification(target=recruiterGrp, text="<a href='"+reverse('core:playerProfile', kwargs={"profileName": slugify(newProfile)})+"'>"+unicode(newProfile)+"</a> created an account.", cssClass="info")
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
						postNotification(target=hrGrp, text=unicode(request.user.userprofile)+" has deleted an API key.", cssClass="warning")
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
					postNotification(target=recruiterGrp, text="<a href='"+reverse('core:playerProfile', kwargs={"profileName": slugify(newKey.profile)})+"'>"+unicode(newKey.profile)+"</a> has added a new API key.", cssClass="info")
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
		return render(request, 'error.html', {'title': '403 - Forbidden', 'description': 'You are not a member.'})
	def unslugify(name):
		return name.replace("-", " ") 
	try:
		c = Character.objects.get(charName__iexact = unslugify(profileName))
	except:
		return render(request, 'error.html', {'title': '404 - Not Found', 'description': 'This character is not in the Database.'})
	return profile(request, c.profile, mark=c)

@csrf_exempt
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
	ctx = {"profile": profile, "titles": titles, "mark": mark, "isRecruiter": isRecruiter(request.user), "isHR": isHR(request.user), "isDirector": director, "grouplist": grouplist}

	if isHR(request.user) or request.user.userprofile == profile:
		from applications.views import getFlyable
		ctx['showSkills'] = True
		ctx["ships"] = getFlyable(profile)

	return render(request, "profile.html", ctx)


def memberList(request):
	if not isHR(request.user):
		return render(request, 'error.html', {'title': '403 - Forbidden', 'description': 'You are not a HR officer.'})
	ctx = {}
	corpchars = CorpMember.objects.filter(altCorp=False)
	chars = Character.objects.all()
	ctx["validCharacters"] = []
	ctx["invalidCharacters"] = []
	for char in corpchars:
		c = chars.filter(charID=char.characterID).first()
		inactiveDays = (datetime.utcnow().replace(tzinfo=None) - char.logoffDate.replace(tzinfo=None)).days
		if not (c and c.api.valid):
			ctx["invalidCharacters"].append({"valid": False, "charName": char.characterName, "joinDate":  char.joinDate, "charID": char.characterID, "logoffDate": char.logoffDate, "location": char.location, "mainChar": "", "shipType": char.shipType, "inactiveDays": inactiveDays})
		else:
			ctx["validCharacters"].append({"valid": True, "charName": char.characterName, "joinDate":  char.joinDate, "charID": char.characterID, "logoffDate": char.logoffDate, "location": char.location, "slug": slugify(char.characterName), "mainChar": c.profile.mainChar, "shipType": char.shipType, "shipName": c.activeShipName, "inactiveDays": inactiveDays})
	if settings.ALTCORP_API_KEYID and settings.ALTCORP_API_VCODE:
		ctx["validAlts"] = []
		ctx["invalidAlts"] = []
		corpchars = CorpMember.objects.filter(altCorp=True)
		for char in corpchars:
			c = chars.filter(charID=char.characterID).first()
			inactiveDays = (datetime.utcnow().replace(tzinfo=None) - char.logoffDate.replace(tzinfo=None)).days
			if not (c and c.api.valid):
				ctx["invalidAlts"].append({"valid": False, "charName": char.characterName, "joinDate":  char.joinDate, "charID": char.characterID, "logoffDate": char.logoffDate, "location": char.location, "mainChar": "", "shipType": char.shipType, "inactiveDays": inactiveDays})
			else:
				ctx["validAlts"].append({"valid": True, "charName": char.characterName, "joinDate":  char.joinDate, "charID": char.characterID, "logoffDate": char.logoffDate, "location": char.location, "slug": slugify(char.characterName), "mainChar": c.profile.mainChar, "shipType": char.shipType, "shipName": c.activeShipName, "inactiveDays": inactiveDays})

	ctx["validCharacters"].sort(key=lambda x: x["mainChar"])
	ctx["invalidCharacters"].sort(key=lambda x: x["mainChar"])
	ctx["validAlts"].sort(key=lambda x: x["mainChar"])
	ctx["invalidAlts"].sort(key=lambda x: x["mainChar"])

	return render(request, "memberlist.html", ctx)


def starbases(request):
	if not isPOS(request.user):
		return render(request, 'error.html', {'title': '403 - Forbidden', 'description': 'You do not have permissions to use the POS tracker.'})

	poses = CorpStarbase.objects.all()

	ctx = {}
	ctx["rf"] = []
	ctx["online"] = []
	ctx["onlining"] = []
	ctx["offline"] = []

	hourly = 0

	for pos in poses:
		try:
			pos.stront = pos.corpstarbasefuel_set.get(typeID=16275).quantity
		except CorpStarbaseFuel.DoesNotExist:
			pos.stront = 0
		try:
			fuels = pos.corpstarbasefuel_set.exclude(typeID=16275)
			if len(fuels) > 1:
				print "WARNING: FOUND MULTIPLE FUEL BLOCK TYPES!"

			if len(fuels) == 0:
				pos.fuel = 0
			else:
				pos.fuel = fuels.first().quantity
		except CorpStarbaseFuel.DoesNotExist:
			pos.fuel = 0

		pos.info = STARBASE_TYPES[pos.typeID]

		pos.remaining = datetime.utcnow() + timedelta(hours=pos.fuel / int(pos.info["consumption"]))
		pos.fuelpercent = int(100*float(pos.fuel)/float(pos.info["maxFuel"]))



		cur = connection.cursor()

		cur.execute('SELECT itemName FROM mapDenormalize WHERE itemID = "' + unicode(pos.moonID)+ '";')

		tup = cur.fetchone()

		if tup:
			pos.location = tup[0]
		else:
			pos.location = "[API Error]"

		try:
			pos.note = StarbaseNote.objects.get(starbaseID=pos.itemID)
			pos.note = pos.note.note
		except:
			pos.note = "-"
		try:
			pos.owner = StarbaseOwner.objects.get(starbaseID=pos.itemID)
			pos.owner = pos.owner.owner
		except:
			pos.owner = None

		if pos.state == 1:
			ctx["offline"].append(pos)
		elif pos.state == 2:
			ctx["onlining"].append(pos)
		elif pos.state == 3:
			ctx["rf"].append(pos)
			hourly += int(pos.info["consumption"])
		elif pos.state == 4:
			ctx["online"].append(pos)
			hourly += int(pos.info["consumption"])

		ctx["online"] = sorted(ctx["online"], key=lambda pos: pos.remaining)
		ctx["monthly"] = hourly*24*30
		ctx["monthlyisk"] = hourly*24*30*15000
		ctx["users"] = jsonify([u[0] for u in UserProfile.objects.values_list('mainChar__charName')])


	return render(request, "poslist.html", ctx)

@csrf_exempt
def updateNote(request):
	if not isPOS(request.user):
		return render(request, 'error.html', {'title': '403 - Forbidden', 'description': 'You do not have the permission to use the POS tracker.'})

	id = request.POST.get('id', False)
	text = request.POST.get('note', False)
	if id and text:		
		try:
			note = StarbaseNote.objects.get(starbaseID = id)
		except:
			note = StarbaseNote(starbaseID=id)

		note.note = text
		note.save()
	return HttpResponse('')

@csrf_exempt
def updateOwner(request):
	if not isPOS(request.user):
		return render(request, 'error.html', {'title': '403 - Forbidden', 'description': 'You do not have the permission to use the POS tracker.'})

	id = request.POST.get('id', False)
	name = request.POST.get('owner', False)
	if id and name:		
		try:
			owner = StarbaseOwner.objects.get(starbaseID = id)
		except:
			owner = StarbaseOwner(starbaseID=id)
		try:
			profile = Character.objects.get(charName=name).profile
			owner.owner = profile
			owner.save()
		except:
			owner.delete()
			owner.owner = None
			profile = None
		
	else:
		owner.owner = None

	return render(request, 'starbaseowner.html', {"profile": owner.owner})


def groupList(request):
	if not isDirector(request.user):
		return render(request, 'error.html', {'title': '403 - Forbidden', 'description': 'You are not a director.'})

	groups = Group.objects.all()

	return render(request, 'grouplist.html', {"groups": groups})

def capCensus(request):
	if not isDirector(request.user):
		return render(request, 'error.html', {'title': '403 - Forbidden', 'description': 'You are not a director.'})

	from applications.views import ships

	capitals = ships[3]['ships']
	result = []

	for cap in capitals:
		chars = Character.objects
		for skill in cap['skills']:
			chars = chars.filter(characterskill__typeID=skill[0])

		chars = chars.filter(profile__user__groups__name="Dropbears")
		if chars:
			result.append({"name": cap["name"], "id": cap["shipID"], "chars": chars})

	return render(request, "capcensus.html", {"ships": result})

def accounting(request):
	if not isFinance(request.user):
		return render(request, 'error.html', {'title': '403 - Forbidden', 'description': 'You are not a finance officer.'})

	context = {}

	entries = AccountingEntry.objects.all()
	
	context["currentBalance"] = entries.filter(name="walletTotal").last().balance if entries.filter(name="walletTotal").last() else 0
	context["currentSRP"] = entries.filter(name="pendingSRP").last().balance or 0
	context["currentTotalFuel"] = entries.filter(name="fuelTotal").last().balance or 0
	context["currentChaFuel"] = entries.filter(name="fuelCHA").last().balance
	context["currentPosFuel"] = entries.filter(name="fuelPOS").last().balance

	walletHistory = entries.filter(name="walletTotal")[:720]
	srpHistory = entries.filter (name="pendingSRP")[:720]
	fuelHistory = entries.filter(name="fuelTotal")[:720]
	fuelCHAHistory = entries.filter(name="fuelCHA")[:720]
	fuelPosHistory = entries.filter(name="fuelPOS")[:720]

	def historyToPlot(queryset):
		result = []
		for entry in queryset:
			unixtime = int(time.mktime(entry.date.timetuple())*1000)
			result.append([unixtime, entry.balance])
		return jsonify(result)

	
	
	context["fuelPosHistory"] = historyToPlot(fuelPosHistory)
	context["fuelCHAHistory"] = historyToPlot(fuelCHAHistory)
	context["fuelHistory"] = historyToPlot(fuelHistory)
	context["srpHistory"] = historyToPlot(srpHistory)
	context["combinedHistory"] = '{label: "Wallet Total", data: '+historyToPlot(walletHistory)+'},{label: "SRP Total", data: '+ historyToPlot(srpHistory)+'}'
	context["walletHistory"] = historyToPlot(walletHistory)


	return render(request, "accounting.html", context)

def assetScan(request, itemID=None):
	if not isHR(request.user):
		return render(request, 'error.html', {'title': '403 - Forbidden', 'description': 'You are not HR.'})

	typeName = request.POST.get("typename", None)

	rAssets = None
	rcAssets = None
	assets = None
	corpAssets = None
	containerName = None
	containerType = None
	typeID = "Unknown"
	
	if typeName and typeName != "":
		typeID = CCPinvType.objects.filter(typeName=typeName)
		if typeID:
			typeID = typeID.first().typeID

			assets = CharacterAsset.objects.filter(typeID=typeID).order_by("-quantity")
			corpAssets = CorpAsset.objects.filter(typeID=typeID).order_by("-quantity")
		else:
			status = "Cannot find <strong>"+typeName+"</strong> in Database."

	elif itemID and int(itemID):
		assets = CharacterAsset.objects.filter(parentID=itemID).order_by("flag")
		corpAssets = CorpAsset.objects.filter(parentID=itemID).order_by("flag")


	if assets or corpAssets:
			rAssets = []
			cur = connection.cursor()
			for asset in assets:
				if asset.parentID:
					p = CharacterAsset.objects.filter(itemID=asset.parentID)
					if p:
						parentType = CCPinvType.objects.filter(typeID=p.first().typeID)
						if parentType:
							asset.parentName = parentType.first().typeName
				invType = CCPinvType.objects.filter(typeID=asset.typeID).first()
				asset.itemName = invType.typeName if invType else "Type ID "+unicode(asset.typeID)+" unknown"

				cur.execute('SELECT itemName FROM mapDenormalize WHERE itemID = '+str(asset.locationID)+';')
				asset.location = cur.fetchone();

				cur.execute('SELECT flagName FROM invFlags WHERE flagID = '+str(asset.flag)+';')
				asset.flag = cur.fetchone();
				rAssets.append(asset)

			
			parentsList = map(str, corpAssets.values_list("parentID", flat=True))
			if itemID:
				parentsList.append(itemID)
			parentNames = retrieveItemNames(parentsList)

			itemsList = map(str, corpAssets.values_list("itemID", flat=True))
			itemNames = retrieveItemNames(itemsList)

			rcAssets = []
			for asset in corpAssets:
				cur.execute('SELECT itemName FROM mapDenormalize WHERE itemID = '+str(asset.locationID)+';')
				asset.location = cur.fetchone();

				cur.execute('SELECT flagName FROM invFlags WHERE flagID = '+str(asset.flag)+';')
				asset.flag = cur.fetchone();

				if asset.parentID:
					asset.parentName = unicode(parentNames.get(asset.parentID, "-"))
					p = CorpAsset.objects.filter(itemID=asset.parentID)
					if p:
						parentType = CCPinvType.objects.filter(typeID=p.first().typeID)
						if parentType:
							asset.parentName += " ("+unicode(parentType.first().typeName)+")"

				asset.itemName = unicode(itemNames.get(asset.itemID, CCPinvType.objects.filter(typeID=asset.typeID).first().typeName))
				rcAssets.append(asset)


			if itemID and (assets or corpAssets):
				containerName = unicode(parentNames.get(int(itemID), "-"))
				p = CorpAsset.objects.filter(itemID=itemID)
				if not p:
					p = CharacterAsset.objects.filter(itemID=itemID)
				
				containerType = CCPinvType.objects.filter(typeID=p.first().typeID).first()
			else:
				containerName = None
				containerType = None

	else:
		status = "Please supply an item name."


						

	return render(request, "assetscan.html", {"assets": rAssets, "corpAssets": rcAssets, "typeName": typeName, "typeID": typeID, "containerName": containerName, "containerType": containerType})


def timezoneAPI(request):
	if request.GET.get("secret", False) == "184supersecretrandomsecuritykey733":
		users = UserProfile.objects.all()
		result = {}

		for user in users:
			result[user.mainChar.charName] = user.tzoffset
		

		return HttpResponse(jsonify(result))

	else:
		return HttpResponseForbidden("NOPE")

