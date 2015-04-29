from django.shortcuts import render
from django.http import HttpResponse
from timerboard.models import Timer
from datetime import datetime
from core.views import isDropbear
from django.views.decorators.csrf import csrf_exempt

# Create your views here.
def timerboard(request):
	if not isDropbear(request.user):
		return HttpResponseForbidden("<h1>You do not have the permission to view this page.</h1>")

	status = None
	if request.method == "POST":
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
			except:
				status = "Invalid Date and/or Time"
		else:
			status = "You didn't fill all the fields."

	timers = Timer.objects.all()

	active = timers.filter(time__gte=datetime.utcnow())
	done = timers.filter(time__lte=datetime.utcnow())

	return render(request, "timers.html", {'active': active, 'done': done})

@csrf_exempt
def updateNote(request):
	if not isDropbear(request.user):
		return HttpResponseForbidden("<h1>You do not have the permission to view this page.</h1>")

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