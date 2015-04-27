import praw
from django.conf import settings
from subreddit.models import RedditAccount

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
	

def deleteRedditAccount(userprofile):
	r = praw.Reddit(user_agent="BAERS User Approver by /u/Nimos")
	r.login(username=settings.REDDIT_USERNAME, password=settings.REDDIT_PASSWORD)
	sub = r.get_subreddit(settings.REDDIT_SUBREDDIT)
	sub.remove_contributor(userprofile.redditaccount.name)

def validateRedditUsers():
	return