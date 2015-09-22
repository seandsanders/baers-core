* Intro  
About the code structure here. I tried to make a new django app for every large "feature" to keep it organized. I sticked to that for some things, but some things I just put into the "core" package.  


* Installation

If you're clueless how to install a django app, just google for "how to deploy a django app"  

Then follow the rest of these instructions:


* Dependencies (all available via pip)  
django  
eveapi  
praw  

You need to dump the eve static data export into the same Database Django is using.

* Other instructions  
main settings file is baerscore/settings.py

Add 3 cronjobs:

1. /path/to/stuff/manage.py refreshkeys
This will take the oldest API key and refresh it for the cache. I have this running every 5 minutes. Even with a very small set, it wont refresh any key more than once an hour.

2. /path/to/stuff/manage.py refreshCorpApi
Refreshes the corp api. I have this running hourly

3. /path/to/stuff/manage.py checkServices
This will purge users from the services that have lost their member status for whatever reason. I'm running this hourly as well

Skill plans need to be in the XML format exported by EVEMon (note: that's not the .EMP format, you can change it while exporting), and go into applications/skillplans/.
They are sorted by file name in the list.


* Useful Commands:

manage.py addgroups
Run this after registering your account to recieve all permission groups


* Group explanation

Director:
 - Can add/delete Users from groups
 - Can view Capital Census

HR:
 - Can view user-API related information, like skills, assets, location, member list and the actual API keys

Recruiter:
 - Can view/comment/edit applications
 - Can see API keys and information for users that are not accepted yet
 - Can NOT see current member's API stuff

Finance:
 - Can view the accounting page
 - Can use the SRP Administration page

POS:
 - Can use the POS tracker

IT:
 - Gets annoying notifications on the main page when an API call fails (you can expect this to happen occasionally, but if it fails a lot there might be a problem)

Member:
 - Can do everything else


* Other stuff

Sometimes the CCP Api is weird and reports a key as "forbidden" even though it isn't. Don't freak out if you see a notification saying that someone invalidated their API key.
Also, connection problems to the API server may cause the system to think the API is invalid, that's just something I haven't fixed yet.