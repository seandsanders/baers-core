from django.shortcuts import render
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseForbidden
from srp.models import SRPRequest, SRPComment
from core.models import Notification, Character
import urllib2, json, gzip
from StringIO import StringIO
import eveapi
from datetime import datetime
from django.db.models import Sum
from django.core.urlresolvers import reverse
from django.contrib.auth.models import Group
from django.utils.text import slugify

# Create your views here.

def isFinance(user):
	return user.groups.filter(name='Finance').exists()
def isDropbears(user):
	return user.groups.filter(name='Dropbears').exists()

def srpadmin(request):
	if not isFinance(request.user):
		return render(request, 'error.html', {'title': '403 - Forbidden', 'description': 'You are not a finance officer.'})
	srps = SRPRequest.objects.all()
	
	pending = srps.filter(status=0)
	approved = srps.filter(status=1)
	denied = srps.filter(status=2)

	pendingsum = pending.aggregate(Sum('value'))
	approvedsum = approved.aggregate(Sum('value'))
	deniedsum = denied.aggregate(Sum('value'))


	c = {
		"pending": pending,
		"approved": approved,
		"denied": denied,
		"deniedsum": deniedsum,
		"pendingsum": pendingsum,
		"approvedsum": approvedsum
	}

	return render(request, 'srplist.html', c)

def srplist(request):
	if not isDropbears(request.user):
		return render(request, 'error.html', {'title': '403 - Forbidden', 'description': 'You are not a member.'})
	srps = SRPRequest.objects.filter(owner=request.user.userprofile)
	
	pending = srps.filter(status=0)
	approved = srps.filter(status=1)
	denied = srps.filter(status=2)

	pendingsum = pending.aggregate(Sum('value'))
	approvedsum = approved.aggregate(Sum('value'))
	deniedsum = denied.aggregate(Sum('value'))


	c = {
		"pending": pending,
		"approved": approved,
		"denied": denied,
		"deniedsum": deniedsum,
		"pendingsum": pendingsum,
		"approvedsum": approvedsum
	}
	return render(request, 'srplist.html', c)

def viewsrp(request, killID):
	kill = SRPRequest.objects.get(killID=killID)
	f = isFinance(request.user)
	if not (f or request.user.userprofile == kill.owner):
		return render(request, 'error.html', {'title': '403 - Forbidden', 'description': 'You are not a member.'})

	if request.method == "POST":
		if request.POST.get('newComment', False):
			c = SRPComment()
			c.text = request.POST.get('commentbody')
			c.author = request.user.userprofile
			c.date = datetime.utcnow()
			c.request = kill
			c.save()
			finance = Group.objects.filter(name="Finance").first()
			note = Notification(cssClass="info")
			note.content="<a href='"+reverse('core:playerProfile', kwargs={"profileName": slugify(request.user.userprofile)})+"'>"+unicode(c.author)+"</a> commented on <a href='"+reverse('srp:viewsrp', kwargs={"killID": kill.killID})+"'>"+unicode(kill.owner)+"'s SRP Request for a "+kill.ship+"</a>"
			note.save()
			note.targetGroup.add(finance)
			note.targetUsers.add(kill.owner.user)
		elif request.POST.get('approve', False) and kill.status != 1 and f:
			kill.status = 1
			kill.approver = request.user.userprofile
			n = Notification(cssClass='success', content='Your <a href="'+reverse("srp:srplist")+'">SRP request</a> for a '+kill.ship+' has been accepted.')
			n.save()
			n.targetUsers.add(kill.owner.user)
		elif request.POST.get('deny', False) and kill.status != 2 and f:
			kill.status = 2
			kill.approver = request.user.userprofile
			n = Notification(cssClass='danger', content='Your <a href="'+reverse("srp:srplist")+'">SRP request</a> for a '+kill.ship+' has been denied.')
			n.save()
			n.targetUsers.add(kill.owner.user)
		elif request.POST.get('pending', False) and kill.status != 0 and f:
			kill.status = 0
			kill.approver = None
			n = Notification(cssClass='warning', content='Your <a href="'+reverse("srp:srplist")+'">SRP request</a> for a '+kill.ship+' has been reset.')
			n.save()
			n.targetUsers.add(kill.owner.user)
		kill.save()

	if not Character.objects.filter(charName=kill.pilot).exists():
		apiwarning = True
	else:
		apiwarning = False

	if not kill:
		return render(request, 'error.html', {'title': '404 - Not Found', 'description': 'There is no kill with that ID in the database.'})
	c = {"kill": kill, "apiwarning": apiwarning, "admin": f}
	return render(request, "srpdetails.html", c)

def submit(request):
	if not isDropbears(request.user):
		return render(request, 'error.html', {'title': '403 - Forbidden', 'description': 'You are not a member.'})
	c = {}
	if request.method == "POST":
		error = False
		new = SRPRequest()
		new.owner = request.user.userprofile

		link = request.POST.get('link', False)
		if link:
			new.killID = link.split("/")[-2]
			if SRPRequest.objects.filter(killID=new.killID).exists():
				error = True
				return render(request, "submit.html", c)
			shipID, shipName, pilot, corp, value = getKillInformation(new.killID)
		if not link or not shipID:
			error = True
		else:
			new.value = int(float(value))
			new.shipID = shipID
			new.fc = request.POST.get('fc', '')
			new.aar = request.POST.get('aar', '')
			new.learned = request.POST.get('learned', '')
			new.suggestions = request.POST.get('suggestions', '')
			new.pilot = pilot
			new.corp = corp
			new.ship = shipName
			new.save()
			c["message"] = "Successfully added kill #"+new.killID
			finance = Group.objects.filter(name="Finance").first()
			note = Notification(cssClass="info")
			note.content="New <a href='"+reverse('srp:viewsrp', kwargs={"killID": new.killID})+"'>SRP request for a "+shipName+"</a> added by <a href='"+reverse('core:playerProfile', kwargs={"profileName": slugify(request.user.userprofile)})+"'>"+unicode(request.user.userprofile)+"</a>."
			note.save()
			note.targetGroup.add(finance)

		c["error"] = error

	return render(request, "submit.html", c)

def getKillInformation(killID):
	api = eveapi.EVEAPIConnection()

	try:
		request = urllib2.Request("https://zkillboard.com/api/killID/"+unicode(killID)+"/")
		request.add_header('Accept-encoding', 'gzip')
		response = urllib2.urlopen(request)
		if response.info().get('Content-Encoding') == 'gzip':
			buf = StringIO( response.read())
			f = gzip.GzipFile(fileobj=buf)
			data = f.read()
		else:
			data = response.read()
		result = json.loads(data)

			
	except urllib2.HTTPError, e:
		print e.read()
		return False, False, False, False, False
	except Exception, e:
		print "ERROR E"
		return False, False, False, False, False
	try:
		shipID = result[0]["victim"]["shipTypeID"]
		ship = api.eve.TypeName(ids=shipID).types[0].typeName
		return shipID, ship, result[0]["victim"]["characterName"], result[0]["victim"]["corporationName"], result[0]["zkb"]["totalValue"]
	except Exception, e:
		print e
		return False, False, False, False, False