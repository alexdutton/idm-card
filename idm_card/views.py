from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView


class IndexView(TemplateView):
    template_name = 'index.html'


class CardView(TemplateView):
    template_name = 'idm_card/card.svg'
    content_type = 'image/svg+xml'
