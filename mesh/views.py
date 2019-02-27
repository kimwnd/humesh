# -*- coding: utf-8 -*-

from django.views.generic import TemplateView, View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import HttpResponse

import logging
logger = logging.getLogger(__name__)

class HomePageView(TemplateView):
    template_name = 'home.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        logger.error("home image is loaded")
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        logger.error("home image is loaded")
        return context

class ReceiveMeshDataView(View):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(ReceiveMeshDataView, self).dispatch(request, *args, **kwargs)

    def get(selfself, request):
        logger.debug("POST Only")
        logger.info("POST Only")
        f = open('demo1.txt', 'a')
        f.write('GET data is added\n\n')
        f.close()
        return HttpResponse('POST Only')

    def post(self, request):
        data = request.POST
        f = open('demo1.txt', 'a')
        f.write('POST data is added\n\n')
        f.write(str(data))
        f.close()

        return HttpResponse('SUCCESS')


@csrf_exempt
def mesh_notification(request):

    if request.method != 'POST':
        f = open('demo1.txt', 'a')
        f.write('POST ONLY\n\n')
        f.close()
        return HttpResponse('c')
    try:
        data = request.POST
        f = open('demo1.txt', 'a')
        f.write('POST data is added\n\n')
        f.write(str(data))
        f.write('data : {}'.format(data['data']))
        f.close()

    except Exception as e:
        f = open('demo1.txt', 'a')
        f.write('POST Exception\n\n')
        f.close()
    return HttpResponse('SUCCESS')

# {'event': ['temp'], 'data': ['77'], 'published_at': ['2019-02-27T11:14:20.263Z'], 'coreid': ['e00fce680760748ba970571d']}
