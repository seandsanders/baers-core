from django.shortcuts import render
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseForbidden
from helpdesk.models import Ticket, Comment
from core.models import Notification, Character
import urllib2, json, gzip, random
from StringIO import StringIO
import eveapi, string
from datetime import datetime
from django.db.models import Sum
from django.core.urlresolvers import reverse
from django.contrib.auth.models import Group
from django.utils.text import slugify

# Create your views here.

def isFinance(user):
    return user.groups.filter(name='Finance').exists()
def isDropbears(user):
    return user.groups.filter(name='Member').exists()
def isDirector(user):
    return user.groups.filter(name='Director').exists()

def ticketAdmin(request):
    if not isDirector(request.user):
        return render(request, 'error.html', {'title': '403 - Forbidden', 'description': 'You have no permission to view this page.'})
    tickets = Ticket.objects.all()
    
    open = tickets.filter(status__lt=2)
    resolved = tickets.filter(status=2)

    c = {
        "open": open,
        "resolved": resolved,
    }

    return render(request, 'ticketlist.html', c)

def ticketList(request):
    if not isDropbears(request.user):
        return render(request, 'error.html', {'title': '403 - Forbidden', 'description': 'You are not a member.'})
    
    myTickets = Ticket.objects.filter(author=request.user.userprofile)
    #assignedTickets = Ticket.objects.filter(assignedTo=request.user.userprofile)
    
    myOpen = myTickets.filter(status__lte=1)
    myResolved = myTickets.filter(status=2)

    #assignedOpen = assignedTickets.filter(status__lte=1)
    #assignedResolved = assignedTickets.filter(status=2)


    c = {
        "open": myOpen,
        "resolved": myResolved,
        #"assignedOpen": assignedOpen,
        #"assignedResolved": assignedResolved
    }
    return render(request, 'ticketlist.html', c)

def viewTicket(request, token):
    ticket = Ticket.objects.get(token=token)
    f = isDirector(request.user)
    if not (f or not ticket.author or request.user.userprofile == ticket.author):
        return render(request, 'error.html', {'title': '403 - Forbidden', 'description': 'You do not have permission to view this page.'})

    if request.method == "POST":
        
        director = Group.objects.filter(name="Director").first()
        oldstatus = ticket.get_status_display()

        if request.POST.get('newComment', False):
            
            c = Comment()
            c.text = request.POST.get('commentbody')
            c.author = request.user.userprofile
            c.date = datetime.utcnow()
            c.ticket = ticket
            c.private = request.POST.get('private') == "on"
            c.save()

            
            note = Notification(cssClass="info")
            note.content="<a href='"+reverse('core:playerProfile', kwargs={"profileName": slugify(request.user.userprofile)})+"'>"+unicode(c.author)+"</a> commented on <a href='"+reverse('helpdesk:viewticket', kwargs={"token": ticket.token})+"'>Ticket #"+str(ticket.id)+" \""+ticket.title+"\"</a>"
            note.save()
            note.targetGroup.add(director)
            if ticket.author and not c.private:
                note.targetUsers.add(ticket.author.user)

        elif request.POST.get('inprogress', False) and ticket.status != 1 and f:
            ticket.status = 1
            n = Notification(cssClass='success', content="<a href='"+reverse('helpdesk:viewticket', kwargs={"token": ticket.token})+"'>Ticket #"+str(ticket.id)+" \""+ticket.title+"\"</a> has been set to \"In Progress\" by <a href='"+reverse('core:playerProfile', kwargs={"profileName": slugify(request.user.userprofile)})+"'>"+unicode(request.user.userprofile)+"</a>")
            n.save()
            if ticket.author:
                n.targetUsers.add(ticket.author.user)
            n.targetGroup.add(director)

        elif request.POST.get('resolved', False) and ticket.status != 2 and f:
            ticket.status = 2
            n = Notification(cssClass='success', content="<a href='"+reverse('helpdesk:viewticket', kwargs={"token": ticket.token})+"'>Ticket #"+str(ticket.id)+" \""+ticket.title+"\"</a> has been set to \"Resolved\" by <a href='"+reverse('core:playerProfile', kwargs={"profileName": slugify(request.user.userprofile)})+"'>"+unicode(request.user.userprofile)+"</a>")
            n.save()
            if ticket.author:
                n.targetUsers.add(ticket.author.user)
            n.targetGroup.add(director)

        elif request.POST.get('new', False) and ticket.status != 0 and f:
            ticket.status = 0
            n = Notification(cssClass='warning', content="<a href='"+reverse('helpdesk:viewticket', kwargs={"token": ticket.token})+"'>Ticket #"+str(ticket.id)+" \""+ticket.title+"\"</a> has been set to \"New\" by <a href='"+reverse('core:playerProfile', kwargs={"profileName": slugify(request.user.userprofile)})+"'>"+unicode(request.user.userprofile)+"</a>")
            n.save()
            if ticket.author:
                n.targetUsers.add(ticket.author.user)
            n.targetGroup.add(director)


        if oldstatus != ticket.get_status_display():
            c = Comment(auto_generated=True)
            c.text = "changed Satus from \""+oldstatus+"\" to \""+ticket.get_status_display()+"\""
            c.author = request.user.userprofile
            c.date = datetime.utcnow()
            c.ticket = ticket
            c.private = False
            c.save()

        ticket.save()

    if not ticket:
        return render(request, 'error.html', {'title': '404 - Not Found', 'description': 'Ticket not found.'})

    comments = Comment.objects.filter(ticket=ticket) if f else Comment.objects.filter(ticket=ticket).filter(private=False)

    c = {"ticket": ticket, "admin": f, "comments": comments}
    return render(request, "ticketdetails.html", c)

def ticketSubmit(request):
    if not isDropbears(request.user):
        return render(request, 'error.html', {'title': '403 - Forbidden', 'description': 'You are not a member.'})
    c = {}
    if request.method == "POST":
        error = False
        new = Ticket()
        anonymous = request.POST.get("anonymous") == "on"
        new.author = None if anonymous else request.user.userprofile 


        new.title = request.POST.get('title', '')
        new.text = request.POST.get('text', '')
        new.category = int(request.POST.get('category', 0))
        sample = string.lowercase+string.digits
        new.token = ''.join(random.sample(sample, 8))
        new.save()
        c["message"] = "Successfully added <a href='"+reverse('helpdesk:viewticket', kwargs={"token": new.token})+"'>Ticket #"+str(new.id)+" \""+new.title+"\"</a>. If you chose to submit anonymously, save this link as it's your only way to access it."

        director = Group.objects.filter(name="Director").first()
        note = Notification(cssClass="info")
        if anonymous:
            note.content="Someone added a new Ticket: <a href='"+reverse('helpdesk:viewticket', kwargs={"token": new.token})+"'>\""+new.title+"\"</a>"
        else:
            note.content="<a href='"+reverse('core:playerProfile', kwargs={"profileName": slugify(request.user.userprofile)})+"'>"+unicode(new.author)+"</a> added a new Ticket: <a href='"+reverse('helpdesk:viewticket', kwargs={"token": new.token})+"'>\""+new.title+"\"</a>"
        note.save()
        note.targetGroup.add(director)

        c["error"] = error

    c["users"] = Group.objects.filter(name="Director").first().user_set.all()

    return render(request, "ticketsubmit.html", c)
