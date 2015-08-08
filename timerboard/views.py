from django.shortcuts import render
from django.http import HttpResponse
from timerboard.models import Timer
from datetime import datetime, timedelta
from core.views import isDropbear
from core import postNotification
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import Group
from django.core.urlresolvers import reverse
from django.utils.text import slugify

# Create your views here.
def timerboard(request):
	if not isDropbear(request.user):
		return render(request, 'error.html', {'title': '403 - Forbidden', 'description': 'You are not a member.'})

	status = None
	if request.method == "POST":
		delete = request.POST.get('delete', False)
		delid = request.POST.get('id', False)

		if delete and delid:
			Timer.objects.filter(id=delid).delete()
		else:

			target = request.POST.get('target', False)
			date = request.POST.get('date', False)
			hours = request.POST.get('hours', False)
			minutes = request.POST.get('minutes', False)

			if target and date and hours and minutes:
				try:
					d = datetime.strptime(date + hours + ":" + minutes, "%m/%d/%Y%H:%M")
					t = Timer()
					t.target = target
					t.time = d
					t.note = "-"
					t.creator = request.user.userprofile
					t.save()
					status = "Timer Added."
					notificationText = "<a href='"+reverse('core:playerProfile', kwargs={"profileName": slugify(request.user.userprofile)})+"'>"+unicode(request.user.userprofile)+"</a> added a new timer for \""+target+"\" to the <a href='"+reverse('timerboard:timerboard')+"'>Timerboard.</a>"
					postNotification(Group.objects.get(name="Dropbears"), notificationText)
				except:
					status = "Invalid Date and/or Time"
			else:
				status = "You didn't fill all the fields."

	timers = Timer.objects.all()

	active = timers.filter(time__gte=datetime.utcnow()-timedelta(hours=1)).order_by("time")
	done = timers.filter(time__lte=datetime.utcnow()-timedelta(hours=1)).order_by("time")

	return render(request, "timers.html", {'active': active, 'done': done, 'status': status})

@csrf_exempt
def updateNote(request):
	if not isDropbear(request.user):
		return render(request, 'error.html', {'title': '403 - Forbidden', 'description': 'You are not a member.'})

	id = request.POST.get('id', False)
	text = request.POST.get('note', False)
	if id and text:		
		try:
			t = Timer.objects.get(id = id)
			t.note = text
			t.save()
		except:
			pass

	return HttpResponse('')