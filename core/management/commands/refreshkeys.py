from django.core.management.base import BaseCommand

from datetime import datetime
from core.apireader import refreshKeyInfo
from core.models import ApiKey

class Command(BaseCommand):
    args = ''
    help = 'Adds all groups to the first UserProfile in the database.'

    def handle(self, *args, **options):
    	start = datetime.now()
    	keys = ApiKey.objects.all()
    	for key in keys:
    		refreshKeyInfo(key)

    	time = datetime.now() - start
    	print "Key refresh completed in", time.seconds, "seconds"