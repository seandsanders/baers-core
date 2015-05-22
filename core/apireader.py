import eveapi
from core.models import *
import datetime
from core import postNotification
from django.db import transaction
from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.text import slugify


def refreshCorpApi():
	keyid = settings.CORP_API_KEYID
	vcode = settings.CORP_API_VCODE

	api = eveapi.EVEAPIConnection()
	auth = api.auth(keyID=keyid, vCode=vcode)

	print "Requesting StarbaseList"
	try:
		result = auth.corp.StarbaseList()
		CorpStarbase.objects.all().delete()
		CorpStarbaseFuel.objects.all().delete()
		newFuelInfos = []
		for starbase in result.starbases:
			try:
				r2 = auth.corp.StarbaseDetail(itemID=starbase.itemID)
				lastStarbase = CorpStarbase(	itemID=starbase.itemID, 
												typeID=starbase.typeID, 
												locationID=starbase.locationID, 
												moonID=starbase.moonID, 
												state=r2.state, 
												stateTimestamp=datetime.datetime.fromtimestamp(r2.stateTimestamp), 
												onlineTimestamp=datetime.datetime.fromtimestamp(r2.onlineTimestamp),
												standingOwnerID=starbase.standingOwnerID,
												allowCorpMembers=r2.generalSettings.allowCorporationMembers,
												allowAllianceMembers=r2.generalSettings.allowAllianceMembers
											)

				lastStarbase.save()

				for fuel in r2.fuel:
					newFuelInfos.append( CorpStarbaseFuel(	pos=lastStarbase,
															typeID=fuel.typeID,
															quantity=fuel.quantity
						))
			except Exception as e:
				print "ERROR Querying StarbaseDetails:", e
			
		CorpStarbaseFuel.objects.bulk_create(newFuelInfos)

	except Exception as e:
		print "ERROR", e

	print "Requesting ContactList"
	try:
		result = auth.corp.ContactList()
		CorpContact.objects.all().delete()
		newContacts = []

		for contact in result.corporateContactList:
			newContacts.append(CorpContact(contactID=contact.contactID, contactName=contact.contactName, contactStanding=contact.standing))

		CorpContact.objects.bulk_create(newContacts)
	except Exception as e:
		print "ERROR", e
	
	print "Requesting CorpMembers"
	try:
		result = auth.corp.MemberTracking(extended=1)
		CorpMember.objects.all().delete()
		newMembers = []

		for member in result.members:
			newMembers.append(
				CorpMember(
					characterID = member.characterID,
					characterName = member.name,
					joinDate = datetime.datetime.fromtimestamp(member.startDateTime),
					title = member.title,
					logonDate = datetime.datetime.fromtimestamp(member.logonDateTime),
					logoffDate = datetime.datetime.fromtimestamp(member.logoffDateTime),
					locationID = member.locationID,
					location = member.location,
					shipTypeID = member.shipTypeID,
					roles = member.grantableRoles,
					shipType = member.shipType
				)
			)
		CorpMember.objects.bulk_create(newMembers)
	except Exception as e:
		print "ERROR", e

	if settings.ALTCORP_API_KEYID and settings.ALTCORP_API_VCODE:
		api = eveapi.EVEAPIConnection()
		auth = api.auth(keyID=settings.ALTCORP_API_KEYID, vCode=settings.ALTCORP_API_VCODE)

		print "Requesting AltCorp Members"
		try:
			result = auth.corp.MemberTracking(extended=1)
			newMembers = []

			for member in result.members:
				newMembers.append(
					CorpMember(
						characterID = member.characterID,
						characterName = member.name,
						joinDate = datetime.datetime.fromtimestamp(member.startDateTime),
						title = member.title,
						logonDate = datetime.datetime.fromtimestamp(member.logonDateTime),
						logoffDate = datetime.datetime.fromtimestamp(member.logoffDateTime),
						locationID = member.locationID,
						location = member.location,
						shipTypeID = member.shipTypeID,
						roles = member.grantableRoles,
						shipType = member.shipType,
						altCorp = True
					)
				)
			CorpMember.objects.bulk_create(newMembers)
		except Exception as e:
			print "ERROR", e

		print "Requesting AltCorp StarbaseList"
		try:
			result = auth.corp.StarbaseList()
			newFuelInfos = []
			for starbase in result.starbases:
				try:
					r2 = auth.corp.StarbaseDetail(itemID=starbase.itemID)
					lastStarbase = CorpStarbase(	itemID=starbase.itemID, 
													typeID=starbase.typeID, 
													locationID=starbase.locationID, 
													moonID=starbase.moonID, 
													state=r2.state, 
													stateTimestamp=datetime.datetime.fromtimestamp(r2.stateTimestamp), 
													onlineTimestamp=datetime.datetime.fromtimestamp(r2.onlineTimestamp),
													standingOwnerID=starbase.standingOwnerID,
													allowCorpMembers=r2.generalSettings.allowCorporationMembers,
													allowAllianceMembers=r2.generalSettings.allowAllianceMembers,
													altCorp=True
												)

					lastStarbase.save()

					for fuel in r2.fuel:
						newFuelInfos.append( CorpStarbaseFuel(	pos=lastStarbase,
																typeID=fuel.typeID,
																quantity=fuel.quantity
							))
				except Exception as e:
					print "ERROR Querying StarbaseDetails:", e
				
			CorpStarbaseFuel.objects.bulk_create(newFuelInfos)

		except Exception as e:
			print "ERROR", e

