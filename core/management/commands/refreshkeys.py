from django.core.management.base import BaseCommand

from datetime import datetime
from core.apireader import refreshKeyInfo
from core.models import ApiKey

class Command(BaseCommand):
    args = ''
    help = 'Refreshes the key with the most outdated information.'

    def handle(self, *args, **options):
        start = datetime.now()
        key = ApiKey.objects.all().order_by('lastRefresh').first()
        
        if key.lastRefresh != None:
            age = start.replace(tzinfo=None) - key.lastRefresh.replace(tzinfo=None) 
            if age.seconds < 3600:
                print "Nothing To do."
                return

        refreshKeyInfo(key)

        time = datetime.now() - start
        print "Key refresh completed in", time.seconds, "seconds"