from django.shortcuts import render
from django.http import HttpResponse, HttpResponseForbidden
from subreddit.reddit import updateRedditAccount

# Create your views here.
def isDropbear(user):
	return user.groups.filter(name='Dropbears').exists()

def reddit(request):
	if not isDropbear(request.user):
		return HttpResponseForbidden("<h1>Only for current members</h1>")

	status = -1
	if request.method == "POST":
		status = updateRedditAccount(request.user.userprofile, request.POST.get('accountname'))

	name = ""
	try:
		name = request.user.userprofile.redditaccount.name
	except:
		pass

	return render(request, "main.html", {"name": name, "status": status})