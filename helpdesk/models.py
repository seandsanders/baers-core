from django.db import models
from core.models import UserProfile

# Create your models here.
class Ticket(models.Model):
    author = models.ForeignKey(UserProfile, null=True)

    title = models.CharField(max_length=200)
    text = models.CharField(max_length=10000)
    token = models.CharField(max_length=8)

    NEW = 0
    INPROGRESS = 1
    RESOLVED = 2
    STATUS_CHOICES = (
        (NEW, 'New'),
        (INPROGRESS, 'In Progress'),
        (RESOLVED, 'Resolved')
    )
    status = models.IntegerField(choices = STATUS_CHOICES, default=NEW)

    REQUEST = 0
    FEEDBACK = 1
    CATEGORY_CHOICES = (
        (REQUEST, 'Request'),
        (FEEDBACK, 'Feedback')
    )
    category = models.IntegerField(choices = CATEGORY_CHOICES, default=REQUEST)


class Comment(models.Model):
    ticket = models.ForeignKey(Ticket)
    author = models.ForeignKey(UserProfile, related_name="ticketcomment")
    date = models.DateTimeField()
    text = models.CharField(max_length=5000)
    auto_generated = models.BooleanField(default=False)
    private = models.BooleanField()