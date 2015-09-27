from django.core.management.base import BaseCommand

from datetime import datetime
from core.apireader import refreshKeyInfo
from core.models import ApiKey

class Command(BaseCommand):
    args = ''
    help = 'Refreshes the key with the most outdated information.'

    def handle(self, *args, **options):
        start = datetime.utcnow()
        key = ApiKey.objects.all().order_by('lastRefresh').first()

        if not key:
            print "No Key found!"
        
        elif key.lastRefresh != None:
            age = start.replace(tzinfo=None) - key.lastRefresh.replace(tzinfo=None)
            if age.seconds < 3600:
                print "Nothing To do."
                return

            refreshKeyInfo(key)

        time = datetime.utcnow() - start
        print "Key refresh completed in", time.seconds, "seconds"
