from django.core.management.base import BaseCommand
import json
from applications.models import DoctrineShipGroup, DoctrineShip, ShipRequiredSkill, DoctrineShipGroupRequiredSkill


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
                group.doctrineships.all().delete()
            group_skills = []
            for import_skill in import_group['skills']:
                group_skill = DoctrineShipGroupRequiredSkill(group=group, skillID=import_skill[0], level=import_skill[1])
                group_skills.append(group_skill)
            DoctrineShipGroupRequiredSkill.objects.bulk_create(group_skills)
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
