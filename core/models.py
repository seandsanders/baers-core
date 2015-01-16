from django.db import models
from django.conf import settings
from django.contrib.auth.models import Group


# Create your models here.

##
# User Management
class UserProfile(models.Model):
	user = models.OneToOneField(settings.AUTH_USER_MODEL)
	mainChar = models.OneToOneField('Character')
	squad = models.IntegerField()

	def __str__(self):
		return self.mainChar.__str__()


##
# Notifications
class Notification(models.Model):
	content = models.CharField(max_length=200)
	targetUsers = models.ManyToManyField(UserProfile)
	targetGroup = models.ManyToManyField(Group)

	def __str__(self):
		return content


##
# API Management
#
# store every call as listed on http://wiki.eve-id.net/APIv2_Page_Index
#
# except: 
# /account/Characters.xml.aspx (seems to be redundant, information returned from APIKeyInfo includes this)
# /api/CallList.xml.aspx (no need to store)
# /char/AccountBalance.xml.aspx (redundtant, provided by CharacterSheet)
# /char/ContactNotifications.xml.aspx (covered by Notifications)
# /char/ContractBids.xml.aspx (who even cares)
# /char/FacWarStats.xml.aspx (we're not in Faction warfare and probably never going to be)
# /char/IndustryJobs.xml.aspx (irrelevant)
# /char/Medals.xml.aspx (most useless thing in the game)
# /char/Research.xml.aspx (don't care)



# /account/APIKeyInfo.xml.aspx
class ApiKey(models.Model):
	profile = models.ForeignKey(UserProfile)
	keyID = models.IntegerField()
	vCode = models.CharField(max_length=100)

	accessMask = models.CharField(max_length=20)
	expiration = models.DateTimeField()

	#/account/AccountStatus.xml.aspx
	accountPaidUntil = models.DateTimeField()
	accountCreateDate = models.DateTimeField()
	accountLogonCount = models.IntegerField()
	accountLogonMinutes = models.IntegerField()

	def __str__(self):
		return unicode(self.keyID)+":"+self.vCode

class Character(models.Model):
	profile = models.ForeignKey(UserProfile)
	api = models.ForeignKey(ApiKey)

	# /account/APIKeyInfo.xml.aspx	
	charID = models.IntegerField()
	charName = models.CharField(max_length=200)

	corpID = models.IntegerField()
	corpName = models.CharField(max_length=200)
	corpTicker = models.CharField(max_length=6)

	allianceID = models.IntegerField()
	allianceName = models.CharField(max_length=200)
	allianceTicker = models.CharField(max_length=6)

	#/char/CharacterSheet.xml.aspx
	dateOfBirth = models.DateTimeField()
	race = models.CharField(max_length=10)
	gender = models.CharField(max_length=6) # I wonder if max_length of 6 covers all preferred pronouns *triggerwarning*
	walletBalance = models.IntegerField()

	jumpFatigue = models.DateTimeField()
	jumpActivation = models.DateTimeField()

	#/char/SkillInTraining.xml.aspx
	skillInTrainingID = models.IntegerField()
	skillInTrainingFinishes = models.DateTimeField()


	def __str__(self):
		return self.charName

#/char/AssetList.xml.aspx
class CharacterAsset(models.Model):
	owner = models.ForeignKey(Character)
	itemID = models.IntegerField()
	locationID = models.IntegerField()
	typeID = models.IntegerField()
	quantity = models.IntegerField()
	flag = models.IntegerField()
	singleton = models.IntegerField()
	rawQuantity = models.IntegerField()

#/char/CalendarEventAttendees.xml.aspx
class CalendarEventAttendee(models.Model):
	owner = models.ForeignKey(Character)
	characterID = models.IntegerField()
	characterName = models.CharField(max_length=100)
	response = models.CharField(max_length=10)

# /char/CharacterSheet.xml.aspx
class CharacterImplant(models.Model):
	owner = models.ForeignKey(Character)

	typeID = models.IntegerField()
	# not storing typeName, we'll need a staticdata export anyway, can be joined if needed

