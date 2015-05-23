import praw
from django.conf import settings
from subreddit.models import RedditAccount
from core.views import isDropbear

def updateRedditAccount(userprofile, redditaccount):

	r = praw.Reddit(user_agent="BAERS User Approver by /u/Nimos")
	r.login(username=settings.REDDIT_USERNAME, password=settings.REDDIT_PASSWORD)
	sub = r.get_subreddit(settings.REDDIT_SUBREDDIT)

	print "Trying to add", redditaccount, "to subreddit"
	try:
		r.set_flair(sub, redditaccount, flair_text=userprofile.mainChar.charName)
	except:
		return 0
	print "Added!"
	
	try:
		userprofile.redditaccount.delete()
		r = userprofile.redditaccount
		deleteRedditAccount(userprofile)
	except:
		pass
		
	sub.add_contributor(redditaccount)
	acc = RedditAccount(owner=userprofile, name=redditaccount)
	acc.save()

	return 1
	

def deleteRedditAccount(account):
	r = praw.Reddit(user_agent="BAERS User Approver by /u/Nimos")
	r.login(username=settings.REDDIT_USERNAME, password=settings.REDDIT_PASSWORD)
	sub = r.get_subreddit(settings.REDDIT_SUBREDDIT)
	sub.remove_contributor(account.name)
	account.delete()

def validateRedditAccounts():
	for acc in RedditAccount.objects.all():
		if not isDropbear(acc.owner.user):
			print "Deleting account", acc.name, "of user", acc.owner
			deleteRedditAccount(acc)