##
# Full API refresh. Calls all EVE API functions that are not within their cache time.
def refreshApis():
	return

def refreshKeyInfo(key, full=True):
	api = eveapi.EVEAPIConnection()
	auth = api.auth(keyID=key.keyID, vCode=key.vCode)
	itGrp, created = Group.objects.get_or_create(name='IT')
	inCorpGrp, created = Group.objects.get_or_create(name='Dropbears')
	recruiterGrp, created = Group.objects.get_or_create(name='Recruiter')
	hrGrp, created = Group.objects.get_or_create(name='HR')
	print "Requesting APIKeyInfo for", key.profile

	if full:
		key.lastRefresh = datetime.datetime.utcnow()
		key.save()

	incrp = False
	for char in key.profile.character_set.all():
		if char.corpID == 98224068 and char.api.valid:
			incrp = True

	if not incrp:
		key.profile.user.groups.clear()

	try:
		result = auth.account.APIKeyInfo()
	except eveapi.AuthenticationError as e:
		if not key.valid:
			return
		key.valid=False
		key.save()
		n = Notification(cssClass="danger")
		n.content = "<a href='"+reverse('core:playerProfile', kwargs={"profileName": slugify(key.profile)})+"'>"+unicode(key.profile)+"</a> has invalidated one of their API keys. (Error: '"+unicode(e)+"')"
		n.save()
		n.targetGroup.add(hrGrp)
		print unicode(key.profile)+" has invalidated one of their API keys."
		return
	except Exception as e:
		if not key.valid:
			return
		n = Notification(cssClass="warning")
		n.content = "There was an Error querying APIKeyInfo for <a href='"+reverse('core:playerProfile', kwargs={"profileName": slugify(key.profile)})+"'>"+unicode(key.profile)+"</a> (Error: '"+unicode(e)+"')"
		n.save()
		n.targetGroup.add(itGrp)
		return		
	key.accessMask = result.key.accessMask

	keyType = result.key.type
	key.accountWide = (keyType == "Account")

	expires = result.key.expires

	if (expires == ""):
		key.expiration = None
	else:
		key.expiration = datetime.datetime.fromtimestamp(expires)

	if key.accessMask != 268435455:
		if not key.valid:
			return
		key.valid = False
		key.lastRefresh = datetime.datetime.utcnow()
		key.save()
		n = Notification(cssClass="danger")
		n.content = "<a href='"+reverse('core:playerProfile', kwargs={"profileName": slugify(key.profile)})+"'>"+unicode(key.profile)+"</a> has invalidated one of their API keys. (API returned Access Mask: '"+key.accessMask+"')"
		n.save()
		n.targetGroup.add(hrGrp)
		print unicode(key.profile)+" has invalidated one of their API keys. (API returned Access Mask: '"+key.accessMask+"')"
		return

	key.valid = True
	key.save()

	for character in result.key.characters:
		try:
			char = Character.objects.get(charID=character.characterID)
			char.profile = key.profile
			char.api = key
			char.charName = character.characterName
			char.corpID = character.corporationID
			char.corpName = character.corporationName
			char.allianceID = character.allianceID
			char.allianceName = character.allianceName
		except:
			char = Character(profile=key.profile, api=key, charID=character.characterID, charName=character.characterName, corpID=character.corporationID, corpName=character.corporationName, allianceID=character.allianceID, allianceName=character.allianceName)
		if (character.corporationID == 98224068):
			key.profile.user.groups.add(inCorpGrp)

		char.save()
		refreshCharacterInfo(char, full=full)

	incrp = False
	for char in key.profile.character_set.all():
		if char.corpID == 98224068 and char.api.valid:
			incrp = True

	if not incrp:
		key.profile.user.groups.clear()

	print "Requesting AccountStatus for", key
	result = auth.account.AccountStatus()

	key.accountPaidUntil = datetime.datetime.fromtimestamp(result.paidUntil)
	key.accountCreateDate = datetime.datetime.fromtimestamp(result.createDate)
	key.accountLogonCount = result.logonCount
	key.accountLogonMinutes = result.logonMinutes
	key.lastRefresh = datetime.datetime.utcnow()

	key.save()


