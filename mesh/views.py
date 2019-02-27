# -*- coding: utf-8 -*-

from django.views.generic import TemplateView, View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import HttpResponse
# from .models import MeshDataModel

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
        event = data['event']
        value = data['data']
        created = data['published_at']
        coreid = data['coreid']
        device_name = data['device_name']

        # mesh = MeshDataModel(event=event,
        #                      data = value,
        #                      created = created,
        #                      coreid = coreid,
        #                      device_name = device_name
        #                      )
        # mesh.save()

        f = open('demo1.txt', 'a')
        f.write('POST data is added\n\n')
        f.write(str(data))
        f.write('published_at : {}'.format(data['published_at']))
        f.close()

    except Exception as e:
        f = open('demo1.txt', 'a')
        f.write('POST Exception\n\n')
        f.close()
    return HttpResponse('SUCCESS')

# {
#   'event': ['xenon_temp'],
#   'data': ['91'],
#   'published_at': ['2019-02-27T11:46:24.250Z'],
#   'coreid': ['e00fce68d5131176d95998b4'],
#   'device_name': ['xenon1']}