from django.shortcuts import render
from core.views import isHR
from core.models import CCPinvType, Character

# Create your views here.
def skillcheck(request):
    if not isHR(request.user):
        return render(request, 'error.html', {'title': '403 - Forbidden', 'description': 'You are not HR.'})
    errors = []
    filters = []
    c = None
    if request.method == "POST":
        items = request.POST.getlist("item")
        levels = request.POST.getlist("level")

        c = Character.objects.filter(profile__user__groups__name="Member")

        for idx,item in enumerate(items):
            print item
            if item.strip() == "":
                continue

            try:
                typeID = CCPinvType.objects.get(typeName=item).typeID
            except:
                errors.append("'"+item+"' is not a valid type.")
                continue

            try:
                level = int(levels[idx])
            except:
                level = 0

            c = c.filter(characterskill__typeID=typeID, characterskill__level__gte=level)
            filters.append([item,level])


    return render(request, 'skillcheck.html', {"errors": errors, "filters": filters, "chars": c})