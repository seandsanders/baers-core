from django.shortcuts import render

# Create your views here.
def dashboard(request):
	context = {
		"mainCharName": unicode(request.user.userprofile),
		"mainCharID": unicode(request.user.userprofile.mainChar.charID),
	}

	return render(request, 'dashboard.html', context)


def landing(request):
	context = {}
	return render(request, 'landing.html', context)