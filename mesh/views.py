# -*- coding: utf-8 -*-

from django.views.generic import TemplateView, View, FormView
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import HttpResponse, JsonResponse
from .models import MeshDataModel, WifiDataModel, MultipleMeshDataMdodel
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

    except Exception as e:
        f = open('demo1.txt', 'a')
        f.write('POST Exception\n\n')
        f.close()
    return HttpResponse('SUCCESS')

@csrf_exempt
def multiple_notification(request):
    if request.method != 'POST':
        return HttpResponse('POST Only')
    try:
        data = request.POST
        logger.debug("data: {}".format(data))
        # f = open('demo1.txt', 'a')
        # f.write('POST data is added\n\n')
        # f.write(str(data))
        # f.write('published_at : {}'.format(data['published_at']))
        # f.close()
        device_name = data['device_name']
        event_name = data['event']
        events = event_name.split('_')
        doc_name = events[0]
        ship_name = events[1]
        set_no = events[2]
        node_role = events[3]
        location = events[4]
        node_no = events[5]
        values = data['data'].split('|')

        if device_name == 'xenon1' :
            co = int(float(values[0])) - 1700
            h2s = int(float(values[1])) - 2650
        elif device_name == 'xenon2' :
            co = int(float(values[0])) - 1450
            h2s = int(float(values[1])) - 2020
        elif device_name == 'xenon3' :
            co = int(float(values[0])) - 1600
            h2s = int(float(values[1])) - 2600

        # h2s = int(float(values[1]))
        o2 = int(float(values[2]))
        ch4 = int(float(values[3]))
        volt = round(float(values[4]),2)
        created = data['published_at']
        coreid = data['coreid']


        year = int(created[:4])
        mon = int(created[5:7])
        day = int(created[8:10])
        hour = int(created[11:13])
        min = int(created[14:16])
        sec = int(created[17:19])

        published = datetime.datetime(year, mon, day, hour, min, sec) + datetime.timedelta(hours=18)

        multi_mesh = MultipleMeshDataMdodel(event=event_name,
                                            device_name=device_name,
                                            data_co=co,
                                            data_h2s=h2s,
                                            data_o2=o2,
                                            data_ch4=ch4,
                                            doc_name=doc_name,
                                            ship_name=ship_name,
                                            set_no=set_no,
                                            node_role=node_role,
                                            location=location,
                                            node_no=node_no,
                                            created=published,
                                            coreid=coreid,
                                            volt=volt)
        multi_mesh.save()

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


        df_argon = df_argon[df_argon['datetime']>'2019-03-26 13:50']
        df_xenon = df_xenon[df_xenon['datetime']>'2019-03-10 09:00']

        # print(df_argon[df_argon['datetime']>'2019-03-04 14:10'].head())

        df_argon = df_argon['data'].resample("12s").max().fillna(0)
        df_argon = df_argon.reset_index()
        df_xenon = df_xenon['data'].resample("12s").max().fillna(0)
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

        df = df[df['datetime']>'2019-03-26 10:00']

        print(df[df['datetime']>'2019-03-26 10:00'].head())

        df_argon = df['argon'].resample("20s").max().fillna(0)
        df_argon = df_argon.reset_index()
        df_xenon = df['xenon'].resample("20s").max().fillna(0)
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

            df = df[df['datetime'] > '2019-03-26 10:00']

            # print(df[df['datetime'] > '2019-03-04'].head())

            df_argon = df['argon'].resample("20s").max().fillna(0)
            df_argon = df_argon.reset_index()
            df_xenon = df['xenon'].resample("20s").max().fillna(0)
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

            df_argon = df_argon[df_argon['datetime'] > '2019-03-26 13:50']
            df_xenon = df_xenon[df_xenon['datetime'] > '2019-03-10 09:00']

            df_argon = df_argon['data'].resample("12s").max().fillna(0)
            df_argon = df_argon.reset_index()
            df_xenon = df_xenon['data'].resample("12s").max().fillna(0)
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

            df_wifi = df_wifi[df_wifi['datetime'] > '2019-03-26 09:00']
            df_xenon = df_xenon[df_xenon['datetime'] > '2019-03-26 09:00']

            df_wifi = df_wifi['temp'].resample("20s").max().fillna(0)
            df_wifi = df_wifi.reset_index()
            df_xenon = df_xenon['data'].resample("20s").max().fillna(0)
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


class MultipleLineChartView(TemplateView):
    template_name = 'multiple_line_chart.html'


