import urllib2
import json
from urllib import quote as urlescape
from django.conf import settings

def hipchatAdd(name, email, password):
   print "Attempting to add Account of "+name
   token = "auth_token="+settings.HIPCHAT_TOKEN
   server = "http://api.hipchat.com/v2/user"+"?"+token


   data = {"name": name, "email": email, "password": password}

   headers = {"content-type": "application/json"}

   request = urllib2.Request(server, json.dumps(data), headers)

   try:
      result = urllib2.urlopen(request)
      r = result.read()
   except urllib2.HTTPError as e:
      r = e.read()
      pass

   print r

   result = json.loads(r)

   if result.get("error", False):
      return False, result["error"]

   return True, result["id"]


def hipchatDelete(uID):
   token = "auth_token="+settings.HIPCHAT_TOKEN
   server = "http://api.hipchat.com/v2/user/"+uID+"?"+token

   request = urllib2.Request(server)
   request.get_method = lambda: 'DELETE'

   try:
      result = urllib2.urlopen(request)
      r = result.read()
   except urllib2.HTTPError as e:
      r = e.read()
      pass

   print r

   return r.strip() == ""
