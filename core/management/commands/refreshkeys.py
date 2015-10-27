from django.core.management.base import BaseCommand

from datetime import datetime
from core.apireader import refreshKeyInfo
from core.models import ApiKey

class Command(BaseCommand):
    help = 'Refreshes the key with the most outdated information.'

    def add_arguments(self, parser):
        parser.add_argument('--key',
                            action='store',
                            dest='keyID',
                            default=None,
                            help='Run a specific key by keyID')
        parser.add_argument('--force',
                            action='store_true',
                            dest='force',
                            default=False,
                            help='Force rerun even if within refresh interval.')

    def handle(self, *args, **options):
        start = datetime.utcnow()

        if options['keyID'] is not None:
            try:
                key = ApiKey.objects.get(keyID=options['keyID'])
            except ApiKey.DoesNotExist:
                print "KeyID does not exist"
                return
        else:
            key = ApiKey.objects.order_by('lastRefresh').first()

        if not key:
            print "No Key found!"

        elif key.lastRefresh is not None:
            age = start.replace(tzinfo=None) - key.lastRefresh.replace(tzinfo=None)
            if age.seconds < 3600 and not options['force']:
                print "Nothing To do."
                return

            refreshKeyInfo(key)

        time = datetime.utcnow() - start
        print "Key refresh completed in", time.seconds, "seconds"
