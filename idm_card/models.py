import re

import copy
import django_fsm

import barcode
from django.contrib.auth.models import AbstractUser
from django.db import models, connection
import lxml.etree
from django.urls import reverse
from django.utils.timezone import now

CARD_STATE_CHOICES = (
    ('potential', 'Potential'),
    ('printing', 'Sent to print'),
    ('to-collect', 'Pending collection'),
    ('current', 'Current'),
    ('previous', 'Previous'),
    ('lost', 'Lost'),
    ('stolen', 'Stolen'),
)

XMLNS = {"namespaces": {
    "svg": "http://www.w3.org/2000/svg",
}}


class Identity(models.Model):
    id = models.UUIDField(primary_key=True, editable=False)


class User(AbstractUser):
    identity = models.ForeignKey(Identity)



class Card(models.Model):
    identity = models.ForeignKey(Identity)
    sequence_number = models.PositiveIntegerField()
    state = django_fsm.FSMField(max_length=10, choices=CARD_STATE_CHOICES, protected=True)
    svg = models.TextField()

    # Migration 0003_card_card_number actually gives this field a default drawn from a sequence.
    card_number = models.IntegerField()

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    expiry = models.DateTimeField(null=True, blank=True)
    max_expiry = models.DateTimeField(null=True, blank=True)
    printed = models.DateTimeField(null=True, blank=True)

    def calculate_expiry(self):
        expiry = now()
        expiry = expiry.replace(year=expiry.year + 4)
        if self.max_expiry:
            expiry = min(expiry, self.max_expiry)
        return expiry


    @property
    def svg_with_expiry(self):
        if self.expiry:
            expiry = self.expiry
        else:
            expiry = self.calculate_expiry()

        xml = lxml.etree.fromstring(self.svg)
        for elem in xml.xpath("//*[@id='expiry']"):
            elem.text = expiry.strftime('%d %b %Y')

        # Add some barcodes
        Code39 = barcode.get_barcode_class('code39')
        for barcode_elem in xml.xpath("//svg:g[@class='barcode']", **XMLNS):
            # to_ascii() looks like 'X XXX   X XXX' etc, which correspond to bar widths
            # By looking for groups of 'X', we can find the positions and widths of bars, which we represent
            # as svg:rect elements of the appropriate size. We also add a transform, so we can create svg:rects
            # in whole numbers and then scale them laterally to fit the original svg:g.
            code39 = Code39(barcode_elem.attrib['data-barcode']).to_ascii()
            bar_width = 1.0 / len(code39)
            barcode_elem.attrib['transform'] = barcode_elem.attrib.get('transform', '') \
                                               + ' scale({:.6f} 1)'.format(bar_width)
            for match in re.finditer('X+', code39):
                lxml.etree.SubElement(barcode_elem, '{http://www.w3.org/2000/svg}rect',
                                      x=str(match.start()), y="0",
                                      width=str(match.end() - match.start()), height="1")


        front, back = xml, copy.deepcopy(xml)
        front.extend(*front.xpath("//svg:page[@id='front']", **XMLNS))
        front.remove(front.xpath("//svg:pageSet", **XMLNS)[0])
        back.extend(*back.xpath("//svg:page[@id='back']", **XMLNS))
        back.remove(back.xpath("//svg:pageSet", **XMLNS)[0])

        # Add the mag stripe
        lxml.etree.SubElement(back, '{http://www.w3.org/2000/svg}rect',
                              x="0", y="4", width="85.60", height="8")
        # And the bit to sign in
        lxml.etree.SubElement(back, '{http://www.w3.org/2000/svg}rect',
                              style="fill: #FFFEEC",
                              x="5", y="17", width="75.60", height="10")

        return {
            'front': lxml.etree.tostring(front),
            'back': lxml.etree.tostring(back),
        }

    def save(self, *args, **kwargs):
        if self.card_number is None:
            with connection.cursor() as c:
                c.execute("SELECT nextval('card_number'::regclass)")
                self.card_number = c.fetchone()[0]
        return super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('card-detail', kwargs={'pk': self.pk})

    class Meta:
        ordering = ('-sequence_number',)
        unique_together = (('identity', 'sequence_number'),)
        index_together = (('identity', 'sequence_number'),)

    # State transitions

    @django_fsm.transition('state', source=['potential'], target='printing')
    def print(self):
        self.expiry = self.calculate_expiry()

    @django_fsm.transition('state', source=['printing', 'to-collect', 'current', 'lost'], target='stolen')
    def stolen(self):
        pass

    @django_fsm.transition('state', source=['printing', 'to-collect', 'current', 'stolen'], target='lost')
    def lost(self):
        pass

    @django_fsm.transition('state', source=['lost', 'stolen'], target='current')
    def found(self):
        pass

