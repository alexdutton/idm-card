from django.conf import settings


def idm_card(request):
    return {
        'IDM_CORE_URL': settings.IDM_CORE_URL,
        'IDM_AUTH_URL': settings.IDM_AUTH_URL,
    }
