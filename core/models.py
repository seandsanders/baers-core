from django.db import models
from django.conf import settings
from django.contrib.auth.models import Group, User
from datetime import datetime


# Create your models here.

##
# User Management
class UserProfile(models.Model):
	user = models.OneToOneField(settings.AUTH_USER_MODEL)
	mainChar = models.OneToOneField('Character', null=True)
	squad = models.IntegerField(null=True)
	mentor = models.ForeignKey('UserProfile', null=True)
	tzoffset = models.IntegerField(null=True)

	def __str__(self):
		return self.mainChar.__str__()


##
# Notifications
class Notification(models.Model):
	content = models.CharField(max_length=2048)
	time = models.DateTimeField(auto_now_add=True)
	targetUsers = models.ManyToManyField(User)
	targetGroup = models.ManyToManyField(Group)
	cssClass = models.CharField(max_length=20)

	def __str__(self):
		return self.content


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
	accountWide = models.BooleanField(default=True)

	valid = models.BooleanField(default=True)
	deleted = models.BooleanField(default=False) 
	lastRefresh = models.DateTimeField(default=datetime(1900,1,1))
	

	accessMask = models.CharField(max_length=20,null=True)
	expiration = models.DateTimeField(null=True)

	#/account/AccountStatus.xml.aspx
	accountPaidUntil = models.DateTimeField(null=True)
	accountCreateDate = models.DateTimeField(null=True)
	accountLogonCount = models.IntegerField(null=True)
	accountLogonMinutes = models.IntegerField(null=True)

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

	allianceID = models.IntegerField()
	allianceName = models.CharField(max_length=200)

	#/char/CharacterSheet.xml.aspx
	dateOfBirth = models.DateTimeField(null=True)
	race = models.CharField(max_length=10,null=True)
	gender = models.CharField(max_length=6,null=True) # I wonder if max_length of 6 covers all preferred pronouns *triggerwarning*
	walletBalance = models.BigIntegerField(null=True)
	sp = models.IntegerField(null=True)

	jumpFatigue = models.DateTimeField(null=True)
	jumpActivation = models.DateTimeField(null=True)

	#/char/SkillInTraining.xml.aspx
	skillInTrainingID = models.IntegerField(null=True)
	skillInTrainingFinishes = models.DateTimeField(null=True)

	#/eve/CharacterInfo.xml.aspx
	activeShipTypeName = models.CharField(max_length=100, null=True)
	activeShipName = models.CharField(max_length=200, null=True)
	location = models.CharField(max_length=200, null=True)

	def __str__(self):
		return self.charName

#/char/AssetList.xml.aspx
class CharacterAsset(models.Model):
	owner = models.ForeignKey(Character)
	itemID = models.BigIntegerField()
	locationID = models.IntegerField()
	typeID = models.IntegerField()
	quantity = models.IntegerField()
	flag = models.IntegerField()
	singleton = models.IntegerField()
	rawQuantity = models.IntegerField(null=True)
	def __str__(self):
		return unicode(self.quantity)+"x"+unicode(self.typeID)

# /char/CharacterSheet.xml.aspx
class CharacterImplant(models.Model):
	owner = models.ForeignKey(Character)

	typeID = models.IntegerField()
	# not storing typeName, we'll need a staticdata export anyway, can be joined if needed
	def __str__(self):
		return self.typeID

# /char/CharacterSheet.xml.aspx
class CharacterTitle(models.Model):
	owner = models.ForeignKey(Character)

	titleID = models.IntegerField()
	titleName = models.CharField(max_length=100)
	def __str__(self):
		return self.titleName

# /char/CharacterSheet.xml.aspx
class CharacterSkill(models.Model):
	owner = models.ForeignKey(Character)

	typeID = models.IntegerField()
	skillpoints = models.IntegerField()
	level = models.IntegerField()
	def __str__(self):
		return unicode(self.typeID)+" lv"+unicode(self.level)

# /char/ContactList.xml.aspx
class CharacterContact(models.Model):
	owner = models.ForeignKey(Character)

	contactID = models.IntegerField()
	contactName = models.CharField(max_length=100)
	inWatchlist = models.BooleanField()
	standing = models.IntegerField()
	def __str__(self):
		return self.contactName+" ("+unicode(self.standing)+")"

# /char/Contracts.xml.aspx
class CharacterContract(models.Model):
	owner = models.ForeignKey(Character)

	contractID = models.BigIntegerField()
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
	dateAccepted = models.DateTimeField(null=True)
	numDays = models.IntegerField()
	dateCompleted = models.DateTimeField(null=True)
	price = models.FloatField()
	reward = models.FloatField()
	collateral = models.FloatField()
	buyout = models.FloatField()
	volume = models.FloatField()

	def __str__(self):
		return self.availability+" "+self.type

# /char/ContractItems.xml.aspx
class ContractItem(models.Model):
	contract = models.ForeignKey(CharacterContract)

	recordID = models.BigIntegerField()
	typeID = models.IntegerField()
	quantity = models.IntegerField()
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
class CharacterMail(models.Model):
	owner = models.ForeignKey(Character)

	messageID = models.IntegerField()
	senderID = models.IntegerField()
	sentDate = models.DateTimeField()
	title = models.CharField(max_length=200)
	toCorpOrAllianceID = models.CharField(max_length=200)
	toCharacterIDs = models.CharField(max_length=200)
	toListID = models.CharField(max_length=200)


# /char/MailBodies.xml.aspx
class MailBody(models.Model):
	messageID = models.IntegerField()
	body = models.CharField(max_length=8192) # ingame character limit is 8000, but I like powers of two



# /char/MarketOrders.xml.aspx
class CharacterMarketOrder(models.Model):
	owner = models.ForeignKey(Character)

	orderID = models.BigIntegerField()
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

	notificationID = models.BigIntegerField()
	typeID = models.IntegerField()
	senderID = models.IntegerField()
	sentDate = models.DateTimeField()
	read = models.BooleanField()

class NotificationText(models.Model):
	notificationID = models.BigIntegerField()
	body = models.CharField(max_length=4096)

# /char/WalletJournal.xml.aspx
class WalletJournal(models.Model):
	owner = models.ForeignKey(Character)

	date = models.DateTimeField()
	refID = models.BigIntegerField()
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
	transactionID = models.BigIntegerField()
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
	journalTransactionID = models.BigIntegerField()

##
# Corp API information
# instead of caching the whole key like we do for characters, we don't really need to do that here, so we're just storing what we need


# /corp/StarbaseList.xml.aspx
# /corp/StarbaseDetail.xml.aspx
class CorpStarbase(models.Model):
	itemID = models.BigIntegerField()
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
	shipType = models.CharField(max_length=100)
	roles = models.BigIntegerField()
	altCorp = models.BooleanField(default=False)


class StarbaseNote(models.Model):
	starbaseID = models.BigIntegerField() 
	note = models.CharField(max_length=1000)

class StarbaseOwner(models.Model):
	starbaseID = models.BigIntegerField() 
	owner = models.ForeignKey(UserProfile, null=True)

##
# Store cache times in a table
class CacheTimer(models.Model):
	targetCharacter = models.ForeignKey(Character, null=True)
	targetKey = models.ForeignKey(ApiKey, null=True)
	callName = models.CharField(max_length=100)
	cachedUntil = models.DateTimeField()


class Haiku(models.Model):
	author = models.CharField(max_length=100)
	text = models.CharField(max_length=1000)