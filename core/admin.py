from django.contrib import admin
from core.models import *;

# Register your models here.
admin.site.register(UserProfile)
admin.site.register(ApiKey)
admin.site.register(Character)

admin.site.register(Notification)

admin.site.register(CharacterSkill)
admin.site.register(CharacterTitle)
admin.site.register(CharacterImplant)
admin.site.register(CharacterAsset)
admin.site.register(CharacterContact)
admin.site.register(CharacterContract)
admin.site.register(ContractItem)
admin.site.register(CharacterKill)
admin.site.register(MailBody)
admin.site.register(CharacterMail)
admin.site.register(CharacterMarketOrder)
admin.site.register(CharacterNotification)
admin.site.register(NotificationText)
admin.site.register(WalletTransactions)
admin.site.register(WalletJournal)

admin.site.register(CorpMember)
admin.site.register(CorpStarbase)
admin.site.register(CorpStarbaseFuel)
admin.site.register(CorpContact)
