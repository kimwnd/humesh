# -*- coding: utf-8 -*-

from django.views.generic import TemplateView, View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import HttpResponse
from .models import MeshDataModel

import datetime
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
        return HttpResponse('POST Only')
    try:
        data = request.POST
        event = data['event']
        value = data['data']
        created = data['published_at']
        coreid = data['coreid']
        device_name = data['device_name']

        year = int(created[:4])
        mon = int(created[5:7])
        day = int(created[8:10])
        hour = int(created[11:13])
        min = int(created[14:16])
        sec = int(created[17:19])

        published = datetime.datetime(year,mon,day,hour,min,sec) + datetime.timedelta(hours=18)

        mesh = MeshDataModel(event=event,
                             data = value,
                             created = published,
                             coreid = coreid,
                             device_name = device_name
                             )
        mesh.save()
        #
        # f = open('demo1.txt', 'a')
        # f.write('POST data is added\n\n')
        # f.write(str(data))
        # f.write('published_at : {}'.format(data['published_at']))
        # f.write('published : {}'.format(str(published)))
        # f.close()

    except Exception as e:
        f = open('demo1.txt', 'a')
        f.write('POST Exception\n\n')
        f.close()
    return HttpResponse('SUCCESS')