class MultipleDashboardView(TemplateView):
    template_name = 'multiple_dash_board.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        with connection.cursor() as cursor:
            cursor.execute("select id, event, data_co, data_h2s, data_o2, data_ch4, created from multiple_mesh_data where device_name = 'xenon1' order by created asc")
            xenon1_meshes = cursor.fetchall()

        with connection.cursor() as cursor:
            cursor.execute("select id, event, data_co, data_h2s, data_o2, data_ch4, created from multiple_mesh_data where device_name = 'xenon2' order by created asc")
            xenon2_meshes = cursor.fetchall()

        with connection.cursor() as cursor:
            cursor.execute("select id, event, data_co, data_h2s, data_o2, data_ch4, created from multiple_mesh_data where device_name = 'xenon3' order by created asc")
            xenon3_meshes = cursor.fetchall()

        with connection.cursor() as cursor:
            cursor.execute("select id, event, data_co, data_h2s, data_o2, data_ch4, created from multiple_mesh_data where device_name = 'xenon3' order by created asc")
            xenon4_meshes = cursor.fetchall()

        df_xenon1 = pd.DataFrame(xenon1_meshes)
        df_xenon1.columns = ['id', 'event', 'data_co', 'data_h2s', 'data_o2', 'data_ch4', 'created']
        df_xenon1['datetime'] = pd.to_datetime(df_xenon1['created'])
        df_xenon1=df_xenon1.set_index(pd.DatetimeIndex(df_xenon1['datetime']))

        df_xenon2 = pd.DataFrame(xenon2_meshes)
        df_xenon2.columns = ['id', 'event', 'data_co', 'data_h2s', 'data_o2', 'data_ch4', 'created']
        df_xenon2['datetime'] = pd.to_datetime(df_xenon2['created'])
        df_xenon2=df_xenon2.set_index(pd.DatetimeIndex(df_xenon2['datetime']))

        df_xenon3 = pd.DataFrame(xenon3_meshes)
        df_xenon3.columns = ['id', 'event', 'data_co', 'data_h2s', 'data_o2', 'data_ch4', 'created']
        df_xenon3['datetime'] = pd.to_datetime(df_xenon3['created'])
        df_xenon3=df_xenon3.set_index(pd.DatetimeIndex(df_xenon3['datetime']))

        df_xenon4 = pd.DataFrame(xenon4_meshes)
        df_xenon4.columns = ['id', 'event', 'data_co', 'data_h2s', 'data_o2', 'data_ch4', 'created']
        df_xenon4['datetime'] = pd.to_datetime(df_xenon4['created'])
        df_xenon4=df_xenon4.set_index(pd.DatetimeIndex(df_xenon4['datetime']))

        df_xenon1 = df_xenon1[df_xenon1['datetime']>'2019-04-15 22:30']
        df_xenon2 = df_xenon2[df_xenon2['datetime']>'2019-04-15 22:30']
        df_xenon3 = df_xenon3[df_xenon3['datetime']>'2019-04-15 22:30']
        df_xenon4 = df_xenon4[df_xenon4['datetime']>'2019-04-15 22:30']

        # For Xenon1
        df_xenon1_co = df_xenon1['data_co'].resample("15s").max().fillna(0)
        df_xenon1_h2s = df_xenon1['data_h2s'].resample("15s").max().fillna(0)
        df_xenon1_o2 = df_xenon1['data_o2'].resample("15s").max().fillna(0)
        df_xenon1_ch4 = df_xenon1['data_ch4'].resample("15s").max().fillna(0)
        df_xenon1_co = df_xenon1_co.reset_index()
        df_xenon1_h2s = df_xenon1_h2s.reset_index()
        df_xenon1_o2 = df_xenon1_o2.reset_index()
        df_xenon1_ch4 = df_xenon1_ch4.reset_index()

        # For Xenon2
        df_xenon2_co = df_xenon2['data_co'].resample("15s").max().fillna(0)
        df_xenon2_h2s = df_xenon2['data_h2s'].resample("15s").max().fillna(0)
        df_xenon2_o2 = df_xenon2['data_o2'].resample("15s").max().fillna(0)
        df_xenon2_ch4 = df_xenon2['data_ch4'].resample("15s").max().fillna(0)
        df_xenon2_co = df_xenon2_co.reset_index()
        df_xenon2_h2s = df_xenon2_h2s.reset_index()
        df_xenon2_o2 = df_xenon2_o2.reset_index()
        df_xenon2_ch4 = df_xenon2_ch4.reset_index()

        # For Xenon3
        df_xenon3_co = df_xenon3['data_co'].resample("15s").max().fillna(0)
        df_xenon3_h2s = df_xenon3['data_h2s'].resample("15s").max().fillna(0)
        df_xenon3_o2 = df_xenon3['data_o2'].resample("15s").max().fillna(0)
        df_xenon3_ch4 = df_xenon3['data_ch4'].resample("15s").max().fillna(0)
        df_xenon3_co = df_xenon3_co.reset_index()
        df_xenon3_h2s = df_xenon3_h2s.reset_index()
        df_xenon3_o2 = df_xenon3_o2.reset_index()
        df_xenon3_ch4 = df_xenon3_ch4.reset_index()

        # For Xenon4
        df_xenon4_co = df_xenon4['data_co'].resample("15s").max().fillna(0)
        df_xenon4_h2s = df_xenon4['data_h2s'].resample("15s").max().fillna(0)
        df_xenon4_o2 = df_xenon4['data_o2'].resample("15s").max().fillna(0)
        df_xenon4_ch4 = df_xenon4['data_ch4'].resample("15s").max().fillna(0)
        df_xenon4_co = df_xenon4_co.reset_index()
        df_xenon4_h2s = df_xenon4_h2s.reset_index()
        df_xenon4_o2 = df_xenon4_o2.reset_index()
        df_xenon4_ch4 = df_xenon4_ch4.reset_index()

        # print(df_xenon2_co)

        xenon1_dts= df_xenon1_co['datetime'].tolist()
        xenon2_dts= df_xenon2_co['datetime'].tolist()
        xenon3_dts= df_xenon3_co['datetime'].tolist()
        xenon4_dts= df_xenon4_co['datetime'].tolist()

        xenon1_labels = []
        xenon2_labels = []
        xenon3_labels = []
        xenon4_labels = []

        for label in xenon1_dts :
            xenon1_labels.append(str(label)[:19])

        for label in xenon2_dts :
            xenon2_labels.append(str(label)[:19])

        for label in xenon3_dts :
            xenon3_labels.append(str(label)[:19])

        for label in xenon4_dts :
            xenon4_labels.append(str(label)[:19])

        # print(xenon2_labels)
        # arg_labels = []
        # arg_data = []
        # xen_data = []
        # for mesh in meshes :
        #     arg_labels.append(str(mesh.created)[:16])
        #     arg_data.append(mesh.data)
        #     xen_data.append(mesh.xenon)
        #
        # argon_data = df_argon['argon'].tolist()
        # print('----------------------')
        # print(df_xenon2_co['data_co'].tolist())
        # print(xenon2_labels)

        context['xenon1_data_co'] = df_xenon1_co['data_co'].tolist()
        context['xenon1_data_h2s'] = df_xenon1_h2s['data_h2s'].tolist()
        context['xenon1_data_o2'] = df_xenon1_o2['data_o2'].tolist()
        context['xenon1_data_ch4'] = df_xenon1_ch4['data_ch4'].tolist()
        context['xenon1_labels'] = xenon1_labels

        context['xenon2_data_co'] = df_xenon2_co['data_co'].tolist()
        context['xenon2_data_h2s'] = df_xenon2_h2s['data_h2s'].tolist()
        context['xenon2_data_o2'] = df_xenon2_o2['data_o2'].tolist()
        context['xenon2_data_ch4'] = df_xenon2_ch4['data_ch4'].tolist()
        context['xenon2_labels'] = xenon2_labels

        context['xenon3_data_co'] = df_xenon3_co['data_co'].tolist()
        context['xenon3_data_h2s'] = df_xenon3_h2s['data_h2s'].tolist()
        context['xenon3_data_o2'] = df_xenon3_o2['data_o2'].tolist()
        context['xenon3_data_ch4'] = df_xenon3_ch4['data_ch4'].tolist()
        context['xenon3_labels'] = xenon3_labels

        context['xenon4_data_co'] = df_xenon4_co['data_co'].tolist()
        context['xenon4_data_h2s'] = df_xenon4_h2s['data_h2s'].tolist()
        context['xenon4_data_o2'] = df_xenon4_o2['data_o2'].tolist()
        context['xenon4_data_ch4'] = df_xenon4_ch4['data_ch4'].tolist()
        context['xenon4_labels'] = xenon4_labels

        return context


