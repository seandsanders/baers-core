from django.core.management.base import BaseCommand

from hipchat.api import validateHipchatAccounts
from subreddit.reddit import validateRedditAccounts

class Command(BaseCommand):
    args = ''
    help = 'Deletes all third party accounts without a valid in-corp character'

    def handle(self, *args, **options):
    	validateRedditAccounts()
    	validateHipchatAccounts()