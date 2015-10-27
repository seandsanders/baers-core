from django.db import models
from core.models import UserProfile




# Create your models here.
class Application(models.Model):
	OFFERED = 0
	UNPROCESSED = 1
	ACCEPTED = 2
	HOLD = 3
	DENIED = 4
	STATUS_CHOICES = (
    	(OFFERED, 'Offered'),
    	(UNPROCESSED, 'Unprocessed'),
    	(ACCEPTED, 'Accepted'),
    	(HOLD, 'On Hold'),
   		(DENIED, 'Denied')
	)

	NEW = 0
	CLEAN = 1
	SUSPICIOUS = 2
	INTERVIEW = 3
	RUSH = 4
	SKILLS = 5
	NOTES = 6
	SPY = 7
	COMPLETED = 8
	TAG_CHOICES = (
		(NEW, 'New Application'),
		(CLEAN, 'Review Requested: Looks Clean'),
		(SUSPICIOUS, 'Review Requested: Looks Suspicious'),
		(INTERVIEW, 'Action Requested: Interview'),
		(RUSH, 'Action Requested: Rush'),
		(SKILLS, 'Waiting: Skills'),
		(NOTES, 'In Progress: See notes'),
		(SPY, 'Completed: Spai, Awox Plz'),
		(COMPLETED, 'Completed: See Status')
	) 

	USTZ = 0
	AUTZ = 1
	EUTZ = 2
	TZ_CHOICES = (
		(USTZ, 'US (00:00-08:00 GMT)'),
		(AUTZ, 'AU (08:00-16:00 GMT)'),
		(EUTZ, 'EU (16:00-24:00 GMT)')
	)

	status = models.IntegerField(choices = STATUS_CHOICES, default=OFFERED)
	tag = models.IntegerField(choices = TAG_CHOICES, default=NEW)
	applicationDate = models.DateTimeField(null=True)
	timezone = models.IntegerField(null=True, choices = TZ_CHOICES)
	applicantName = models.CharField(max_length=100, null=True)
	applicantProfile = models.OneToOneField(UserProfile, null=True)
	token = models.CharField(max_length=20, null=True)

class Answer(models.Model):
	app = models.ForeignKey(Application)
	question = models.CharField(max_length=500)
	text = models.CharField(max_length=1000)
	def __str__(self):
		if self.text:
			return self.text
		return "None" 

class Comment(models.Model):
	app = models.ForeignKey(Application)
	author = models.ForeignKey(UserProfile)
	date = models.DateTimeField()
	text = models.CharField(max_length=1000)
	auto_generated = models.BooleanField(default=False)


class DoctrineShipGroup(models.Model):
	name = models.CharField(max_length=50)


class DoctrineShip(models.Model):
	group = models.ForeignKey(DoctrineShipGroup, related_name='doctrineships')
	shipID = models.IntegerField()
	name = models.CharField(max_length=50)


class ShipRequiredSkill(models.Model):
	ship = models.ForeignKey(DoctrineShip, related_name='skills')
	skillID = models.BigIntegerField()
	level = models.BigIntegerField()