class DashboardNumbersView(TemplateView):
    template_name = 'dashboard_numbers.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        with connection.cursor() as cursor:
            cursor.execute("select id, event, data_co, data_h2s, data_o2, data_ch4, created from multiple_mesh_data where device_name = 'xenon1' order by created asc")
            xenon1_meshes = cursor.fetchall()

        with connection.cursor() as cursor:
            cursor.execute("select id, event, data_co, data_h2s, data_o2, data_ch4, created from multiple_mesh_data where device_name = 'xenon2' order by created asc")
            xenon2_meshes = cursor.fetchall()

        with connection.cursor() as cursor:
            cursor.execute("select id, event, data_co, data_h2s, data_o2, data_ch4, created from multiple_mesh_data where device_name = 'xenon3' order by created asc")
            xenon3_meshes = cursor.fetchall()

        with connection.cursor() as cursor:
            cursor.execute("select id, event, data_co, data_h2s, data_o2, data_ch4, created from multiple_mesh_data where device_name = 'xenon3' order by created asc")
            xenon4_meshes = cursor.fetchall()

        df_xenon1 = pd.DataFrame(xenon1_meshes)
        df_xenon1.columns = ['id', 'event', 'data_co', 'data_h2s', 'data_o2', 'data_ch4', 'created']
        df_xenon1['datetime'] = pd.to_datetime(df_xenon1['created'])
        df_xenon1=df_xenon1.set_index(pd.DatetimeIndex(df_xenon1['datetime']))

        df_xenon2 = pd.DataFrame(xenon2_meshes)
        df_xenon2.columns = ['id', 'event', 'data_co', 'data_h2s', 'data_o2', 'data_ch4', 'created']
        df_xenon2['datetime'] = pd.to_datetime(df_xenon2['created'])
        df_xenon2=df_xenon2.set_index(pd.DatetimeIndex(df_xenon2['datetime']))

        df_xenon3 = pd.DataFrame(xenon3_meshes)
        df_xenon3.columns = ['id', 'event', 'data_co', 'data_h2s', 'data_o2', 'data_ch4', 'created']
        df_xenon3['datetime'] = pd.to_datetime(df_xenon3['created'])
        df_xenon3=df_xenon3.set_index(pd.DatetimeIndex(df_xenon3['datetime']))

        df_xenon4 = pd.DataFrame(xenon4_meshes)
        df_xenon4.columns = ['id', 'event', 'data_co', 'data_h2s', 'data_o2', 'data_ch4', 'created']
        df_xenon4['datetime'] = pd.to_datetime(df_xenon4['created'])
        df_xenon4=df_xenon4.set_index(pd.DatetimeIndex(df_xenon4['datetime']))

        df_xenon1 = df_xenon1[df_xenon1['datetime']>'2019-04-15 22:30']
        df_xenon2 = df_xenon2[df_xenon2['datetime']>'2019-04-15 22:30']
        df_xenon3 = df_xenon3[df_xenon3['datetime']>'2019-04-15 22:30']
        df_xenon4 = df_xenon4[df_xenon4['datetime']>'2019-04-15 22:30']

        # For Xenon1
        df_xenon1_co = df_xenon1['data_co'].resample("15s").max().fillna(0)
        df_xenon1_h2s = df_xenon1['data_h2s'].resample("15s").max().fillna(0)
        df_xenon1_o2 = df_xenon1['data_o2'].resample("15s").max().fillna(0)
        df_xenon1_ch4 = df_xenon1['data_ch4'].resample("15s").max().fillna(0)
        df_xenon1_co = df_xenon1_co.reset_index()
        df_xenon1_h2s = df_xenon1_h2s.reset_index()
        df_xenon1_o2 = df_xenon1_o2.reset_index()
        df_xenon1_ch4 = df_xenon1_ch4.reset_index()

        # For Xenon2
        df_xenon2_co = df_xenon2['data_co'].resample("15s").max().fillna(0)
        df_xenon2_h2s = df_xenon2['data_h2s'].resample("15s").max().fillna(0)
        df_xenon2_o2 = df_xenon2['data_o2'].resample("15s").max().fillna(0)
        df_xenon2_ch4 = df_xenon2['data_ch4'].resample("15s").max().fillna(0)
        df_xenon2_co = df_xenon2_co.reset_index()
        df_xenon2_h2s = df_xenon2_h2s.reset_index()
        df_xenon2_o2 = df_xenon2_o2.reset_index()
        df_xenon2_ch4 = df_xenon2_ch4.reset_index()

        # For Xenon3
        df_xenon3_co = df_xenon3['data_co'].resample("15s").max().fillna(0)
        df_xenon3_h2s = df_xenon3['data_h2s'].resample("15s").max().fillna(0)
        df_xenon3_o2 = df_xenon3['data_o2'].resample("15s").max().fillna(0)
        df_xenon3_ch4 = df_xenon3['data_ch4'].resample("15s").max().fillna(0)
        df_xenon3_co = df_xenon3_co.reset_index()
        df_xenon3_h2s = df_xenon3_h2s.reset_index()
        df_xenon3_o2 = df_xenon3_o2.reset_index()
        df_xenon3_ch4 = df_xenon3_ch4.reset_index()

        # For Xenon4
        df_xenon4_co = df_xenon4['data_co'].resample("15s").max().fillna(0)
        df_xenon4_h2s = df_xenon4['data_h2s'].resample("15s").max().fillna(0)
        df_xenon4_o2 = df_xenon4['data_o2'].resample("15s").max().fillna(0)
        df_xenon4_ch4 = df_xenon4['data_ch4'].resample("15s").max().fillna(0)
        df_xenon4_co = df_xenon4_co.reset_index()
        df_xenon4_h2s = df_xenon4_h2s.reset_index()
        df_xenon4_o2 = df_xenon4_o2.reset_index()
        df_xenon4_ch4 = df_xenon4_ch4.reset_index()

        # print(df_xenon2_co)

        # xenon1_dts= df_xenon1_co['datetime'].tolist()
        # xenon2_dts= df_xenon2_co['datetime'].tolist()
        # xenon3_dts= df_xenon3_co['datetime'].tolist()
        # xenon4_dts= df_xenon4_co['datetime'].tolist()
        #
        # xenon1_labels = []
        # xenon2_labels = []
        # xenon3_labels = []
        # xenon4_labels = []
        #
        # for label in xenon1_dts :
        #     xenon1_labels.append(str(label)[:19])
        #
        # for label in xenon2_dts :
        #     xenon2_labels.append(str(label)[:19])
        #
        # for label in xenon3_dts :
        #     xenon3_labels.append(str(label)[:19])
        #
        # for label in xenon4_dts :
        #     xenon4_labels.append(str(label)[:19])

        # print(xenon2_labels)
        # arg_labels = []
        # arg_data = []
        # xen_data = []
        # for mesh in meshes :
        #     arg_labels.append(str(mesh.created)[:16])
        #     arg_data.append(mesh.data)
        #     xen_data.append(mesh.xenon)
        #
        # argon_data = df_argon['argon'].tolist()
        # print('----------------------')
        # print(df_xenon2_co['data_co'].tolist())
        # print(xenon2_labels)

        context['xenon1_data_co'] = df_xenon1_co['data_co'].tolist()[-1]
        context['xenon1_data_h2s'] = df_xenon1_h2s['data_h2s'].tolist()[-1]
        context['xenon1_data_o2'] = df_xenon1_o2['data_o2'].tolist()[-1]
        context['xenon1_data_ch4'] = df_xenon1_ch4['data_ch4'].tolist()[-1]
        # context['xenon1_labels'] = xenon1_labels

        context['xenon2_data_co'] = df_xenon2_co['data_co'].tolist()[-1]
        context['xenon2_data_h2s'] = df_xenon2_h2s['data_h2s'].tolist()[-1]
        context['xenon2_data_o2'] = df_xenon2_o2['data_o2'].tolist()[-1]
        context['xenon2_data_ch4'] = df_xenon2_ch4['data_ch4'].tolist()[-1]
        # context['xenon2_labels'] = xenon2_labels

        context['xenon3_data_co'] = df_xenon3_co['data_co'].tolist()[-1]
        context['xenon3_data_h2s'] = df_xenon3_h2s['data_h2s'].tolist()[-1]
        context['xenon3_data_o2'] = df_xenon3_o2['data_o2'].tolist()[-1]
        context['xenon3_data_ch4'] = df_xenon3_ch4['data_ch4'].tolist()[-1]
        # context['xenon3_labels'] = xenon3_labels

        context['xenon4_data_co'] = df_xenon4_co['data_co'].tolist()[-1]
        context['xenon4_data_h2s'] = df_xenon4_h2s['data_h2s'].tolist()[-1]
        context['xenon4_data_o2'] = df_xenon4_o2['data_o2'].tolist()[-1]
        context['xenon4_data_ch4'] = df_xenon4_ch4['data_ch4'].tolist()[-1]
        # context['xenon4_labels'] = xenon4_labels

        print(context)

        return context


