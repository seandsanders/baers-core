from django.core.management.base import BaseCommand

from datetime import datetime
from core.apireader import refreshCorpApi
from core.models import ApiKey

class Command(BaseCommand):
    args = ''
    help = 'Refreshes the stored corp Api.'

    def handle(self, *args, **options):
    	start = datetime.now()
    	refreshCorpApi()

    	time = datetime.now() - start
    	print "Key refresh completed in", time.seconds, "seconds"