# /char/CharacterSheet.xml.aspx
class CharacterTitle(models.Model):
	owner = models.ForeignKey(Character)

	titleID = models.IntegerField()
	titleName = models.CharField(max_length=100)

# /char/CharacterSheet.xml.aspx
class CharacterSkill(models.Model):
	owner = models.ForeignKey(Character)

	typeID = models.IntegerField()
	skillpoints = models.IntegerField()
	level = models.IntegerField()

# /char/ContactList.xml.aspx
class CharacterContact(models.Model):
	owner = models.ForeignKey(Character)

	contactID = models.IntegerField()
	contactName = models.CharField(max_length=100)
	inWatchlist = models.BooleanField()
	standing = models.IntegerField()
	contactType = models.IntegerField() # 0 personal contact, 1 corp contact, 2 alliance contact

# /char/Contracts.xml.aspx
class CharacterContract(models.Model):
	owner = models.ForeignKey(Character)

	contractID = models.IntegerField()
	issuerID = models.IntegerField()
	issuerCorpID = models.IntegerField()
	assigneeID = models.IntegerField()
	acceptorID = models.IntegerField()
	startStationID = models.IntegerField()
	endStationID = models.IntegerField()
	type = models.CharField(max_length=20)
	status = models.CharField(max_length=30)
	title = models.CharField(max_length=100)
	forCorp = models.BooleanField()
	availability = models.CharField(max_length=10)
	dateIssued = models.DateTimeField()
	dateExpired = models.DateTimeField()
	dateAccepted = models.DateTimeField()
	numDays = models.IntegerField()
	dateCompleted = models.DateTimeField()
	price = models.FloatField()
	reward = models.FloatField()
	collateral = models.FloatField()
	buyout = models.FloatField()
	volume = models.FloatField()


# /char/ContractItems.xml.aspx
class ContractItems(models.Model):
	contract = models.ForeignKey(CharacterContract)

	recordID = models.IntegerField()
	typeID = models.IntegerField()
	quantity = models.IntegerField()
	rawQuantity = models.IntegerField()
	singleton = models.BooleanField()
	included = models.BooleanField()

# /char/KillLog.xml.aspx
class CharacterKill(models.Model):
	owner = models.ForeignKey(Character)

	killID = models.IntegerField()
	solarSystemID = models.IntegerField()
	killTime = models.DateTimeField()

	victimAllianceID = models.IntegerField()
	victimAllianceName = models.CharField(max_length=100)
	victimCharacterID = models.IntegerField()
	victimCharacterName = models.CharField(max_length=100)
	victimCorporationID = models.IntegerField()
	victimCorporationName = models.CharField(max_length=100)
	victimDamageTaken = models.IntegerField()
	victimShipTypeID = models.IntegerField()

# /char/KillLog.xml.asp
class KillmailAttackers(models.Model):
	killmail = models.ForeignKey(CharacterKill)

	allianceID = models.IntegerField()
	allianceName = models.CharField(max_length=100)

	corporationID = models.IntegerField()
	corporationName = models.CharField(max_length=100)

	characterID = models.IntegerField()
	characterName = models.CharField(max_length=100)

	damageDone = models.IntegerField()

	finalBlow = models.BooleanField()
	shipTypeID = models.IntegerField()
	weaponTypeID = models.IntegerField()

# /char/KillLog.xml.asp
class KillmailItems(models.Model):
	killmail = models.ForeignKey(CharacterKill)

	flag = models.IntegerField()
	qtyDropped = models.IntegerField()
	qtyDestroyed = models.IntegerField()
	typeID = models.IntegerField()
	singleton = models.IntegerField()


# /char/MailMessages.xml.aspx
# /char/MailBodies.xml.aspx
class CharacterMail(models.Model):
	owner = models.ForeignKey(Character)

	messageID = models.IntegerField()
	senderID = models.IntegerField()
	sentDate = models.DateTimeField()
	title = models.CharField(max_length=200)
	toCorpOrAllianceID = models.CharField(max_length=200)
	toCharacterIDs = models.CharField(max_length=200)
	toListID = models.CharField(max_length=200)

	body = models.CharField(max_length=1024)