class DashboardUpdateView(View):

    def get(self, request, *args, **kwargs):
        if request.is_ajax():
            with connection.cursor() as cursor:
                cursor.execute(
                    "select id, event, data_co, data_h2s, data_o2, data_ch4, created from multiple_mesh_data where device_name = 'xenon1' order by created asc")
                xenon1_meshes = cursor.fetchall()

            with connection.cursor() as cursor:
                cursor.execute(
                    "select id, event, data_co, data_h2s, data_o2, data_ch4, created from multiple_mesh_data where device_name = 'xenon2' order by created asc")
                xenon2_meshes = cursor.fetchall()

            with connection.cursor() as cursor:
                cursor.execute(
                    "select id, event, data_co, data_h2s, data_o2, data_ch4, created from multiple_mesh_data where device_name = 'xenon3' order by created asc")
                xenon3_meshes = cursor.fetchall()

            with connection.cursor() as cursor:
                cursor.execute(
                    "select id, event, data_co, data_h2s, data_o2, data_ch4, created from multiple_mesh_data where device_name = 'xenon3' order by created asc")
                xenon4_meshes = cursor.fetchall()

            df_xenon1 = pd.DataFrame(xenon1_meshes)
            df_xenon1.columns = ['id', 'event', 'data_co', 'data_h2s', 'data_o2', 'data_ch4', 'created']
            df_xenon1['datetime'] = pd.to_datetime(df_xenon1['created'])
            df_xenon1 = df_xenon1.set_index(pd.DatetimeIndex(df_xenon1['datetime']))

            df_xenon2 = pd.DataFrame(xenon2_meshes)
            df_xenon2.columns = ['id', 'event', 'data_co', 'data_h2s', 'data_o2', 'data_ch4', 'created']
            df_xenon2['datetime'] = pd.to_datetime(df_xenon2['created'])
            df_xenon2 = df_xenon2.set_index(pd.DatetimeIndex(df_xenon2['datetime']))

            df_xenon3 = pd.DataFrame(xenon3_meshes)
            df_xenon3.columns = ['id', 'event', 'data_co', 'data_h2s', 'data_o2', 'data_ch4', 'created']
            df_xenon3['datetime'] = pd.to_datetime(df_xenon3['created'])
            df_xenon3 = df_xenon3.set_index(pd.DatetimeIndex(df_xenon3['datetime']))

            df_xenon4 = pd.DataFrame(xenon4_meshes)
            df_xenon4.columns = ['id', 'event', 'data_co', 'data_h2s', 'data_o2', 'data_ch4', 'created']
            df_xenon4['datetime'] = pd.to_datetime(df_xenon4['created'])
            df_xenon4 = df_xenon4.set_index(pd.DatetimeIndex(df_xenon4['datetime']))

            df_xenon1 = df_xenon1[df_xenon1['datetime'] > '2019-04-15 12:30']
            df_xenon2 = df_xenon2[df_xenon2['datetime'] > '2019-04-15 12:30']
            df_xenon3 = df_xenon3[df_xenon3['datetime'] > '2019-04-15 12:30']
            df_xenon4 = df_xenon4[df_xenon4['datetime'] > '2019-04-15 12:30']

            # For Xenon1
            df_xenon1_co = df_xenon1['data_co'].resample("15s").max().fillna(0)
            df_xenon1_h2s = df_xenon1['data_h2s'].resample("15s").max().fillna(0)
            df_xenon1_o2 = df_xenon1['data_o2'].resample("15s").max().fillna(0)
            df_xenon1_ch4 = df_xenon1['data_ch4'].resample("15s").max().fillna(0)
            df_xenon1_co = df_xenon1_co.reset_index()
            df_xenon1_h2s = df_xenon1_h2s.reset_index()
            df_xenon1_o2 = df_xenon1_o2.reset_index()
            df_xenon1_ch4 = df_xenon1_ch4.reset_index()

            # For Xenon2
            df_xenon2_co = df_xenon2['data_co'].resample("15s").max().fillna(0)
            df_xenon2_h2s = df_xenon2['data_h2s'].resample("15s").max().fillna(0)
            df_xenon2_o2 = df_xenon2['data_o2'].resample("15s").max().fillna(0)
            df_xenon2_ch4 = df_xenon2['data_ch4'].resample("15s").max().fillna(0)
            df_xenon2_co = df_xenon2_co.reset_index()
            df_xenon2_h2s = df_xenon2_h2s.reset_index()
            df_xenon2_o2 = df_xenon2_o2.reset_index()
            df_xenon2_ch4 = df_xenon2_ch4.reset_index()

            # For Xenon3
            df_xenon3_co = df_xenon3['data_co'].resample("15s").max().fillna(0)
            df_xenon3_h2s = df_xenon3['data_h2s'].resample("15s").max().fillna(0)
            df_xenon3_o2 = df_xenon3['data_o2'].resample("15s").max().fillna(0)
            df_xenon3_ch4 = df_xenon3['data_ch4'].resample("15s").max().fillna(0)
            df_xenon3_co = df_xenon3_co.reset_index()
            df_xenon3_h2s = df_xenon3_h2s.reset_index()
            df_xenon3_o2 = df_xenon3_o2.reset_index()
            df_xenon3_ch4 = df_xenon3_ch4.reset_index()

            # For Xenon4
            df_xenon4_co = df_xenon4['data_co'].resample("15s").max().fillna(0)
            df_xenon4_h2s = df_xenon4['data_h2s'].resample("15s").max().fillna(0)
            df_xenon4_o2 = df_xenon4['data_o2'].resample("15s").max().fillna(0)
            df_xenon4_ch4 = df_xenon4['data_ch4'].resample("15s").max().fillna(0)
            df_xenon4_co = df_xenon4_co.reset_index()
            df_xenon4_h2s = df_xenon4_h2s.reset_index()
            df_xenon4_o2 = df_xenon4_o2.reset_index()
            df_xenon4_ch4 = df_xenon4_ch4.reset_index()

            xenon1_dts = df_xenon1_co['datetime'].tolist()
            xenon2_dts = df_xenon2_co['datetime'].tolist()
            xenon3_dts = df_xenon3_co['datetime'].tolist()
            xenon4_dts = df_xenon4_co['datetime'].tolist()

            data = {'xenon1_label': str(xenon1_dts[-1])[:19],
                    'xenon1_data_co': df_xenon1_co['data_co'].tolist()[-1], 'xenon1_data_h2s': df_xenon1_h2s['data_h2s'].tolist()[-1],
                    'xenon1_data_o2': df_xenon1_o2['data_o2'].tolist()[-1], 'xenon1_data_ch4': df_xenon1_ch4['data_ch4'].tolist()[-1],
                    'xenon2_label': str(xenon2_dts[-1])[:19],
                    'xenon2_data_co': df_xenon2_co['data_co'].tolist()[-1], 'xenon2_data_h2s': df_xenon2_h2s['data_h2s'].tolist()[-1],
                    'xenon2_data_o2': df_xenon2_o2['data_o2'].tolist()[-1], 'xenon2_data_ch4': df_xenon2_ch4['data_ch4'].tolist()[-1],
                    'xenon3_label': str(xenon3_dts[-1])[:19],
                    'xenon3_data_co': df_xenon3_co['data_co'].tolist()[-1], 'xenon3_data_h2s': df_xenon3_h2s['data_h2s'].tolist()[-1],
                    'xenon3_data_o2': df_xenon3_o2['data_o2'].tolist()[-1], 'xenon3_data_ch4': df_xenon3_ch4['data_ch4'].tolist()[-1],
                    'xenon4_label': str(xenon4_dts[-1])[:19],
                    'xenon4_data_co': df_xenon4_co['data_co'].tolist()[-1], 'xenon4_data_h2s': df_xenon4_h2s['data_h2s'].tolist()[-1],
                    'xenon4_data_o2': df_xenon4_o2['data_o2'].tolist()[-1], 'xenon4_data_ch4': df_xenon4_ch4['data_ch4'].tolist()[-1],
                    }

            return JsonResponse(data)


