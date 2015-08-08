from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render
from core.models import CCPinvType, CorpAsset
from corpmarket.models import CorpMarketItem
from django.db.models import Sum
from core.views import isDropbear
import json


# Create your views here.
def resolveTypeID(request):
		term = request.GET.get("term", None)

		result = []
		if term:
			items = CCPinvType.objects.filter(typeName__icontains=term)
			for item in items[:10]:
				result.append({"id": item.typeID, "label": item.typeName, "value": item.typeName})

		return HttpResponse(json.dumps(result))

def add(request):
	if not isDropbear(request.user):
		return render(request, 'error.html', {'title': '403 - Forbidden', 'description': 'You are not a member.'})

	status = None
	if (request.method == "POST"):
		status = "Something went wrong."

		typeName = request.POST.get("item", None)
		quantity = request.POST.get("quantity", 1)

		try:
			quantity = int(quantity)
		except:
			typeName = False

		if typeName and typeName != "":
			typeID = CCPinvType.objects.filter(typeName=typeName)
			if typeID:
				typeID = typeID.first().typeID
				try:
					c = CorpMarketItem.objects.get(typeID=typeID)
				except:
					c = CorpMarketItem()

				c.typeID = typeID
				c.itemName = typeName
				c.quantity = int(quantity)

				c.save()

				if c.quantity <= 0:
					c.delete()
					status = "Removed <strong>" + typeName + "</strong> from Corp Market List!" 
				else:
					status = "Added <strong>"+ str(quantity) + "x " + typeName + "</strong> to Corp Market List!" 
			else:
				status = "Cannot find "+typeName+" in Database."
		else:
			status = "No item name supplied, or invalid quantity."




	return render(request, "add.html", {"status": status})


def list(request):
	if not isDropbear(request.user):
		return render(request, 'error.html', {'title': '403 - Forbidden', 'description': 'You are not a member.'})

	items = CorpMarketItem.objects.all()

	result = []
	chaContents = CorpAsset.objects.filter(parentID__in=[1014516459082,1014612434725,1014611085566])
	for item in items:
		chaQuantity = chaContents.filter(typeID=item.typeID).aggregate(Sum('quantity'))["quantity__sum"]
		if not chaQuantity:
			chaQuantity = 0
		result.append({
			"typeName": item.itemName,
			"quantity": chaQuantity,
			"desiredQuantity": item.quantity,
			"pct": int(100*(float(chaQuantity) / float(item.quantity)))
			})

	return render(request, "cmlist.html", {"assets": sorted(result, key=lambda k: k['pct'])})

