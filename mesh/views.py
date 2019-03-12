# -*- coding: utf-8 -*-

from django.views.generic import TemplateView, View, FormView
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import HttpResponse, JsonResponse
from .models import MeshDataModel, WifiDataModel
from .forms import ControlLEDForm

from django.db import connection

import datetime
import logging
import pandas as pd
import requests

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

@csrf_exempt
def wifi_notification(request):

    if request.method != 'POST':
        return HttpResponse('POST Only')
    try:
        data = request.POST
        temp = data['temp']
        created = datetime.datetime.now() + datetime.timedelta(hours=9)

        wifi = WifiDataModel(temp=temp, created = created)
        wifi.save()

    except Exception as e:
        pass
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

        df = df[df['datetime']>'2019-03-04']

        print(df[df['datetime']>'2019-03-04'].head())

        df_argon = df['argon'].resample("120s").max().fillna(0)
        df_argon = df_argon.reset_index()
        df_xenon = df['xenon'].resample("120s").max().fillna(0)
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

class LineChartView(TemplateView):
    template_name = 'line_chart.html'

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

        df = df[df['datetime']>'2019-03-08 10:00']

        print(df[df['datetime']>'2019-03-08 10:00'].head())

        df_argon = df['argon'].resample("30s").max().fillna(0)
        df_argon = df_argon.reset_index()
        df_xenon = df['xenon'].resample("30s").max().fillna(0)
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


class NewLineChartView(TemplateView):
    template_name = 'line_chart_new.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # meshes = MeshDataModel.objects.order_by('created').all()

        with connection.cursor() as cursor:
            cursor.execute("select id, event, data, created from mesh_meshdatamodel where event = 'temp' order by created asc")
            argon_meshes = cursor.fetchall()

        with connection.cursor() as cursor:
            cursor.execute("select id, event, data, created from mesh_meshdatamodel where event = 'xenon_temp' order by created asc")
            xenon_meshes = cursor.fetchall()

        df_argon = pd.DataFrame(argon_meshes)
        df_argon.columns = ['id', 'event', 'data', 'created']
        df_argon['datetime'] = pd.to_datetime(df_argon['created'])
        df_argon=df_argon.set_index(pd.DatetimeIndex(df_argon['datetime']))

        df_xenon = pd.DataFrame(xenon_meshes)
        df_xenon.columns = ['id', 'event', 'data', 'created']
        df_xenon['datetime'] = pd.to_datetime(df_xenon['created'])
        df_xenon=df_xenon.set_index(pd.DatetimeIndex(df_xenon['datetime']))


        df_argon = df_argon[df_argon['datetime']>'2019-03-12 09:00']
        df_xenon = df_xenon[df_xenon['datetime']>'2019-03-12 09:00']

        # print(df_argon[df_argon['datetime']>'2019-03-04 14:10'].head())

        df_argon = df_argon['data'].resample("30s").max().fillna(0)
        df_argon = df_argon.reset_index()
        df_xenon = df_xenon['data'].resample("30s").max().fillna(0)
        df_xenon = df_xenon.reset_index()

        argon_dts= df_argon['datetime'].tolist()
        xenon_dts= df_xenon['datetime'].tolist()

        argon_labels = []
        xenon_labels = []

        for label in argon_dts :
            argon_labels.append(str(label)[:19])

        for label in xenon_dts :
            xenon_labels.append(str(label)[:19])

        # arg_labels = []
        # arg_data = []
        # xen_data = []
        # for mesh in meshes :
        #     arg_labels.append(str(mesh.created)[:16])
        #     arg_data.append(mesh.data)
        #     xen_data.append(mesh.xenon)
        #
        # argon_data = df_argon['argon'].tolist()
        print('----------------------')
        print(df_argon['data'].tolist())
        print(argon_labels)

        context['argon_data'] = df_argon['data'].tolist()
        context['xenon_data'] = df_xenon['data'].tolist()
        context['argon_labels'] = argon_labels
        context['xenon_labels'] = xenon_labels

        return context

