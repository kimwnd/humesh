# -*- coding: utf-8 -*-

from django.views.generic import TemplateView, View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import HttpResponse
from .models import MeshDataModel
from django.db import connection

import datetime
import logging
import pandas as pd

logger = logging.getLogger(__name__)

class HomePageView(TemplateView):
    template_name = 'index.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        logger.debug("home image is loaded")
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        logger.debug("home image is loaded")
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
        logger.debug("data: {}".format(data))
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


class ChartView(TemplateView):
    template_name = 'chart.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        meshes = MeshDataModel.objects.order_by('created').all()

        with connection.cursor() as cursor:
            cursor.execute("select id, event, data, created from mesh_meshdatamodel order by created asc")
            meshdata = cursor.fetchall()

        df = pd.DataFrame(meshdata)
        df.columns = ['id', 'event', 'data', 'created']
        df['datetime'] = pd.to_datetime(df['created'])
        df=df.set_index(pd.DatetimeIndex(df['datetime']))

        mesh_argon = []
        mesh_xenon = []
        for mesh in meshes :
            if mesh.event == 'temp':
                mesh.argon = mesh.data
                mesh.xenon = 0
            else:
                mesh.argon = 0
                mesh.xenon = mesh.data

            mesh_argon.append(mesh.argon)
            mesh_xenon.append(mesh.xenon)

        df["argon"] =  mesh_argon
        df["xenon"] =  mesh_xenon

        df_argon = df['argon'].resample("300s").max().fillna(0)
        df_argon = df_argon.reset_index()
        df_xenon = df['xenon'].resample("300s").max().fillna(0)
        df_xenon = df_xenon.reset_index()

        df_dts= df_argon['datetime'].tolist()

        datetime = []

        for dt in df_dts :
            datetime.append(str(dt)[:19])

        arg_labels = []
        arg_data = []
        xen_data = []
        for mesh in meshes :
            arg_labels.append(str(mesh.created)[:16])
            arg_data.append(mesh.data)
            xen_data.append(mesh.xenon)

        argon_data = df_argon['argon'].tolist()

        context['dataset1'] = df_argon['argon'].tolist()
        context['dataset2'] = df_xenon['xenon'].tolist()
        context['data_labels'] = datetime

        return context

