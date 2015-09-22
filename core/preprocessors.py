from django.conf import settings


def template_settings(request):
    return {
        'HIPCHAT_ENABLED': settings.HIPCHAT_ENABLED,
        'REDDIT_ENABLED': settings.REDDIT_ENABLED,
        'CORP_FULLNAME': settings.CORP_FULLNAME,
        'ALTCORP_FULLNAME': settings.ALTCORP_FULLNAME,
        'ALTCORP_SHORTNAME': settings.ALTCORP_SHORTNAME
    }