def refreshCharacterInfo(char, full=True):
	print "Refreshing Character Information for", char
	key = char.api
	itGrp, created = Group.objects.get_or_create(name='IT')

	api = eveapi.EVEAPIConnection()
	auth = api.auth(keyID=key.keyID, vCode=key.vCode)
	cAuth = auth.character(char.charID)

	print "Requesting CharacterSheet for", char
	try:
		result = cAuth.CharacterSheet()

		char.dateOfBirth = datetime.datetime.fromtimestamp(result.DoB)
		char.race = result.race
		char.gender = result.gender
		char.walletBalance = result.balance
		char.jumpFatigue = datetime.datetime.fromtimestamp(result.jumpFatigue)
		char.jumpActivation = datetime.datetime.fromtimestamp(result.jumpActivation)

		CharacterImplant.objects.filter(owner=char).delete()
		newImplants = []
		for implant in result.implants:
			newImplants.append( CharacterImplant(owner=char, typeID= implant.typeID) )
		CharacterImplant.objects.bulk_create(newImplants)


		CharacterTitle.objects.filter(owner=char).delete()
		newTitles = []
		for title in result.corporationTitles:
			newTitles.append( CharacterTitle(owner=char, titleName=title.titleName, titleID=title.titleID) )
		CharacterTitle.objects.bulk_create(newTitles)



		cachedSkills = CharacterSkill.objects.filter(owner=char)
		newSkills = []
		for skill in result.skills:
			try:
				changed = False
				skil = cachedSkills.get(typeID=skill.typeID)
				if (skil.skillpoints != skill.skillpoints):
					skil.skillpoints = skill.skillpoints
					changed = True
				if (skil.level != skill.level):
					skil.level=skill.level
					changed = True
				if changed: 
					skil.save()
			except:
				newSkills.append( CharacterSkill(owner=char, typeID=skill.typeID, skillpoints=skill.skillpoints, level=skill.level) )

		CharacterSkill.objects.bulk_create(newSkills)
	except:
		postNotification(target=itGrp, text="Request for CharacterSheet failed while refreshing API for "+unicode(char), cssClass="warning")

	if not full:
		return

	print "Requesting SkillInTraining for", char
	try:
		result = cAuth.SkillInTraining()
		try:
			char.skillInTrainingID = result.trainingTypeID
			char.skillInTrainingFinishes = datetime.datetime.fromtimestamp(result.trainingEndTime)
		except:
			char.skillInTrainingID = None
			char.skillInTrainingFinishes = None

		char.save()
	except:
		postNotification(target=itGrp, text="Request for SkillInTraining failed while refreshing API for "+unicode(char), cssClass="warning")


	print "Requesting CharacterInfo for", char
	try:
		result = auth.eve.CharacterInfo(characterID=char.charID)
		try:
			char.activeShipTypeName = result.shipTypeName
			char.activeShipName = result.shipName
			char.location = result.lastKnownLocation
			char.sp = result.skillPoints
			char.save()
		except:
			pass

	except:
		postNotification(target=itGrp, text="Request for CharacterInfo failed while refreshing API for "+unicode(char), cssClass="warning")

	print "Requesting AssetList for", char
	try:
		result = cAuth.AssetList()

		CharacterAsset.objects.filter(owner=char).delete()
		newAssets = []
		def crawlAssetList(assetList, newAssets, parent=None):
			for asset in assetList:
				if parent:
					newAssets.append( CharacterAsset(owner=char, itemID=asset.itemID,locationID=parent.locationID, typeID=asset.typeID, quantity=asset.quantity, flag=asset.flag, singleton=asset.singleton) )
				else:
					newAssets.append( CharacterAsset(owner=char, itemID=asset.itemID,locationID=asset.locationID, typeID=asset.typeID, quantity=asset.quantity, flag=asset.flag, singleton=asset.singleton) )
				try:
					crawlAssetList(asset.contents, newAssets, asset)
				except:
					pass

		crawlAssetList(result.assets, newAssets)
		CharacterAsset.objects.bulk_create(newAssets)
	except:
		postNotification(target=itGrp, text="Request for AssetList failed while refreshing API for "+unicode(char), cssClass="warning")

	print "Requesting ContactList for", char
	try:
		result = cAuth.ContactList()
		CharacterContact.objects.filter(owner=char).delete()
		newContacts = []
		for contact in result.contactList:
			newContacts.append( CharacterContact(owner=char, contactID=contact.contactID, contactName=contact.contactName, inWatchlist=contact.inWatchlist, standing=contact.standing))

		CharacterContact.objects.bulk_create(newContacts)
	except:
		pass
	
	print "Requesting Contracts for", char
	try:
		result = cAuth.Contracts()
		cachedContracts = CharacterContract.objects.filter(owner=char)
		newItems = []
		for contract in result.contractList:
			try:
				changed = False
				old = cachedContracts.get(contractID=contract.contractID)
				if (old.acceptorID != contract.acceptorID):
					old.acceptorID = contract.acceptorID
					changed = True
				if (old.status != contract.status):
					old.status = contract.status
					changed = True
				if (old.dateAccepted != datetime.datetime.fromtimestamp(contract.dateAccepted)):
					old.dateAccepted = datetime.datetime.fromtimestamp(contract.dateAccepted)
					changed = True
				if (old.dateAccepted != datetime.datetime.fromtimestamp(contract.dateAccepted)):
					old.dateAccepted = datetime.datetime.fromtimestamp(contract.dateAccepted)
					changed = True
				if changed: 
					old.save()
			except:
				if (contract.dateAccepted == ""):
					dateAccepted = None
				else:
					dateAccepted = datetime.datetime.fromtimestamp(contract.dateAccepted)
				if (contract.dateCompleted == ""):
					dateCompleted = None
				else:
					dateCompleted = datetime.datetime.fromtimestamp(contract.dateCompleted)

				newestContract = CharacterContract(	owner=char,
														contractID=contract.contractID,
														issuerID=contract.issuerID,
														issuerCorpID=contract.issuerCorpID,
														assigneeID=contract.assigneeID,
														acceptorID=contract.acceptorID,
														startStationID=contract.startStationID,
														endStationID=contract.endStationID,
														type=contract.type,
														status=contract.status,
														title=contract.title,
														forCorp=contract.forCorp,
														availability=contract.availability,
														dateIssued=datetime.datetime.fromtimestamp(contract.dateIssued),
														dateExpired=datetime.datetime.fromtimestamp(contract.dateExpired),
														dateAccepted=dateAccepted,
														numDays=contract.numDays,
														dateCompleted=dateCompleted,
														price=contract.price,
														reward=contract.reward,
														collateral=contract.collateral,
														buyout=contract.buyout,
														volume=contract.volume)
				newestContract.save()

				cachedItems = ContractItem.objects.filter(contract=newestContract)
				if not cachedItems: # this should never not be true, but better make sure we dont add duplicates
					print "Requesting Contractitems for", char
					try:
						itemsresult = cAuth.ContractItems(contractID=contract.contractID)
						for item in itemsresult.itemList:
							newItems.append( ContractItem(contract=newestContract, recordID=item.recordID, typeID=item.typeID, quantity=item.quantity, singleton=item.singleton, included=item.included) )			
						ContractItem.objects.bulk_create(newItems)
					except:
						pass
	except:
		postNotification(target=itGrp, text="Request for ContactList failed while refreshing API for "+unicode(char), cssClass="warning")


	#print "Requesting Killlog for", char
	print "Skipping KillLog because CCP is really paranoid about it and I'm too lazy to actually look at the cache time"
	#try:
	#	result = cAuth.Killlog()
	#	cachedKills = CharacterKill.objects.filter(owner=char)
	##	newAttackers = []	
	##	newItems = []
	##	for kill in result.kills:
	##		try:
	##			cachedKills.get(killID=kill.killID)
	##		except:
	##			newestKill = CharacterKill(	owner=char,						
	##										killID=kill.killID,
	##										solarSystemID=kill.solarSystemID,
	##										killTime=datetime.datetime.fromtimestamp(kill.killTime),
	##										victimAllianceID=kill.victim.allianceID,
	##										victimAllianceName=kill.victim.allianceName,
	##										victimCharacterID=kill.victim.characterID,
	##										victimCharacterName=kill.victim.characterName,
	##										victimCorporationID=kill.victim.corporationID,
	##										victimCorporationName=kill.victim.corporationName,
	##										victimDamageTaken=kill.victim.damageTaken,
	##										victimShipTypeID=kill.victim.shipTypeID )
	##			newestKill.save()
