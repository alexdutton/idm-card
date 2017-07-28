from django.db import models

CARD_STATUS_CHOICES = (
    ('potential', 'Potential'),
    ('printing', 'Sent to print'),
    ('to-collect', 'Pending collection'),
    ('current', 'Current')


)

class Identity(models.Model):
    id = models.UUIDField(primary_key=True, editable=False)


class Card(models.Model):
    identity = models.ForeignKey(Identity)
    sequence_number = models.PositiveIntegerField()
    svg = models.TextField()

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)



    class Meta:
        unique_together = (('identity', 'sequence_number'),)
        index_together = (('identity', 'sequence_number'),)
