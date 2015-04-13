from django.db import models
from core.models import UserProfile

# Create your models here.


class SRPRequest(models.Model):
	owner = models.ForeignKey(UserProfile)
	approver = models.ForeignKey(UserProfile, related_name="approvedsrps", null=True)
	killID = models.IntegerField()
	fc = models.CharField(max_length=100)
	aar = models.CharField(max_length=1000)
	learned = models.CharField(max_length=1000)
	suggestions = models.CharField(max_length=1000)

	value = models.IntegerField(null=True)
	ship = models.CharField(max_length=100, null=True)
	shipID = models.IntegerField(null=True)
	pilot = models.CharField(null=True, max_length=100)
	corp = models.CharField(null=True, max_length=100)

	PENDING = 0
	APPROVED = 1
	DENIED = 2
	STATUS_CHOICES = (
		(PENDING, 'Pending'),
		(APPROVED, 'Approved'),
		(DENIED, 'Denied')
	)

	status = models.IntegerField(choices = STATUS_CHOICES, default=PENDING)

	def __str__(self):
		return unicode(owner)+" "+unicode(killID)

