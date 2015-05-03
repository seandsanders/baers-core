from django.shortcuts import render
from django.http import HttpResponse, HttpResponseForbidden
from subreddit.reddit import updateRedditAccount
from subreddit.models import RedditAccount
from core.views import isRecruiter

# Create your views here.
def isDropbear(user):
	return user.groups.filter(name='Dropbears').exists()

def reddit(request):
	if not isDropbear(request.user):
		return render(request, 'error.html', {'title': '403 - Forbidden', 'description': 'You are not a member.'})

	status = -1
	if request.method == "POST":
		status = updateRedditAccount(request.user.userprofile, request.POST.get('accountname'))

	name = ""
	try:
		name = request.user.userprofile.redditaccount.name
	except:
		pass

	return render(request, "main.html", {"name": name, "status": status})

def redditlist(request):
	if not isHR(request.user):
		return render(request, 'error.html', {'title': '403 - Forbidden', 'description': 'You are not a HR officer.'})

	accs = RedditAccount.objects.all()

	return render(request, "list.html", {"reddits": accs})