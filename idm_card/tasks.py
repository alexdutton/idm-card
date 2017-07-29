import celery
from django.db import transaction
from django.template import Engine, Context

from idm_card import models, util


@celery.shared_task(ignore_result=True)
@transaction.atomic
def process_person_update(body, delivery_info, **kwargs):
    identity_id = body['id']
    identity = models.Identity.objects.get_or_create(id=identity_id)

    engine = Engine.get_default()
    template = engine.get_template('idm_card/card.svg')

    current_card = models.Card.objects \
        .filter(identity_id=identity_id).order_by('-sequence_number').select_for_update().first()
    if not current_card:
        current_card = models.Card.objects.create(identity_id, sequence_number=1)

    previous_svg = current_card.svg

    if current_card.status != 'potential':
        current_card = models.Card(identity_id=identity_id,
                                   status='potential',
                                   sequence_number=current_card.sequence_number+1,
                                   card_number=current_card.card_number)

    context = util.get_card_context(body, card_number = current_card.card_number)
    current_card.svg = template.render(context)

    if current_card.svg == previous_svg and (not current_card.expiry or context['max_expiry'] >= current_card.expiry):
        return

    current_card.max_expiry = context['max_expiry']
    current_card.save()