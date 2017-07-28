from idm_card.models import Identity


def process_userinfo(user, claims):
    identity = Identity.objects.get(id=claims['identity_id'])
    user.identity_id = identity.id
    user.identity_content_type_id = identity.content_type_id
    user.save()