class WifiCheckChartView(TemplateView):
    template_name = 'wifi_check_view.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        with connection.cursor() as cursor:
            cursor.execute("select id, temp, created from mesh_wifidatamodel order by created asc")
            wifi_data = cursor.fetchall()

        with connection.cursor() as cursor:
            cursor.execute("select id, event, data, created from mesh_meshdatamodel where event = 'xenon_temp' order by created asc")
            xenon_meshes = cursor.fetchall()

        df_wifi = pd.DataFrame(wifi_data)
        df_wifi.columns = ['id', 'temp', 'created']
        df_wifi['datetime'] = pd.to_datetime(df_wifi['created'])
        df_wifi=df_wifi.set_index(pd.DatetimeIndex(df_wifi['datetime']))

        df_xenon = pd.DataFrame(xenon_meshes)
        df_xenon.columns = ['id', 'event', 'data', 'created']
        df_xenon['datetime'] = pd.to_datetime(df_xenon['created'])
        df_xenon=df_xenon.set_index(pd.DatetimeIndex(df_xenon['datetime']))


        df_wifi = df_wifi[df_wifi['datetime']>'2019-03-11 09:00']
        df_xenon = df_xenon[df_xenon['datetime']>'2019-03-11 09:00']

        # print(df_argon[df_argon['datetime']>'2019-03-04 14:10'].head())

        df_wifi = df_wifi['temp'].resample("30s").max().fillna(0)
        df_wifi = df_wifi.reset_index()
        df_xenon = df_xenon['data'].resample("30s").max().fillna(0)
        df_xenon = df_xenon.reset_index()

        wifi_dts= df_wifi['datetime'].tolist()
        xenon_dts= df_xenon['datetime'].tolist()

        wifi_labels = []
        xenon_labels = []

        for label in wifi_dts :
            wifi_labels.append(str(label)[:19])

        for label in xenon_dts :
            xenon_labels.append(str(label)[:19])

        # arg_labels = []
        # arg_data = []
        # xen_data = []
        # for mesh in meshes :
        #     arg_labels.append(str(mesh.created)[:16])
        #     arg_data.append(mesh.data)
        #     xen_data.append(mesh.xenon)
        #
        # argon_data = df_argon['argon'].tolist()
        print('----------------------')
        print(df_wifi['temp'].tolist())
        print(wifi_labels)

        context['wifi_data'] = df_wifi['temp'].tolist()
        context['xenon_data'] = df_xenon['data'].tolist()
        context['wifi_labels'] = wifi_labels
        context['xenon_labels'] = xenon_labels

        return context

class MultiChartView(TemplateView):
    template_name = 'multi_chart.html'

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

        df = df[df['datetime']>'2019-03-08 10:00']

        print(df[df['datetime']>'2019-03-08 10:00'].head())

        df_argon = df['argon'].resample("30s").max().fillna(0)
        df_argon = df_argon.reset_index()
        df_xenon = df['xenon'].resample("30s").max().fillna(0)
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

class GetLineDataView(View):

    def get(self, request, *args, **kwargs):
        if request.is_ajax():

            meshes = MeshDataModel.objects.order_by('-created').all()
            meshes = meshes[:5]

            with connection.cursor() as cursor:
                cursor.execute("select id, event, data, created from mesh_meshdatamodel order by created desc limit 5")
                meshdata = cursor.fetchall()

            df = pd.DataFrame(meshdata)
            df.columns = ['id', 'event', 'data', 'created']
            df['datetime'] = pd.to_datetime(df['created'])
            df = df.set_index(pd.DatetimeIndex(df['datetime']))

            mesh_argon = []
            mesh_xenon = []
            for mesh in meshes:
                if mesh.event == 'temp':
                    mesh.argon = mesh.data
                    mesh.xenon = 0
                else:
                    mesh.argon = 0
                    mesh.xenon = mesh.data

                mesh_argon.append(mesh.argon)
                mesh_xenon.append(mesh.xenon)

            df["argon"] = mesh_argon
            df["xenon"] = mesh_xenon

            df = df[df['datetime'] > '2019-03-08 10:00']

            # print(df[df['datetime'] > '2019-03-04'].head())

            df_argon = df['argon'].resample("30s").max().fillna(0)
            df_argon = df_argon.reset_index()
            df_xenon = df['xenon'].resample("30s").max().fillna(0)
            df_xenon = df_xenon.reset_index()

            df_dts = df_argon['datetime'].tolist()

            datetime = []

            for dt in df_dts:
                datetime.append(str(dt)[:19])

            arg_labels = []
            arg_data = []
            xen_data = []
            for mesh in meshes:
                arg_labels.append(str(mesh.created)[:16])
                arg_data.append(mesh.data)
                xen_data.append(mesh.xenon)

            argon_data = df_argon['argon'].tolist()

            dataset1 = df_argon['argon'].tolist()
            dataset2 = df_xenon['xenon'].tolist()
            data_labels = datetime

            print(data_labels[-1])
            print(dataset1[-1])

            data = {'datetime': data_labels[-1], "data1": dataset1[-1], "data2": dataset2[-1] }

            return JsonResponse(data)


