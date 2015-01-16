from django.contrib import admin
from core.models import *;

# Register your models here.
admin.site.register(UserProfile)
admin.site.register(ApiKey)
admin.site.register(Character)

admin.site.register(Notification)
