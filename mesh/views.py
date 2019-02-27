# -*- coding: utf-8 -*-

from django.views.generic import TemplateView
import logging
logger = logging.getLogger(__name__)

class HomePageView(TemplateView):
    template_name = 'home.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        logger.debug('home image isloaded')
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class ReceiveMeshData(TemplateView):
    template_name = 'receive.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
