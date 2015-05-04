from django.db import models
from core.models import UserProfile

# Create your models here.
class HipchatAccount(models.Model):
	profile = models.OneToOneField(UserProfile)
	hipchatID = models.CharField(max_length=100)
	