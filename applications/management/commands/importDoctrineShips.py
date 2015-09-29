from django.core.management.base import BaseCommand
import json
from applications.models import DoctrineShipGroup, DoctrineShip, ShipRequiredSkill


class Command(BaseCommand):
    help = "Imports doctrine ships from a file in json format. Format should follow sampleships.json"

    def add_arguments(self, parser):
        parser.add_argument('file', type=str)

    def handle(self, *args, **options):
        with open(options['file'], 'r') as f:
            data = json.loads(f.read())

        for import_group in data:
            group, created = DoctrineShipGroup.objects.get_or_create(name=import_group['group'])
            if not created:
                group.doctrineship_set.all().delete()

            for import_ship in import_group['ships']:
                ship = DoctrineShip(group=group,
                                    shipID=import_ship['shipID'],
                                    name=import_ship['name'])
                ship.save()
                skills = []
                for import_skill in import_ship['skills']:
                    skill = ShipRequiredSkill(ship=ship, skillID=import_skill[0], level=import_skill[1])
                    skills.append(skill)

                ShipRequiredSkill.objects.bulk_create(skills)
