from django.contrib import admin
from applications.models import *

# Register your models here.
admin.site.register(DoctrineShipGroup)
admin.site.register(DoctrineShip)
admin.site.register(ShipRequiredSkill)