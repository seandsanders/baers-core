from django.shortcuts import render
from django.http import HttpResponse, HttpResponseForbidden
from hipchat import api
from hipchat.models import HipchatAccount
from core.views import isHR

# Create your views here.
def isDropbear(user):
	return user.groups.filter(name='Member').exists()

def hipchat(request):
	if not isDropbear(request.user):
		return render(request, 'error.html', {'title': '403 - Forbidden', 'description': 'You are not a member.'})

	profile = request.user.userprofile

	try:
		acc = request.user.userprofile.hipchataccount
		hasAccount = True
	except:
		hasAccount = False

	status = False
	if not hasAccount:
		if request.method == "POST":
			if (request.POST.get("pwd", False) and request.POST.get("email", False)):
				try:
					success, result = api.hipchatAdd(profile.mainChar.charName, request.POST.get("email"), request.POST.get("pwd"))
					if success:
						acc = HipchatAccount(profile=profile, hipchatID=result)
						acc.save()
						status = "Successfully created account"
						hasAccount = True
					else:
						status = result["message"]
				except:
					status = "There was an error creating your account."

	return render(request, "hipchat.html", {"status": status, "hasAccount": hasAccount})

def hipchatlist(request):
	if not isHR(request.user):
		return render(request, 'error.html', {'title': '403 - Forbidden', 'description': 'You are not a HR officer.'})

	accs = HipchatAccount.objects.all()

	return render(request, "hipchatlist.html", {"accs": accs})