class DashboardNumnersUpdateView(View):

    def get(self, request, *args, **kwargs):
        if request.is_ajax():
            with connection.cursor() as cursor:
                cursor.execute(
                    "select id, event, data_co, data_h2s, data_o2, data_ch4, created from multiple_mesh_data where device_name = 'xenon1' order by created asc")
                xenon1_meshes = cursor.fetchall()

            with connection.cursor() as cursor:
                cursor.execute(
                    "select id, event, data_co, data_h2s, data_o2, data_ch4, created from multiple_mesh_data where device_name = 'xenon2' order by created asc")
                xenon2_meshes = cursor.fetchall()

            with connection.cursor() as cursor:
                cursor.execute(
                    "select id, event, data_co, data_h2s, data_o2, data_ch4, created from multiple_mesh_data where device_name = 'xenon3' order by created asc")
                xenon3_meshes = cursor.fetchall()

            with connection.cursor() as cursor:
                cursor.execute(
                    "select id, event, data_co, data_h2s, data_o2, data_ch4, created from multiple_mesh_data where device_name = 'xenon3' order by created asc")
                xenon4_meshes = cursor.fetchall()

            df_xenon1 = pd.DataFrame(xenon1_meshes)
            df_xenon1.columns = ['id', 'event', 'data_co', 'data_h2s', 'data_o2', 'data_ch4', 'created']
            df_xenon1['datetime'] = pd.to_datetime(df_xenon1['created'])
            df_xenon1 = df_xenon1.set_index(pd.DatetimeIndex(df_xenon1['datetime']))

            df_xenon2 = pd.DataFrame(xenon2_meshes)
            df_xenon2.columns = ['id', 'event', 'data_co', 'data_h2s', 'data_o2', 'data_ch4', 'created']
            df_xenon2['datetime'] = pd.to_datetime(df_xenon2['created'])
            df_xenon2 = df_xenon2.set_index(pd.DatetimeIndex(df_xenon2['datetime']))

            df_xenon3 = pd.DataFrame(xenon3_meshes)
            df_xenon3.columns = ['id', 'event', 'data_co', 'data_h2s', 'data_o2', 'data_ch4', 'created']
            df_xenon3['datetime'] = pd.to_datetime(df_xenon3['created'])
            df_xenon3 = df_xenon3.set_index(pd.DatetimeIndex(df_xenon3['datetime']))

            df_xenon4 = pd.DataFrame(xenon4_meshes)
            df_xenon4.columns = ['id', 'event', 'data_co', 'data_h2s', 'data_o2', 'data_ch4', 'created']
            df_xenon4['datetime'] = pd.to_datetime(df_xenon4['created'])
            df_xenon4 = df_xenon4.set_index(pd.DatetimeIndex(df_xenon4['datetime']))

            df_xenon1 = df_xenon1[df_xenon1['datetime'] > '2019-04-15 20:30']
            df_xenon2 = df_xenon2[df_xenon2['datetime'] > '2019-04-15 20:30']
            df_xenon3 = df_xenon3[df_xenon3['datetime'] > '2019-04-15 20:30']
            df_xenon4 = df_xenon4[df_xenon4['datetime'] > '2019-04-15 20:30']

            # For Xenon1
            df_xenon1_co = df_xenon1['data_co'].resample("15s").max().fillna(0)
            df_xenon1_h2s = df_xenon1['data_h2s'].resample("15s").max().fillna(0)
            df_xenon1_o2 = df_xenon1['data_o2'].resample("15s").max().fillna(0)
            df_xenon1_ch4 = df_xenon1['data_ch4'].resample("15s").max().fillna(0)
            df_xenon1_co = df_xenon1_co.reset_index()
            df_xenon1_h2s = df_xenon1_h2s.reset_index()
            df_xenon1_o2 = df_xenon1_o2.reset_index()
            df_xenon1_ch4 = df_xenon1_ch4.reset_index()

            # For Xenon2
            df_xenon2_co = df_xenon2['data_co'].resample("15s").max().fillna(0)
            df_xenon2_h2s = df_xenon2['data_h2s'].resample("15s").max().fillna(0)
            df_xenon2_o2 = df_xenon2['data_o2'].resample("15s").max().fillna(0)
            df_xenon2_ch4 = df_xenon2['data_ch4'].resample("15s").max().fillna(0)
            df_xenon2_co = df_xenon2_co.reset_index()
            df_xenon2_h2s = df_xenon2_h2s.reset_index()
            df_xenon2_o2 = df_xenon2_o2.reset_index()
            df_xenon2_ch4 = df_xenon2_ch4.reset_index()

            # For Xenon3
            df_xenon3_co = df_xenon3['data_co'].resample("15s").max().fillna(0)
            df_xenon3_h2s = df_xenon3['data_h2s'].resample("15s").max().fillna(0)
            df_xenon3_o2 = df_xenon3['data_o2'].resample("15s").max().fillna(0)
            df_xenon3_ch4 = df_xenon3['data_ch4'].resample("15s").max().fillna(0)
            df_xenon3_co = df_xenon3_co.reset_index()
            df_xenon3_h2s = df_xenon3_h2s.reset_index()
            df_xenon3_o2 = df_xenon3_o2.reset_index()
            df_xenon3_ch4 = df_xenon3_ch4.reset_index()

            # For Xenon4
            df_xenon4_co = df_xenon4['data_co'].resample("15s").max().fillna(0)
            df_xenon4_h2s = df_xenon4['data_h2s'].resample("15s").max().fillna(0)
            df_xenon4_o2 = df_xenon4['data_o2'].resample("15s").max().fillna(0)
            df_xenon4_ch4 = df_xenon4['data_ch4'].resample("15s").max().fillna(0)
            df_xenon4_co = df_xenon4_co.reset_index()
            df_xenon4_h2s = df_xenon4_h2s.reset_index()
            df_xenon4_o2 = df_xenon4_o2.reset_index()
            df_xenon4_ch4 = df_xenon4_ch4.reset_index()

            # print(df_xenon2_co)

            xenon1_dts = df_xenon1_co['datetime'].tolist()
            xenon2_dts = df_xenon2_co['datetime'].tolist()
            xenon3_dts = df_xenon3_co['datetime'].tolist()
            xenon4_dts = df_xenon4_co['datetime'].tolist()

            data = {'xenon1_label': str(xenon1_dts[-1])[:19],
                    'xenon1_data_co': df_xenon1_co['data_co'].tolist()[-1], 'xenon1_data_h2s': df_xenon1_h2s['data_h2s'].tolist()[-1],
                    'xenon1_data_o2': df_xenon1_o2['data_o2'].tolist()[-1], 'xenon1_data_ch4': df_xenon1_ch4['data_ch4'].tolist()[-1],
                    'xenon2_label': str(xenon2_dts[-1])[:19],
                    'xenon2_data_co': df_xenon2_co['data_co'].tolist()[-1], 'xenon2_data_h2s': df_xenon2_h2s['data_h2s'].tolist()[-1],
                    'xenon2_data_o2': df_xenon2_o2['data_o2'].tolist()[-1], 'xenon2_data_ch4': df_xenon2_ch4['data_ch4'].tolist()[-1],
                    'xenon3_label': str(xenon3_dts[-1])[:19],
                    'xenon3_data_co': df_xenon3_co['data_co'].tolist()[-1], 'xenon3_data_h2s': df_xenon3_h2s['data_h2s'].tolist()[-1],
                    'xenon3_data_o2': df_xenon3_o2['data_o2'].tolist()[-1], 'xenon3_data_ch4': df_xenon3_ch4['data_ch4'].tolist()[-1],
                    'xenon4_label': str(xenon4_dts[-1])[:19],
                    'xenon4_data_co': df_xenon4_co['data_co'].tolist()[-1], 'xenon4_data_h2s': df_xenon4_h2s['data_h2s'].tolist()[-1],
                    'xenon4_data_o2': df_xenon4_o2['data_o2'].tolist()[-1], 'xenon4_data_ch4': df_xenon4_ch4['data_ch4'].tolist()[-1],
                    }

            # print(data)

            return JsonResponse(data)