# /char/MarketOrders.xml.aspx
class CharacterMarketOrder(models.Model):
	owner = models.ForeignKey(Character)

	orderID = models.IntegerField()
	charID = models.IntegerField()
	stationID = models.IntegerField()
	volEntered = models.IntegerField()
	volRemaining = models.IntegerField()
	minVolume = models.IntegerField()
	orderState = models.IntegerField()
	typeID = models.IntegerField()
	range = models.IntegerField()
	accountKey = models.IntegerField()
	duration = models.IntegerField()
	escrow = models.FloatField()
	price = models.FloatField()
	bid = models.BooleanField()
	issued = models.DateTimeField()

# /char/Notifications.xml.aspx
# /char/NotificationTexts.xml.aspx
class CharacterNotification(models.Model):
	owner = models.ForeignKey(Character)

	notificationID = models.IntegerField()
	typeID = models.IntegerField()
	senderID = models.IntegerField()
	sentDate = models.DateTimeField()
	read = models.BooleanField()

	body = models.CharField(max_length=1024)

# /char/WalletJournal.xml.aspx
class WalletJournal(models.Model):
	owner = models.ForeignKey(Character)

	date = models.DateTimeField()
	refID = models.IntegerField()
	refTypeID =  models.IntegerField()
	ownerName1 = models.CharField(max_length=100)
	ownerID1 = models.IntegerField()
	ownerName2 = models.CharField(max_length=100)
	ownerID2 = models.IntegerField()
	argName1 = models.CharField(max_length=50)
	argID1 = models.IntegerField()
	amount = models.FloatField()
	balance = models.FloatField()
	reason = models.CharField(max_length=200)

# /char/WalletTransactions.xml.aspx
class WalletTransactions(models.Model):
	owner = models.ForeignKey(Character)

	transactionDateTime = models.DateTimeField()
	transactionID = models.IntegerField()
	quantity = models.IntegerField()
	typeName = models.CharField(max_length=100)
	typeID = models.IntegerField()
	price = models.IntegerField()
	clientID = models.IntegerField()
	clientName = models.CharField(max_length=100)
	stationID = models.IntegerField()
	stationName = models.CharField(max_length=200)
	transactionType = models.CharField(max_length=5)
	transactionFor = models.CharField(max_length=15)
	journalTransactionID = models.IntegerField()

##
# Corp API information
# instead of caching the whole key like we do for characters, we don't really need to do that here, so we're just storing what we need


# /corp/StarbaseList.xml.aspx
# /corp/StarbaseDetail.xml.aspx
class CorpStarbase(models.Model):

	itemID = models.IntegerField()
	typeID = models.IntegerField()
	locationID = models.IntegerField()
	moonID = models.IntegerField()
	state = models.IntegerField()
	stateTimestamp = models.DateTimeField()
	onlineTimestamp = models.DateTimeField()
	standingOwnerID = models.IntegerField()

	allowCorpMembers = models.BooleanField()
	allowAllianceMembers = models.BooleanField()

# /corp/StarbaseDetail.xml.aspx
class CorpStarbaseFuel(models.Model):
	pos = models.ForeignKey(CorpStarbase)

	typeID = models.IntegerField()
	quantity = models.IntegerField()

# /corp/ContactList.xml.aspx
class CorpContact(models.Model):
	contactID = models.IntegerField()
	contactName = models.CharField(max_length=100)
	contactStanding = models.IntegerField()


# /corp/MemberTracking.xml.aspx
class CorpMember(models.Model):
	characterID = models.IntegerField()
	characterName = models.CharField(max_length=100)
	joinDate = models.DateTimeField()
	title = models.CharField(max_length=200)
	logonDate = models.DateTimeField()
	logoffDate = models.DateTimeField()
	locationID = models.IntegerField()
	location = models.CharField(max_length=200)
	shipTypeID = models.IntegerField()
	roles = models.IntegerField()
