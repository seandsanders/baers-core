from django.db import models
from core.models import UserProfile

# Create your models here.
class Timer(models.Model):
	creator = models.ForeignKey(UserProfile)
	target = models.CharField(max_length=100)
	time = models.DateTimeField()
	note = models.CharField(max_length=1000, null=True)