class GetMeshDataView(View):

    def get(self, request, *args, **kwargs):
        if request.is_ajax():
            with connection.cursor() as cursor:
                cursor.execute(
                    "select id, event, data, created from mesh_meshdatamodel where event = 'temp' order by created desc limit 5")
                argon_meshes = cursor.fetchall()

            with connection.cursor() as cursor:
                cursor.execute(
                    "select id, event, data, created from mesh_meshdatamodel where event = 'xenon_temp' order by created desc limit 5")
                xenon_meshes = cursor.fetchall()

            df_argon = pd.DataFrame(argon_meshes)
            df_argon.columns = ['id', 'event', 'data', 'created']
            df_argon['datetime'] = pd.to_datetime(df_argon['created'])
            df_argon = df_argon.set_index(pd.DatetimeIndex(df_argon['datetime']))

            df_xenon = pd.DataFrame(xenon_meshes)
            df_xenon.columns = ['id', 'event', 'data', 'created']
            df_xenon['datetime'] = pd.to_datetime(df_xenon['created'])
            df_xenon = df_xenon.set_index(pd.DatetimeIndex(df_xenon['datetime']))

            df_argon = df_argon[df_argon['datetime'] > '2019-03-12 09:00']
            df_xenon = df_xenon[df_xenon['datetime'] > '2019-03-12 09:00']

            df_argon = df_argon['data'].resample("30s").max().fillna(0)
            df_argon = df_argon.reset_index()
            df_xenon = df_xenon['data'].resample("30s").max().fillna(0)
            df_xenon = df_xenon.reset_index()

            argon_dts = df_argon['datetime'].tolist()
            xenon_dts = df_xenon['datetime'].tolist()

            data = {'argon_label': str(argon_dts[-1])[:19], 'xenon_label': str(xenon_dts[-1])[:19], 'argon_data': df_argon['data'].tolist()[-1], 'xenon_data': df_xenon['data'].tolist()[-1]}

            print(data)

            return JsonResponse(data)


class GetWifiDataUpdateView(View):

    def get(self, request, *args, **kwargs):
        if request.is_ajax():
            with connection.cursor() as cursor:
                cursor.execute(
                    "select id, temp, created from mesh_wifidatamodel order by created desc limit 5")
                wifi_meshes = cursor.fetchall()

            with connection.cursor() as cursor:
                cursor.execute(
                    "select id, event, data, created from mesh_meshdatamodel where event = 'xenon_temp' order by created desc limit 5")
                xenon_meshes = cursor.fetchall()

            df_wifi = pd.DataFrame(wifi_meshes)
            df_wifi.columns = ['id', 'temp', 'created']
            df_wifi['datetime'] = pd.to_datetime(df_wifi['created'])
            df_wifi = df_wifi.set_index(pd.DatetimeIndex(df_wifi['datetime']))

            df_xenon = pd.DataFrame(xenon_meshes)
            df_xenon.columns = ['id', 'event', 'data', 'created']
            df_xenon['datetime'] = pd.to_datetime(df_xenon['created'])
            df_xenon = df_xenon.set_index(pd.DatetimeIndex(df_xenon['datetime']))

            df_wifi = df_wifi[df_wifi['datetime'] > '2019-03-12 09:00']
            df_xenon = df_xenon[df_xenon['datetime'] > '2019-03-12 09:00']

            df_wifi = df_wifi['temp'].resample("30s").max().fillna(0)
            df_wifi = df_wifi.reset_index()
            df_xenon = df_xenon['data'].resample("30s").max().fillna(0)
            df_xenon = df_xenon.reset_index()

            wifi_dts = df_wifi['datetime'].tolist()
            xenon_dts = df_xenon['datetime'].tolist()

            data = {'wifi_label': str(wifi_dts[-1]), 'xenon_label': str(xenon_dts[-1]), 'wifi_data': df_wifi['temp'].tolist()[-1], 'xenon_data': df_xenon['data'].tolist()[-1]}

            return JsonResponse(data)


class ControlLEDView(FormView):
    template_name = 'control_led.html'
    form_class = ControlLEDForm
    success_url = 'control/led/'


class ControlSwitchView(View):

    def get(self, request, *args, **kwargs):
        return HttpResponse('POST Only')

    def post(self, request, *args, **kwargs):
        if request.is_ajax():
            state = request.POST.get('state', 'off')
            req = requests.post("https://api.particle.io/v1/devices/e00fce68d5131176d95998b4/led?access_token=1845bd04a1bbc86c7cb18984337243f78a5cc265", data={'command': state})
            data = {'state': state}

            return JsonResponse(data)
