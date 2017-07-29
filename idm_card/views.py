from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView


class IndexView(LoginRequiredMixin, TemplateView):
    template_name = 'index.html'


class CardView(LoginRequiredMixin, TemplateView):
    template_name = 'idm_card/card.svg'
    content_type = 'image/svg+xml'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'identity': self.request.user.identity,
        })
        return