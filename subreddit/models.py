from django.db import models
from core.models import UserProfile

# Create your models here.
class RedditAccount(models.Model):
	owner = models.OneToOneField(UserProfile, null=True)
	name = models.CharField(max_length=100)