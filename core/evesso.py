from django.conf import settings
from django.shortcuts import redirect, render
from urllib2 import urlopen, Request as urlrequest
from urllib import urlencode
import json
import re
import urllib2
from base64 import b64encode as base64
from core.models import Character
from django.contrib.auth import login

def ssologin(request):
    code = request.GET.get('code', None)

    clientid = settings.SSO_CLIENT_ID
    clientkey = settings.SSO_SECRET_KEY
    authorization = base64(clientid+":"+clientkey)
    redirect_url = settings.SSO_CALLBACK_URL


    if not code:
        base = "https://login.eveonline.com/oauth/authorize/?response_type=code"
        url = base + "&redirect_uri=" + redirect_url + "&client_id=" + clientid + "&scope="

        return redirect(url)
    else:
        data = {"grant_type": "authorization_code", "code": code}
        headers = {"Authorization": authorization}

        data = urlencode(data)
        rq = urlrequest("https://login.eveonline.com/oauth/token", data, headers)

        try:
            result = urlopen(rq)
            result = json.loads(result.read())
        except urllib2.HTTPError, e:
            r = e.read()
            return render(request, 'landing.html', {"error": "Your Login Token is invalid or expired. Please try again."})

        headers = {"Authorization": "Bearer " + result["access_token"], "Host": "login.eveonline.com"}

        rq = urlrequest("https://login.eveonline.com/oauth/verify", headers=headers)
        result = urlopen(rq)
        result = result.read()

        result = json.loads(result)

        if not result["CharacterID"]:
            return render(request, 'landing.html', {"error": "Cannot get a valid answer from CCP. Please try again."})

        try:
            char = Character.objects.get(charID=result["CharacterID"])
            char.profile.user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, char.profile.user)
            token = request.session.get('appToken', False)
            if token:
                return redirect("applications:apply", token=token)
            return redirect("core:dashboard")
        except:
            return render(request, 'landing.html', {"error": "The selected Character is not in our Database. Please register using the link below."})
        
