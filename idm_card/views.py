from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views.generic import TemplateView, ListView, DetailView

from . import models


class IndexView(LoginRequiredMixin, TemplateView):
    template_name = 'index.html'


class CardDetailView(LoginRequiredMixin, DetailView):
    model = models.Card

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.method != 'GET':
            queryset = queryset.select_for_update()
        return queryset

    def post(self, request, pk):
        self.object = self.get_object()
        if 'print' in request.POST:
            self.object.print()
        elif 'lost' in request.POST:
            self.object.lost()
        elif 'collected' in request.POST:
            self.object.collected()
        elif 'stolen' in request.POST:
            self.object.stolen()
        elif 'found' in request.POST:
            self.object.found()
        self.object.save()
        return redirect(request.POST.get('next', request.build_absolute_uri()))

class CardView(LoginRequiredMixin, TemplateView):
    template_name = 'idm_card/card.svg'
    content_type = 'image/svg+xml'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'identity': self.request.user.identity,
        })
        return