##
##				cachedAttackers = KillmailAttackers.objects.filter(killmail=newestKill)
##				if not cachedAttackers:
##					for attacker in kill.attackers:
##						newAttackers.append( KillmailAttackers(	killmail = newestKill,
##																allianceID=attacker.allianceID,
##																allianceName=attacker.allianceName,
##																corporationID=attacker.corporationID,
##																corporationName=attacker.corporationName,
##																characterID=attacker.characterID,
##																characterName=attacker.characterName,
##																damageDone=attacker.damageDone,
##																finalBlow=attacker.finalBlow,
##																shipTypeID=attacker.shipTypeID,
##																weaponTypeID=attacker.weaponTypeID) )
##				cachedItems = KillmailItems.objects.filter(killmail=newestKill)
##				if not cachedAttackers:
##					for item in kill.items:
##						newItems.append( KillmailItems(	killmail = newestKill,
##															flag=item.flag,
##															qtyDropped=item.qtyDropped,
##															qtyDestroyed=item.qtyDestroyed,
##															typeID=item.typeID,
##															singleton=item.singleton ) )		
##
##		KillmailAttackers.objects.bulk_create(newAttackers)
##		KillmailItems.objects.bulk_create(newItems)
##		killmail = models.ForeignKey(CharacterKill)
##	except:
#		postNotification(target=itGrp, text="Request for Killlog failed while refreshing API for "+unicode(char), cssClass="warning")

	print "Requesting MailMessages for", char
	try:
		result = cAuth.MailMessages()

		newMails = []
		mailsToQuery = []
		cachedMails = CharacterMail.objects.filter(owner=char)
		for mail in result.messages:
			try:
				cachedMails.get(messageID=mail.messageID)
			except:
				newMails.append( CharacterMail(	owner=char,
												messageID=mail.messageID,
												senderID=mail.senderID,
												sentDate=datetime.datetime.fromtimestamp(mail.sentDate),
												title=mail.title,
												toCorpOrAllianceID=mail.toCorpOrAllianceID,
												toCharacterIDs=mail.toCharacterIDs,
												toListID=mail.toListID ))
				mailsToQuery.append(unicode(mail.messageID))
		CharacterMail.objects.bulk_create(newMails)
			
		if len(mailsToQuery):
			newMails = []
			result = cAuth.MailBodies(ids=",".join(mailsToQuery))
			cachedMails = MailBody.objects.all()
			for mail in result.messages:
				try:
					cachedMails.get(messageID=mail.messageID)
				except:
					newMails.append( MailBody(	messageID=mail.messageID,
													body=mail.data ))
			MailBody.objects.bulk_create(newMails)
	except:
		postNotification(target=itGrp, text="Request for MailMessages failed while refreshing API for "+unicode(char), cssClass="warning")

	print "Requesting MarketOrders for", char
	try:
		result = cAuth.MarketOrders()
		CharacterMarketOrder.objects.filter(owner=char).delete()
		newObjects = []
		for order in result.orders:
			newObjects.append( CharacterMarketOrder(owner=char, 
													orderID=order.orderID,
													charID=order.charID,
													stationID=order.stationID,
													volEntered=order.volEntered,
													volRemaining=order.volRemaining,
													minVolume=order.minVolume,
													orderState=order.orderState,
													typeID=order.typeID,
													range=order.range,
													accountKey=order.accountKey,
													duration=order.duration,
													escrow=order.escrow,
													price=order.price,
													bid=order.bid,
													issued=datetime.datetime.fromtimestamp(order.issued)) )
		
		CharacterMarketOrder.objects.bulk_create(newObjects)
	except:
		postNotification(target=itGrp, text="Request for MarketOrders failed while refreshing API for "+unicode(char), cssClass="warning")

	print "Requesting Notifications for", char
	try:
		newNotifications = []
		notificationsToQuery = []
		cachedNotifications = CharacterNotification.objects.filter(owner=char)
		result = cAuth.Notifications()
		for notification in result.notifications:
			try:
				cachedNotifications.get(notificationID=notification.notificationID)
			except:
				newNotifications.append( CharacterNotification(	owner=char,
																notificationID=notification.notificationID,
																typeID=notification.typeID,
																senderID=notification.senderID,
																sentDate=datetime.datetime.fromtimestamp(notification.sentDate),
																read=notification.read))
				notificationsToQuery.append(unicode(notification.notificationID))

		CharacterNotification.objects.bulk_create(newNotifications)

		if len(notificationsToQuery):
			newNotifications = []
			result = cAuth.NotificationTexts(ids=",".join(notificationsToQuery))
			cachedNotifications = NotificationText.objects.all()
			for notification in result.notifications:
				try:
					cachedNotifications.get(messageID=mail.messageID)
				except:
					newNotifications.append( NotificationText(	notificationID=notification.notificationID,
																body=notification.data ))
			NotificationText.objects.bulk_create(newNotifications)
	except:
		postNotification(target=itGrp, text="Request for Notifications failed while refreshing API for "+unicode(char), cssClass="warning")

	print "Requesting WalletJournal for", char
	try:
		newTransactions = []
		cachedTransactions = WalletJournal.objects.filter(owner=char)
		result = cAuth.WalletJournal()
		for transaction in result.transactions:
			try:
				cachedTransactions.get(refID=transaction.refID)
			except:
				newTransactions.append( WalletJournal(	owner=char,
														date=datetime.datetime.fromtimestamp(transaction.date),
														refID=transaction.refID,
														refTypeID=transaction.refTypeID,
														ownerName1=transaction.ownerName1,
														ownerID1=transaction.ownerID1,
														ownerName2=transaction.ownerName2,
														ownerID2=transaction.ownerID2,
														argName1=transaction.argName1,
														argID1=transaction.argID1,
														amount=transaction.amount,
														balance=transaction.balance,
														reason=transaction.reason ))
		WalletJournal.objects.bulk_create(newTransactions)
	except:
		postNotification(target=itGrp, text="Request for WalletJournal failed while refreshing API for "+unicode(char), cssClass="warning")

	print "Requesting WalletTransactions for", char
	try:
		newTransactions = []
		cachedTransactions = WalletTransactions.objects.filter(owner=char)
		result = cAuth.WalletTransactions()
		for transaction in result.transactions:
			try:
				cachedTransactions.get(transactionID=transaction.transactionID)
			except:
				newTransactions.append( WalletTransactions(	owner=char,
															transactionDateTime=datetime.datetime.fromtimestamp(transaction.transactionDateTime),
															transactionID=transaction.transactionID,
															quantity=transaction.quantity,
															typeName=transaction.typeName,
															typeID=transaction.typeID,
															price=transaction.price,
															clientID=transaction.clientID,
															clientName=transaction.clientName,
															stationID=transaction.stationID,
															stationName=transaction.stationName,
															transactionType=transaction.transactionType,
															transactionFor=transaction.transactionFor,
															journalTransactionID=transaction.journalTransactionID))
		WalletTransactions.objects.bulk_create(newTransactions)
	except:
		postNotification(target=itGrp, text="Request for WalletTransactions failed while refreshing API for "+unicode(char), cssClass="warning")



def validateKey(keyID, vCode):
	try:
		key = ApiKey.objects.get(keyID=keyID, deleted=False)
		return None, "The Key you provided is already in the database."
	except:
		pass
	api = eveapi.EVEAPIConnection()
	auth = api.auth(keyID=keyID, vCode=vCode)
	try:
		result = auth.account.APIKeyInfo()
	except:
		return None, "The Key you provided is invalid."

	if (result.key.expires != ""):
		return None, "The Key you provided has an expiration date set."
	if result.key.accessMask != 268435455:
		return None, "The Key you provided is not a full access key."
	if result.key.type != "Account":
		return None, "The Key you provided is not a full Account key."

	charlist = []
	storedChars = Character.objects.all()
	for character in result.key.characters:
		try:
			storedChars.get(charID=character.characterID)
			if not char.apikey.deleted:
				return None, "The character "+character.characterName+" is already in the database."
		except:
			charlist.append({"charID": character.characterID, "charName": character.characterName})
	return charlist, None

# /corp/StarbaseList.xml.aspx
# /corp/StarbaseDetail.xml.aspx
# /corp/ContactList.xml.aspx
# /corp/MemberTracking.xml.aspx

