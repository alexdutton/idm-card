from django.core.exceptions import PermissionDenied

from idm_card.models import Identity


def process_userinfo(user, claims):
    try:
        identity = Identity.objects.get(id=claims['identity_id'])
    except Identity.DoesNotExist:
        raise PermissionDenied

    user.identity_id = identity.id
    user.save()