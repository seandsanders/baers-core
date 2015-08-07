from django.db import models

# Create your models here.
class CorpMarketItem(models.Model):
	typeID = models.IntegerField()
	itemName = models.CharField(max_length=200)
	quantity = models.IntegerField()

	def __str__(self):
		return str(self.quantity)+"x "+self.itemName
