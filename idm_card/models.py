from django.contrib.auth.models import AbstractUser
from django.db import models
import lxml.etree
from django.utils.timezone import now

CARD_STATUS_CHOICES = (
    ('potential', 'Potential'),
    ('printing', 'Sent to print'),
    ('to-collect', 'Pending collection'),
    ('current', 'Current'),
    ('previous', 'Previous'),
)


class Identity(models.Model):
    id = models.UUIDField(primary_key=True, editable=False)


class User(AbstractUser):
    identity = models.ForeignKey(Identity)



class Card(models.Model):
    identity = models.ForeignKey(Identity)
    sequence_number = models.PositiveIntegerField()
    status = models.CharField(max_length=10, choices=CARD_STATUS_CHOICES)
    svg = models.TextField()

    # Migration 0003_card_card_number actually gives this field a default drawn from a sequence.
    card_number = models.IntegerField()

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    expiry = models.DateTimeField(null=True, blank=True)
    max_expiry = models.DateTimeField(null=True, blank=True)
    printed = models.DateTimeField(null=True, blank=True)

    @property
    def svg_with_expiry(self):
        if self.expiry:
            expiry = self.expiry
        else:
            expiry = now()
            expiry = expiry.replace(year=expiry.year + 4)
            if self.max_expiry:
                expiry = min(expiry, self.max_expiry)

        xml = lxml.etree.fromstring(self.svg)
        for elem in xml.xpath("//*[@id='expiry']"):
            elem.text = expiry.strftime('%d %b %Y')

        return lxml.etree.tostring(xml)

    class Meta:
        unique_together = (('identity', 'sequence_number'),)
        index_together = (('identity', 'sequence_number'),)
