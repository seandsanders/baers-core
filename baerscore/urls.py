from django.conf.urls import include, url
from django.contrib import admin


urlpatterns = [
    # Examples:
    # url(r'^$', 'baerscore.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^applications/', include('applications.urls', namespace='applications')),
    url(r'^srp/', include('srp.urls', namespace='srp')),
    url(r'^reddit/$', include('subreddit.urls', namespace='subreddit')),
    url(r'^timerboard/', include('timerboard.urls', namespace='timerboard')),
    url(r'^', include('core.urls', namespace='core')),

    
]
