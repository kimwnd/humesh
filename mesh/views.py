# -*- coding: utf-8 -*-

from django.views.generic import TemplateView, View, FormView
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import HttpResponse, JsonResponse
from .models import ( MeshDataModel, WifiDataModel, MultipleMeshDataMdodel, CloudMeshDataMdodel, CatM1SensorDataMdodel,
                      CatM1LocationMdodel )
from .forms import ControlLEDForm

from django.db import connection
from django.utils import timezone

import datetime
import pytz
import logging
import pandas as pd
import requests
import ast

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
def cloud_notification(request):
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
        values = data['data']

        flag = values[0]
        o2 = int(values[1:5],16)/10.0
        co = int(values[5:9],16)
        if co < 3 :
            co = 0
        ch4 = int(values[9:11],16)
        temp = int(values[11:15],16)/10.0
        humid = int(values[15:17],16)
        volt = int(values[17:21],16)/100.0
        created = data['published_at']
        coreid = data['coreid']

        year = int(created[:4])
        mon = int(created[5:7])
        day = int(created[8:10])
        hour = int(created[11:13])
        min = int(created[14:16])
        sec = int(created[17:19])

        published = datetime.datetime(year, mon, day, hour, min, sec) + datetime.timedelta(hours=18)

        cloud_mesh = CloudMeshDataMdodel(event=event_name,
                                            device_name=device_name,
                                            data_co=co,
                                            data_o2=o2,
                                            data_ch4=ch4,
                                            data_humid=humid,
                                            data_temp=temp,
                                            doc_name=doc_name,
                                            ship_name=ship_name,
                                            set_no=set_no,
                                            node_role=node_role,
                                            location=location,
                                            node_no=node_no,
                                            created=published,
                                            coreid=coreid,
                                            volt=volt)
        cloud_mesh.save()

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
def test_notification(request):
    if request.method != 'POST':
        return HttpResponse('POST Only')
    try:
        data = request.POST
        logger.debug("data: {}".format(data))
        f = open('demo1.txt', 'a')
        f.write('POST data is new added\n\n')
        f.write("{}".format(request.body))
        f.write("----\n\n")
        received = (request.body).decode('ascii')
        received = ast.literal_eval(received)
        if received.get('dock_name', None) and received.get('data_type', None) :
            dock_name = received['dock_name']
            device_name = received['device_name']
            data_type = received['data_type']
            timestamp = received['timestamp']
            published = datetime.datetime.fromtimestamp(timestamp)
            # mytimezone = pytz.timezone("Asia/Seoul")
            # published = timezone.localtime(fromtimetamp)

            shipname = 'Ship1'

            if data_type == 'data' :
                values      = received['value']
                data_co     = values['co']
                data_o2     = values['o2']/10.0
                data_ch4    = values['ch4']
                data_temp   = values['temp']
                data_humid  = values['humid']
                volt        = values['volt']/10.0

                catm1_data = CatM1SensorDataMdodel( device_name = device_name,
                                                    data_co = data_co,
                                                    data_o2 = data_o2,
                                                    data_ch4 = data_ch4,
                                                    data_temp = data_temp,
                                                    data_humid = data_humid,
                                                    volt= volt,
                                                    dock_name = dock_name,
                                                    shipname = shipname,
                                                    created = published )

                catm1_data.save()

            if data_type == 'location' :
                locations = received['gps']
                lat_temp = float(locations['latitude'])
                lat_do = int(lat_temp/100)
                latitude = lat_do * 1.0 + (lat_temp - lat_do * 100)/60.0

                long_temp = float(locations['longitude'])
                long_do = int(long_temp/100)
                longitude = long_do * 1.0 + (long_temp - long_do * 100)/60.0

                # f.write("--latitude org--\n\n")
                # f.write("{}".format(lat_temp))
                # f.write("----\n\n")
                # f.write("{}".format(latitude))
                #
                # f.write("--longitude org--\n\n")
                # f.write("{}".format(long_temp))
                # f.write("----\n\n")
                # f.write("{}".format(longitude))

                device_location = CatM1LocationMdodel(device_name = device_name,
                                                      latitude = latitude,
                                                      longitude = longitude,
                                                      created=published )

                device_location.save()

        # f.write(str(received['data']['GpsInfo']))
        # f.write("----\n\n")
        # f.write(str(type(data)))
        # f.write("----\n\n")
        # f.write('published_at : {}'.format(data['published_at']))
        # f.close()

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

        # if device_name == 'xenon1' :
        #     co = int(float(values[0])) - 1650
        #     h2s = int(float(values[1])) - 2550
        # elif device_name == 'xenon2' :
        #     co = int(float(values[0])) - 1400
        #     h2s = int(float(values[1])) - 1850
        # elif device_name == 'xenon3' :
        #     co = int(float(values[0])) - 1750
        #     h2s = int(float(values[1])) - 2560
        if device_name == 'xenon2' :
            co = 0
        else:
            co = int(float(values[0]))

        h2s = int(float(values[1]))
        o2 = int(float(values[2]))
        ch4 = int(float(values[3]))
        volt = round(float(values[4]),2)
        created = data['published_at']
        coreid = data['coreid']

        # co_m_inv = 4762.0
        # vref = volt/3.3*0.5*4096.0
        # co_ppm = co_m_inv*(co-vref - 550.0)
        # co_ppm = int(co_ppm)
        # if device_name == 'xenon1' :
        #     if co < 1900.0 :
        #         co = 1900.0
        #
        #     co_voff = 1900.0 * 0.0011224
        #     co_v_diff = 3.3 - co_voff
        #     co_ppm = 1000.0 / co_v_diff*(co*0.0011224 - co_voff)
        # else:
        #     co_ppm = 0.0

        h2s = 0

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


class CloudDashboardView(TemplateView):
    # template_name = 'cloud_dash_board.html'
    template_name = 'layouts-preloader.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        with connection.cursor() as cursor:
            cursor.execute("select id, event, data_co, data_o2, data_ch4, data_temp, data_humid, volt, created from cloud_mesh_data where device_name = 'xenon1' order by created asc")
            sensor1_meshes = cursor.fetchall()

        with connection.cursor() as cursor:
            cursor.execute("select id, event, data_co, data_o2, data_ch4, data_temp, data_humid, volt, created from cloud_mesh_data where device_name = 'xenon2' order by created asc")
            sensor2_meshes = cursor.fetchall()

        with connection.cursor() as cursor:
            cursor.execute(
                "select id, event, data_co, data_o2, data_ch4, data_temp, data_humid, volt, created from cloud_mesh_data where device_name = 'xenon3' order by created asc")
            sensor3_meshes = cursor.fetchall()

        # with connection.cursor() as cursor:
        #     cursor.execute("select id, event, data_co, data_h2s, data_o2, data_ch4, created, volt from multiple_mesh_data where device_name = 'xenon2' order by created asc")
        #     xenon4_meshes = cursor.fetchall()

        df_sensor1              = pd.DataFrame(sensor1_meshes)
        df_sensor1.columns      = ['id', 'event', 'data_co', 'data_o2', 'data_ch4', 'data_temp', 'data_humid', 'volt', 'created']
        df_sensor1['datetime']  = pd.to_datetime(df_sensor1['created'])
        df_sensor1              = df_sensor1.set_index(pd.DatetimeIndex(df_sensor1['datetime']))

        df_sensor2              = pd.DataFrame(sensor2_meshes)
        df_sensor2.columns      = ['id', 'event', 'data_co', 'data_o2', 'data_ch4', 'data_temp', 'data_humid', 'volt', 'created']
        df_sensor2['datetime']  = pd.to_datetime(df_sensor2['created'])
        df_sensor2              = df_sensor2.set_index(pd.DatetimeIndex(df_sensor2['datetime']))

        df_sensor3              = pd.DataFrame(sensor3_meshes)
        df_sensor3.columns      = ['id', 'event', 'data_co', 'data_o2', 'data_ch4', 'data_temp', 'data_humid', 'volt', 'created']
        df_sensor3['datetime']  = pd.to_datetime(df_sensor3['created'])
        df_sensor3              =df_sensor3.set_index(pd.DatetimeIndex(df_sensor3['datetime']))

        # df_sensor4 = pd.DataFrame(sensor4_meshes)
        # df_sensor4.columns = ['id', 'event', 'data_co', 'data_o2', 'data_ch4', 'data_temp', 'data_humid', 'volt', 'created']
        # df_sensor4['datetime'] = pd.to_datetime(df_sensor4['created'])
        # df_sensor4=df_sensor4.set_index(pd.DatetimeIndex(df_sensor4['datetime']))

        df_sensor1 = df_sensor1[df_sensor1['datetime']>'2019-11-01 10:00']
        df_sensor2 = df_sensor2[df_sensor2['datetime']>'2019-11-01 10:00']
        df_sensor3 = df_sensor3[df_sensor3['datetime']>'2019-11-01 10:00']
        # df_sensor4 = df_sensor4[df_sensor4['datetime']>'2019-04-25 15:00']

        # df_sensor1 = df_sensor1[df_sensor1['datetime']<'2019-10-15 15:50']
        # df_sensor2 = df_sensor2[df_sensor2['datetime']<'2019-10-15 15:50']
        # df_sensor3 = df_sensor3[df_sensor3['datetime']<'2019-10-15 15:50']

        # For Sensor1
        df_sensor1_co       = df_sensor1['data_co'].resample("600s").median().fillna(0)
        df_sensor1_o2       = df_sensor1['data_o2'].resample("600s").median().fillna(0)
        df_sensor1_ch4      = df_sensor1['data_ch4'].resample("600s").median().fillna(0)
        df_sensor1_temp     = df_sensor1['data_temp'].resample("600s").median().fillna(0)
        df_sensor1_humid    = df_sensor1['data_humid'].resample("600s").median().fillna(0)
        df_sensor1_volt     = df_sensor1['volt'].resample("600s").median().fillna(0)

        df_sensor1_co   = df_sensor1_co.reset_index()
        df_sensor1_o2   = df_sensor1_o2.reset_index()
        df_sensor1_ch4  = df_sensor1_ch4.reset_index()
        df_sensor1_volt = df_sensor1_volt.reset_index()
        df_sensor1_temp = df_sensor1_temp.reset_index()
        df_sensor1_humid = df_sensor1_humid.reset_index()

        # For Sensor2
        df_sensor2_co       = df_sensor2['data_co'].resample("600s").median().fillna(0)
        df_sensor2_o2       = df_sensor2['data_o2'].resample("600s").median().fillna(0)
        df_sensor2_ch4      = df_sensor2['data_ch4'].resample("600s").median().fillna(0)
        df_sensor2_temp     = df_sensor2['data_temp'].resample("600s").median().fillna(0)
        df_sensor2_humid    = df_sensor2['data_humid'].resample("600s").median().fillna(0)
        df_sensor2_volt     = df_sensor2['volt'].resample("600s").median().fillna(0)

        df_sensor2_co   = df_sensor2_co.reset_index()
        df_sensor2_o2   = df_sensor2_o2.reset_index()
        df_sensor2_ch4  = df_sensor2_ch4.reset_index()
        df_sensor2_volt = df_sensor2_volt.reset_index()
        df_sensor2_temp = df_sensor2_temp.reset_index()
        df_sensor2_humid = df_sensor2_humid.reset_index()

        # For Sensor3
        df_sensor3_co       = df_sensor3['data_co'].resample("600s").median().fillna(0)
        df_sensor3_o2       = df_sensor3['data_o2'].resample("600s").median().fillna(0)
        df_sensor3_ch4      = df_sensor3['data_ch4'].resample("600s").median().fillna(0)
        df_sensor3_temp     = df_sensor3['data_temp'].resample("600s").median().fillna(0)
        df_sensor3_humid    = df_sensor3['data_humid'].resample("600s").median().fillna(0)
        df_sensor3_volt     = df_sensor3['volt'].resample("600s").median().fillna(0)

        df_sensor3_co       = df_sensor3_co.reset_index()
        df_sensor3_o2       = df_sensor3_o2.reset_index()
        df_sensor3_ch4      = df_sensor3_ch4.reset_index()
        df_sensor3_volt     = df_sensor3_volt.reset_index()
        df_sensor3_temp     = df_sensor3_temp.reset_index()
        df_sensor3_humid    = df_sensor3_humid.reset_index()

        # # For Sensor4
        # df_sensor4_co       = df_sensor4['data_co'].resample("10s").max().fillna(0)
        # df_sensor4_o2       = df_sensor4['data_o2'].resample("10s").max().fillna(0)
        # df_sensor4_ch4      = df_sensor4['data_ch4'].resample("10s").max().fillna(0)
        # df_sensor4_temp     = df_sensor4['data_temp'].resample("10s").max().fillna(0)
        # df_sensor4_humid    = df_sensor4['data_humid'].resample("10s").max().fillna(0)
        # df_sensor4_volt     = df_sensor4['data_volt'].resample("10s").max().fillna(0)
        #
        # df_sensor4_co   = df_sensor4_co.reset_index()
        # df_sensor4_o2   = df_sensor4_o2.reset_index()
        # df_sensor4_ch4  = df_sensor4_ch4.reset_index()
        # df_sensor4_volt = df_sensor4_volt.reset_index()

        # print('df_sensor2_o2')
        # print('len of df_sensor2_co')
        # print(len(df_sensor1_co))

        sensor1_dts = df_sensor1_co['datetime'].tolist()
        sensor2_dts = df_sensor2_co['datetime'].tolist()
        sensor3_dts = df_sensor3_co['datetime'].tolist()
        # sensor4_dts = df_sensor4_co['datetime'].tolist()

        sensor1_labels = []
        sensor2_labels = []
        sensor3_labels = []
        # sensor4_labels = []

        for label in sensor1_dts :
            sensor1_labels.append(str(label)[:19])

        for label in sensor2_dts :
            sensor2_labels.append(str(label)[:19])

        for label in sensor3_dts :
            sensor3_labels.append(str(label)[:19])

        # for label in sensor4_dts :
        #     sensor4_labels.append(str(label)[:19])

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
        # print('len of sensor2_labels')
        # print(len(sensor2_labels))

        # 산소 데이터 리스트

        sensor1_o2_list = []
        sensor2_o2_list = []
        sensor3_o2_list = []
        # sensor4_o2_list = []

        sensor1_len_o2 = len(df_sensor1_o2)
        sensor2_len_o2 = len(df_sensor2_o2)
        sensor3_len_o2 = len(df_sensor3_o2)
        # sensor4_len_o2 = len(df_sensor4['data_o2'])

        for i in range(sensor1_len_o2) :
            sensor1_o2_list.append(df_sensor1_o2['data_o2'][i])

        for i in range(sensor2_len_o2) :
            sensor2_o2_list.append(df_sensor2_o2['data_o2'][i])

        for i in range(sensor3_len_o2):
            sensor3_o2_list.append(df_sensor3_o2['data_o2'][i])

        # for i in range(sensor3_len_o2):
        #     sensor3_o2_list.append(round(df_sensor4['data_o2'][i], 1))
        # print('sensor2_o2_list')
        # print(sensor2_o2_list)

        # CO 데이터 리스트

        sensor1_co_list = []
        sensor2_co_list = []
        sensor3_co_list = []
        # sensor4_co_list = []

        sensor1_len_co = len(df_sensor1_co)
        sensor2_len_co = len(df_sensor2_co)
        sensor3_len_co = len(df_sensor3_co)
        # sensor4_len_co = len(df_sensor4['data_co'])

        for i in range(sensor1_len_co) :
            sensor1_co_list.append(df_sensor1_co['data_co'][i])

        for i in range(sensor2_len_co) :
            sensor2_co_list.append(df_sensor2_co['data_co'][i])

        for i in range(sensor3_len_co) :
            sensor3_co_list.append(df_sensor3_co['data_co'][i])

        # for i in range(sensor4_len_co) :
        #     sensor4_co_list.append(df_sensor4['data_co'][i])

        # print('sensor2_co_list')
        # print(sensor2_co_list)
        # print(len(sensor2_co_list))

        # CH4 데이터 리스트

        sensor1_ch4_list = []
        sensor2_ch4_list = []
        sensor3_ch4_list = []
        # sensor4_ch4_list = []

        sensor1_len_ch4   = len(df_sensor1_ch4)
        sensor2_len_ch4   = len(df_sensor2_ch4)
        sensor3_len_ch4   = len(df_sensor3_ch4)
        # sensor4_len_ch4 = len(df_sensor4['data_ch4'])

        for i in range(sensor1_len_ch4):
            sensor1_ch4_list.append(df_sensor1_ch4['data_ch4'][i])

        for i in range(sensor2_len_ch4):
            sensor2_ch4_list.append(df_sensor2_ch4['data_ch4'][i])

        for i in range(sensor3_len_ch4):
            sensor3_ch4_list.append(df_sensor3_ch4['data_ch4'][i])

        # Volt 데이터 리스트

        sensor1_volt_list = []
        sensor2_volt_list = []
        sensor3_volt_list = []
        # sensor4_ch4_list = []

        sensor1_len_volt = len(df_sensor1_volt)
        sensor2_len_volt = len(df_sensor2_volt)
        sensor3_len_volt = len(df_sensor3_volt)
        # sensor4_len_ch4 = len(df_sensor4['data_ch4'])

        for i in range(sensor1_len_volt):
            sensor1_volt_list.append(df_sensor1_volt['volt'][i])

        for i in range(sensor2_len_volt):
            sensor2_volt_list.append(df_sensor2_volt['volt'][i])

        for i in range(sensor3_len_volt):
            sensor3_volt_list.append(df_sensor3_volt['volt'][i])

        # 온도 데이터 리스트

        sensor1_temp_list = []
        sensor2_temp_list = []
        sensor3_temp_list = []
        # sensor4_ch4_list = []

        sensor1_len_temp = len(df_sensor1_temp)
        sensor2_len_temp = len(df_sensor2_temp)
        sensor3_len_temp = len(df_sensor3_temp)
        # sensor4_len_ch4 = len(df_sensor4['data_ch4'])

        for i in range(sensor1_len_temp):
            sensor1_temp_list.append(df_sensor1_temp['data_temp'][i])

        for i in range(sensor2_len_temp):
            sensor2_temp_list.append(df_sensor2_temp['data_temp'][i])

        for i in range(sensor3_len_volt):
            sensor3_temp_list.append(df_sensor3_temp['data_temp'][i])

        # 습도 데이터 리스트

        sensor1_humid_list = []
        sensor2_humid_list = []
        sensor3_humid_list = []
        # sensor4_ch4_list = []

        sensor1_len_humid = len(df_sensor1_humid)
        sensor2_len_humid = len(df_sensor2_humid)
        sensor3_len_humid = len(df_sensor3_humid)
        # sensor4_len_ch4 = len(df_sensor4['data_ch4'])

        for i in range(sensor1_len_humid):
            sensor1_humid_list.append(df_sensor1_humid['data_humid'][i])

        for i in range(sensor2_len_humid):
            sensor2_humid_list.append(df_sensor2_humid['data_humid'][i])

        for i in range(sensor3_len_humid):
            sensor3_humid_list.append(df_sensor3_humid['data_humid'][i])

        # print('sensor2_ch4_list')
        # print(sensor2_ch4_list)
        # print(len(sensor2_ch4_list))

        # print(df_sensor2_co['data_co'])
        # print(df_sensor1_co['data_co'].tolist())
        # print(df_xenon1['data_o2'].tolist())
        # print('-------------')
        # print(len(sensor1_co_list))
        # print(len(sensor1_o2_list))
        # print(len(sensor1_ch4_list))
        # print(len(sensor1_labels))

        context['sensor1_data_co']  = sensor1_co_list
        context['sensor1_data_o2']  = sensor1_o2_list
        context['sensor1_data_ch4'] = sensor1_ch4_list
        context['sensor1_volt']     = sensor1_volt_list
        context['sensor1_temp']     = sensor1_temp_list
        context['sensor1_labels']   = sensor1_labels
        context['sensor1_co_val']   = int(sensor1_co_list[-1])
        context['sensor1_o2_val']   = round(sensor1_o2_list[-1],1)
        context['sensor1_ch4_val']   = int(sensor1_ch4_list[-1])
        context['sensor1_temp_val']   = round(sensor1_temp_list[-1],1)
        context['sensor1_humid_val']   = int(sensor1_humid_list[-1])
        context['sensor1_power_per']   = int((sensor1_volt_list[-1]-3.3)  / 0.9 * 100.0)
        context['sensor1_datenow']   = sensor1_labels[-1][0:16]

        context['sensor2_data_co']  = sensor2_co_list
        context['sensor2_data_o2']  = sensor2_o2_list
        context['sensor2_data_ch4'] = sensor2_ch4_list
        context['sensor2_volt']     = sensor2_volt_list
        context['sensor2_temp']     = sensor2_temp_list
        context['sensor2_labels']   = sensor2_labels
        context['sensor2_co_val']   = int(sensor2_co_list[-1])
        context['sensor2_o2_val']   = round(sensor2_o2_list[-1],1)
        context['sensor2_ch4_val']   = int(sensor2_ch4_list[-1])
        context['sensor2_temp_val']   = round(sensor2_temp_list[-1],1)
        context['sensor2_humid_val']   = int(sensor2_humid_list[-1])
        context['sensor2_power_per'] = int((sensor2_volt_list[-1]-3.3) / 0.9 * 100.0)
        context['sensor2_datenow'] = sensor2_labels[-1][0:16]

        context['sensor3_data_co']  = sensor3_co_list
        context['sensor3_data_o2']  = sensor3_o2_list
        context['sensor3_data_ch4'] = sensor3_ch4_list
        context['sensor3_volt']     = sensor3_volt_list
        context['sensor3_temp']     = sensor3_temp_list
        context['sensor3_labels']   = sensor3_labels
        context['sensor3_co_val']   = int(sensor3_co_list[-1])
        context['sensor3_o2_val']   = round(sensor3_o2_list[-1],1)
        context['sensor3_ch4_val']   = int(sensor3_ch4_list[-1])
        context['sensor3_temp_val']   = round(sensor3_temp_list[-1])
        context['sensor3_humid_val']   = int(sensor3_humid_list[-1])
        context['sensor3_power_per'] = int((sensor3_volt_list[-1]-3.3) / 0.9 * 100.0)
        context['sensor3_datenow'] = sensor3_labels[-1][0:16]

        return context

class LTEDashboardView(TemplateView):
    # template_name = 'cloud_dash_board.html'
    template_name = 'lte-dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        with connection.cursor() as cursor:
            cursor.execute("select id, data_co, data_o2, data_ch4, data_temp, data_humid, volt, created from catm1_sensor_data where device_name = 'sensor001' and created > '2019-12-10' order by created asc;")
            sensor1_data = cursor.fetchall()

        with connection.cursor() as cursor:
            cursor.execute("select id, data_co, data_o2, data_ch4, data_temp, data_humid, volt, created from catm1_sensor_data where device_name = 'sensor002' and created > '2019-12-10' order by created asc;")
            sensor2_data = cursor.fetchall()

        with connection.cursor() as cursor:
            cursor.execute("select id, latitude, longitude, created from device_location_data where device_name = 'sensor001' order by created desc limit 5")
            sensor1_locs = cursor.fetchone()

        with connection.cursor() as cursor:
            cursor.execute("select id, latitude, longitude, created from device_location_data where device_name = 'sensor002' order by created desc limit 5")
            sensor2_locs = cursor.fetchone()

        locs1 = CatM1LocationMdodel.objects.filter(device_name = 'sensor001').order_by('-created').values('id', 'latitude', 'longitude', 'created')[:5]
        sensor1_locs = [ e for e in locs1 ]

        locs2 = CatM1LocationMdodel.objects.filter(
            device_name='sensor002').order_by('-created').values('id', 'latitude', 'longitude', 'created')[:5]
        sensor2_locs = [e for e in locs2]

        df_sensor1              = pd.DataFrame(sensor1_data)
        df_sensor1.columns      = ['id', 'data_co', 'data_o2', 'data_ch4', 'data_temp', 'data_humid', 'volt', 'created']
        dtime1                  = pd.to_datetime(df_sensor1['created'])
        df_sensor1['datetime']  = dtime1.dt.tz_convert('Asia/Seoul')
        df_sensor1              = df_sensor1.set_index(pd.DatetimeIndex(df_sensor1['datetime']))

        df_sensor2              = pd.DataFrame(sensor2_data)
        df_sensor2.columns      = ['id', 'data_co', 'data_o2', 'data_ch4', 'data_temp', 'data_humid', 'volt', 'created']
        dtime2                  = pd.to_datetime(df_sensor2['created'])
        df_sensor2['datetime']  = dtime2.dt.tz_convert('Asia/Seoul')
        df_sensor2              = df_sensor2.set_index(pd.DatetimeIndex(df_sensor2['datetime']))

        df_sensor1 = df_sensor1[df_sensor1['datetime']>'2019-12-10 01:00']
        df_sensor2 = df_sensor2[df_sensor2['datetime']>'2019-12-10 01:00']

        # For Sensor1
        df_sensor1_co       = df_sensor1['data_co'].resample("20s").median().fillna(0)
        df_sensor1_o2       = df_sensor1['data_o2'].resample("20s").median().fillna(0)
        df_sensor1_ch4      = df_sensor1['data_ch4'].resample("20s").median().fillna(0)
        df_sensor1_temp     = df_sensor1['data_temp'].resample("20s").median().fillna(0)
        df_sensor1_humid    = df_sensor1['data_humid'].resample("20s").median().fillna(0)
        df_sensor1_volt     = df_sensor1['volt'].resample("20s").median().fillna(0)

        df_sensor1_co   = df_sensor1_co.reset_index()
        df_sensor1_o2   = df_sensor1_o2.reset_index()
        df_sensor1_ch4  = df_sensor1_ch4.reset_index()
        df_sensor1_volt = df_sensor1_volt.reset_index()
        df_sensor1_temp = df_sensor1_temp.reset_index()
        df_sensor1_humid = df_sensor1_humid.reset_index()

        # For Sensor2
        df_sensor2_co       = df_sensor2['data_co'].resample("20s").median().fillna(0)
        df_sensor2_o2       = df_sensor2['data_o2'].resample("20s").median().fillna(0)
        df_sensor2_ch4      = df_sensor2['data_ch4'].resample("20s").median().fillna(0)
        df_sensor2_temp     = df_sensor2['data_temp'].resample("20s").median().fillna(0)
        df_sensor2_humid    = df_sensor2['data_humid'].resample("20s").median().fillna(0)
        df_sensor2_volt     = df_sensor2['volt'].resample("20s").median().fillna(0)

        df_sensor2_co   = df_sensor2_co.reset_index()
        df_sensor2_o2   = df_sensor2_o2.reset_index()
        df_sensor2_ch4  = df_sensor2_ch4.reset_index()
        df_sensor2_volt = df_sensor2_volt.reset_index()
        df_sensor2_temp = df_sensor2_temp.reset_index()
        df_sensor2_humid = df_sensor2_humid.reset_index()

        sensor1_dts = df_sensor1_co['datetime'].tolist()
        sensor2_dts = df_sensor2_co['datetime'].tolist()

        sensor1_labels = []
        sensor2_labels = []

        for label in sensor1_dts :
            sensor1_labels.append(str(label)[:19])

        for label in sensor2_dts :
            sensor2_labels.append(str(label)[:19])

        # 산소 데이터 리스트

        sensor1_o2_list = []
        sensor2_o2_list = []

        sensor1_len_o2 = len(df_sensor1_o2)
        sensor2_len_o2 = len(df_sensor2_o2)

        for i in range(sensor1_len_o2) :
            sensor1_o2_list.append(df_sensor1_o2['data_o2'][i])

        for i in range(sensor2_len_o2) :
            sensor2_o2_list.append(df_sensor2_o2['data_o2'][i])

        # CO 데이터 리스트

        sensor1_co_list = []
        sensor2_co_list = []

        sensor1_len_co = len(df_sensor1_co)
        sensor2_len_co = len(df_sensor2_co)

        for i in range(sensor1_len_co) :
            sensor1_co_list.append(df_sensor1_co['data_co'][i])

        for i in range(sensor2_len_co) :
            sensor2_co_list.append(df_sensor2_co['data_co'][i])

        # CH4 데이터 리스트

        sensor1_ch4_list = []
        sensor2_ch4_list = []

        sensor1_len_ch4   = len(df_sensor1_ch4)
        sensor2_len_ch4   = len(df_sensor2_ch4)

        for i in range(sensor1_len_ch4):
            sensor1_ch4_list.append(df_sensor1_ch4['data_ch4'][i])

        for i in range(sensor2_len_ch4):
            sensor2_ch4_list.append(df_sensor2_ch4['data_ch4'][i])

        # Volt 데이터 리스트

        sensor1_volt_list = []
        sensor2_volt_list = []

        sensor1_len_volt = len(df_sensor1_volt)
        sensor2_len_volt = len(df_sensor2_volt)

        for i in range(sensor1_len_volt):
            sensor1_volt_list.append(df_sensor1_volt['volt'][i])

        for i in range(sensor2_len_volt):
            sensor2_volt_list.append(df_sensor2_volt['volt'][i])

        # 온도 데이터 리스트

        sensor1_temp_list = []
        sensor2_temp_list = []

        sensor1_len_temp = len(df_sensor1_temp)
        sensor2_len_temp = len(df_sensor2_temp)

        for i in range(sensor1_len_temp):
            sensor1_temp_list.append(df_sensor1_temp['data_temp'][i])

        for i in range(sensor2_len_temp):
            sensor2_temp_list.append(df_sensor2_temp['data_temp'][i])

        # 습도 데이터 리스트

        sensor1_humid_list = []
        sensor2_humid_list = []

        sensor1_len_humid = len(df_sensor1_humid)
        sensor2_len_humid = len(df_sensor2_humid)

        for i in range(sensor1_len_humid):
            sensor1_humid_list.append(df_sensor1_humid['data_humid'][i])

        for i in range(sensor2_len_humid):
            sensor2_humid_list.append(df_sensor2_humid['data_humid'][i])

        context['sensor1_data_co']  = sensor1_co_list
        context['sensor1_data_o2']  = sensor1_o2_list
        context['sensor1_data_ch4'] = sensor1_ch4_list
        context['sensor1_volt']     = sensor1_volt_list
        context['sensor1_temp']     = sensor1_temp_list
        context['sensor1_labels']   = sensor1_labels
        context['sensor1_co_val']   = int(sensor1_co_list[-1])
        context['sensor1_o2_val']   = round(sensor1_o2_list[-1],1)
        context['sensor1_ch4_val']   = int(sensor1_ch4_list[-1])
        context['sensor1_temp_val']   = round(sensor1_temp_list[-1],1)
        context['sensor1_humid_val']   = int(sensor1_humid_list[-1])
        context['sensor1_power_per']   = int((sensor1_volt_list[-1]-3.3)  / 0.9 * 100.0)
        context['sensor1_datenow']   = sensor1_labels[-1][0:16]

        context['sensor2_data_co']  = sensor2_co_list
        context['sensor2_data_o2']  = sensor2_o2_list
        context['sensor2_data_ch4'] = sensor2_ch4_list
        context['sensor2_volt']     = sensor2_volt_list
        context['sensor2_temp']     = sensor2_temp_list
        context['sensor2_labels']   = sensor2_labels
        context['sensor2_co_val']   = int(sensor2_co_list[-1])
        context['sensor2_o2_val']   = round(sensor2_o2_list[-1],1)
        context['sensor2_ch4_val']   = int(sensor2_ch4_list[-1])
        context['sensor2_temp_val']   = round(sensor2_temp_list[-1],1)
        context['sensor2_humid_val']   = int(sensor2_humid_list[-1])
        context['sensor2_power_per'] = int((sensor2_volt_list[-1]-3.3) / 0.9 * 100.0)
        context['sensor2_datenow'] = sensor2_labels[-1][0:16]

        print(sensor1_locs[-1].items())

        latitude_1  = sensor1_locs[-1]['latitude']
        longitude_1 = sensor1_locs[-1]['longitude']
        datetime_1  = timezone.localtime(sensor1_locs[-1]['created'])

        latitude_2  = sensor2_locs[-1]['latitude']
        longitude_2 = sensor2_locs[-1]['longitude']
        datetime_2  = timezone.localtime(sensor2_locs[-1]['created'])

        context['sensor1_latitude'] = latitude_1
        context['sensor1_longitude'] = longitude_1
        context['sensor2_latitude'] = latitude_2
        context['sensor2_longitude'] = longitude_2

        return context


class MultipleDashboardView(TemplateView):
    template_name = 'multiple_dash_board.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        with connection.cursor() as cursor:
            cursor.execute("select id, event, data_co, data_h2s, data_o2, data_ch4, created, volt from multiple_mesh_data where device_name = 'xenon1' order by created asc")
            xenon1_meshes = cursor.fetchall()

        with connection.cursor() as cursor:
            cursor.execute("select id, event, data_co, data_h2s, data_o2, data_ch4, created, volt from multiple_mesh_data where device_name = 'xenon2' order by created asc")
            xenon2_meshes = cursor.fetchall()

        with connection.cursor() as cursor:
            cursor.execute("select id, event, data_co, data_h2s, data_o2, data_ch4, created, volt from multiple_mesh_data where device_name = 'xenon2' order by created asc")
            xenon3_meshes = cursor.fetchall()

        with connection.cursor() as cursor:
            cursor.execute("select id, event, data_co, data_h2s, data_o2, data_ch4, created, volt from multiple_mesh_data where device_name = 'xenon2' order by created asc")
            xenon4_meshes = cursor.fetchall()

        df_xenon1 = pd.DataFrame(xenon1_meshes)
        df_xenon1.columns = ['id', 'event', 'data_co', 'data_h2s', 'data_o2', 'data_ch4', 'created', 'volt']
        df_xenon1['datetime'] = pd.to_datetime(df_xenon1['created'])
        df_xenon1=df_xenon1.set_index(pd.DatetimeIndex(df_xenon1['datetime']))

        df_xenon2 = pd.DataFrame(xenon2_meshes)
        df_xenon2.columns = ['id', 'event', 'data_co', 'data_h2s', 'data_o2', 'data_ch4', 'created', 'volt']
        df_xenon2['datetime'] = pd.to_datetime(df_xenon2['created'])
        df_xenon2=df_xenon2.set_index(pd.DatetimeIndex(df_xenon2['datetime']))

        df_xenon3 = pd.DataFrame(xenon3_meshes)
        df_xenon3.columns = ['id', 'event', 'data_co', 'data_h2s', 'data_o2', 'data_ch4', 'created', 'volt']
        df_xenon3['datetime'] = pd.to_datetime(df_xenon3['created'])
        df_xenon3=df_xenon3.set_index(pd.DatetimeIndex(df_xenon3['datetime']))

        df_xenon4 = pd.DataFrame(xenon4_meshes)
        df_xenon4.columns = ['id', 'event', 'data_co', 'data_h2s', 'data_o2', 'data_ch4', 'created', 'volt']
        df_xenon4['datetime'] = pd.to_datetime(df_xenon4['created'])
        df_xenon4=df_xenon4.set_index(pd.DatetimeIndex(df_xenon4['datetime']))

        df_xenon1 = df_xenon1[df_xenon1['datetime']>'2019-04-25 15:00']
        df_xenon2 = df_xenon2[df_xenon2['datetime']>'2019-04-25 15:00']
        df_xenon3 = df_xenon3[df_xenon3['datetime']>'2019-04-25 15:00']
        df_xenon4 = df_xenon4[df_xenon4['datetime']>'2019-04-25 15:00']

        # For Xenon1
        df_xenon1_co = df_xenon1['data_co'].resample("10s").max().fillna(0)
        df_xenon1_h2s = df_xenon1['data_h2s'].resample("10s").max().fillna(0)
        df_xenon1_o2 = df_xenon1['data_o2'].resample("10s").max().fillna(0)
        df_xenon1_ch4 = df_xenon1['data_ch4'].resample("10s").max().fillna(0)
        df_xenon1_co = df_xenon1_co.reset_index()
        df_xenon1_h2s = df_xenon1_h2s.reset_index()
        df_xenon1_o2 = df_xenon1_o2.reset_index()
        df_xenon1_ch4 = df_xenon1_ch4.reset_index()

        # For Xenon2
        df_xenon2_co = df_xenon2['data_co'].resample("10s").max().fillna(0)
        df_xenon2_h2s = df_xenon2['data_h2s'].resample("10s").max().fillna(0)
        df_xenon2_o2 = df_xenon2['data_o2'].resample("10s").max().fillna(0)
        df_xenon2_ch4 = df_xenon2['data_ch4'].resample("10s").max().fillna(0)
        df_xenon2_co = df_xenon2_co.reset_index()
        df_xenon2_h2s = df_xenon2_h2s.reset_index()
        df_xenon2_o2 = df_xenon2_o2.reset_index()
        df_xenon2_ch4 = df_xenon2_ch4.reset_index()

        # For Xenon3
        df_xenon3_co = df_xenon3['data_co'].resample("10s").max().fillna(0)
        df_xenon3_h2s = df_xenon3['data_h2s'].resample("10s").max().fillna(0)
        df_xenon3_o2 = df_xenon3['data_o2'].resample("10s").max().fillna(0)
        df_xenon3_ch4 = df_xenon3['data_ch4'].resample("10s").max().fillna(0)
        df_xenon3_co = df_xenon3_co.reset_index()
        df_xenon3_h2s = df_xenon3_h2s.reset_index()
        df_xenon3_o2 = df_xenon3_o2.reset_index()
        df_xenon3_ch4 = df_xenon3_ch4.reset_index()

        # For Xenon4
        df_xenon4_co = df_xenon4['data_co'].resample("10s").max().fillna(0)
        df_xenon4_h2s = df_xenon4['data_h2s'].resample("10s").max().fillna(0)
        df_xenon4_o2 = df_xenon4['data_o2'].resample("10s").max().fillna(0)
        df_xenon4_ch4 = df_xenon4['data_ch4'].resample("10s").max().fillna(0)
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
        xenon1_o2_list = []
        xenon2_o2_list = []
        xenon3_o2_list = []
        xenon4_o2_list = []
        xenon1_len_o2 = len(df_xenon1['data_o2'])
        xenon2_len_o2 = len(df_xenon2['data_o2'])
        xenon3_len_o2 = len(df_xenon3['data_o2'])
        xenon4_len_o2 = len(df_xenon4['data_o2'])

        for i in range(xenon1_len_o2) :
            xenon1_o2_per = df_xenon1['data_o2'][i] *20.9/2400.0
            xenon1_o2_list.append(round(xenon1_o2_per,1))

        for i in range(xenon2_len_o2) :
            xenon2_o2_per = df_xenon2['data_o2'][i] *20.9/2350.0
            xenon2_o2_list.append(round(xenon2_o2_per,1))

        for i in range(xenon3_len_o2) :
            xenon3_o2_per = df_xenon3['data_o2'][i] *20.9/2350.0
            xenon3_o2_list.append(round(xenon3_o2_per,1))

        for i in range(xenon4_len_o2) :
            xenon4_o2_per = df_xenon4['data_o2'][i] *20.9/2350.0
            xenon4_o2_list.append(round(xenon4_o2_per,1))

        xenon1_co_list = []
        xenon2_co_list = []
        xenon1_len_co = len(df_xenon1['data_co'])
        xenon2_len_co = len(df_xenon2['data_co'])

        for i in range(xenon1_len_co) :
            co_val = df_xenon1['data_co'][i]
            if co_val < 1900 :
                co_val = 1900

            co_voff = 1900.0 * 0.0011224
            co_v_diff = 3.3 - co_voff
            co_ppm = 1000.0 / co_v_diff * (co_val * 0.0011224 - co_voff)

            xenon1_co_list.append(int(co_ppm))

        # print(o2_list)
        # print(df_xenon1['data_o2'].tolist())
        # context['xenon1_data_co'] = df_xenon1_co['data_co'].tolist()
        context['xenon1_data_co'] = xenon1_co_list
        context['xenon1_data_h2s'] = df_xenon1_h2s['data_h2s'].tolist()
        # context['xenon1_data_o2'] = df_xenon1_o2['data_o2'].tolist()
        context['xenon1_data_o2'] = xenon1_o2_list
        context['xenon1_data_ch4'] = df_xenon1_ch4['data_ch4'].tolist()
        context['xenon1_labels'] = xenon1_labels

        context['xenon2_data_co'] = df_xenon2_co['data_co'].tolist()
        context['xenon2_data_co'] = df_xenon2_co['data_co'].tolist()
        context['xenon2_data_h2s'] = df_xenon2_h2s['data_h2s'].tolist()
        # context['xenon2_data_o2'] = df_xenon2_o2['data_o2'].tolist()
        context['xenon2_data_o2'] = xenon2_o2_list
        context['xenon2_data_ch4'] = df_xenon2_ch4['data_ch4'].tolist()
        context['xenon2_labels'] = xenon2_labels

        context['xenon3_data_co'] = df_xenon3_co['data_co'].tolist()
        context['xenon3_data_h2s'] = df_xenon3_h2s['data_h2s'].tolist()
        context['xenon3_data_o2'] = xenon3_o2_list
        # context['xenon3_data_o2'] = df_xenon3_o2['data_o2'].tolist()
        context['xenon3_data_ch4'] = df_xenon3_ch4['data_ch4'].tolist()
        context['xenon3_labels'] = xenon3_labels

        context['xenon4_data_co'] = df_xenon4_co['data_co'].tolist()
        context['xenon4_data_h2s'] = df_xenon4_h2s['data_h2s'].tolist()
        # context['xenon4_data_o2'] = df_xenon4_o2['data_o2'].tolist()
        context['xenon4_data_o2'] = xenon1_o2_list
        context['xenon4_data_ch4'] = df_xenon4_ch4['data_ch4'].tolist()
        context['xenon4_labels'] = xenon4_labels

        return context


class CloudDataboardView(TemplateView):
    template_name = 'cloud_databoard_views.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        with connection.cursor() as cursor:
            cursor.execute(
                "select id, event, data_co, data_o2, data_ch4, data_temp, data_humid, volt, created from cloud_mesh_data where device_name = 'xenon1' order by created desc limit 5")
            sensor1_meshes = cursor.fetchall()

        with connection.cursor() as cursor:
            cursor.execute(
                "select id, event, data_co, data_o2, data_ch4, data_temp, data_humid, volt, created from cloud_mesh_data where device_name = 'xenon2' order by created desc limit 5")
            sensor2_meshes = cursor.fetchall()

        with connection.cursor() as cursor:
            cursor.execute(
                "select id, event, data_co, data_o2, data_ch4, data_temp, data_humid, volt, created from cloud_mesh_data where device_name = 'xenon3' order by created desc limit 5")
            sensor3_meshes = cursor.fetchall()

        # with connection.cursor() as cursor:
        #     cursor.execute(
        #         "select id, event, data_co, data_o2, data_ch4, data_temp, data_humid, volt, created from cloud_mesh_data where device_name = 'xenon1' order by created desc limit 5")
        #     sensor4_meshes = cursor.fetchall()

        df_sensor1 = pd.DataFrame(sensor1_meshes)
        df_sensor1.columns = ['id', 'event', 'data_co', 'data_o2', 'data_ch4', 'data_temp', 'data_humid', 'volt',
                              'created']
        df_sensor1['datetime'] = pd.to_datetime(df_sensor1['created'])
        df_sensor1=df_sensor1.set_index(pd.DatetimeIndex(df_sensor1['datetime']))

        df_sensor2 = pd.DataFrame(sensor2_meshes)
        df_sensor2.columns = ['id', 'event', 'data_co', 'data_o2', 'data_ch4', 'data_temp', 'data_humid', 'volt',
                              'created']
        df_sensor2['datetime'] = pd.to_datetime(df_sensor2['created'])
        df_sensor2=df_sensor2.set_index(pd.DatetimeIndex(df_sensor2['datetime']))

        df_sensor3 = pd.DataFrame(sensor3_meshes)
        df_sensor3.columns = ['id', 'event', 'data_co', 'data_o2', 'data_ch4', 'data_temp', 'data_humid', 'volt',
                              'created']
        df_sensor3['datetime'] = pd.to_datetime(df_sensor3['created'])
        df_sensor3=df_sensor3.set_index(pd.DatetimeIndex(df_sensor3['datetime']))

        # df_sensor4 = pd.DataFrame(sensor4_meshes)
        # df_sensor4.columns = ['id', 'event', 'data_co', 'data_o2', 'data_ch4', 'data_temp', 'data_humid', 'volt',
        #                       'created']
        # df_sensor4['datetime'] = pd.to_datetime(df_sensor4['created'])
        # df_sensor4 = df_sensor4.set_index(pd.DatetimeIndex(df_sensor4['datetime']))

        df_sensor1 = df_sensor1[df_sensor1['datetime']>'2019-09-27 18:00']
        df_sensor2 = df_sensor2[df_sensor2['datetime']>'2019-09-27 18:00']
        df_sensor3 = df_sensor3[df_sensor3['datetime']>'2019-09-27 18:00']
        # df_sensor4 = df_sensor4[df_sensor4['datetime']>'2019-04-25 15:00']

        # For Sensor1
        df_sensor1_co    = df_sensor1['data_co'].resample("10m").max().fillna(0)
        df_sensor1_o2    = df_sensor1['data_o2'].resample("10m").max().fillna(0)
        df_sensor1_ch4   = df_sensor1['data_ch4'].resample("10m").max().fillna(0)
        df_sensor1_temp  = df_sensor1['data_temp'].resample("10m").max().fillna(0)
        df_sensor1_humid = df_sensor1['data_humid'].resample("10m").max().fillna(0)
        df_sensor1_volt  = df_sensor1['volt'].resample("10m").max().fillna(0)

        df_sensor1_co    = df_sensor1_co.reset_index()
        df_sensor1_o2    = df_sensor1_o2.reset_index()
        df_sensor1_ch4   = df_sensor1_ch4.reset_index()
        df_sensor1_temp  = df_sensor1_temp.reset_index()
        df_sensor1_humid = df_sensor1_humid.reset_index()
        df_sensor1_volt  = df_sensor1_volt.reset_index()

        # For Xenon2
        df_sensor2_co    = df_sensor2['data_co'].resample("10m").max().fillna(0)
        df_sensor2_o2    = df_sensor2['data_o2'].resample("10m").max().fillna(0)
        df_sensor2_ch4   = df_sensor2['data_ch4'].resample("10m").max().fillna(0)
        df_sensor2_temp  = df_sensor2['data_temp'].resample("10m").max().fillna(0)
        df_sensor2_humid = df_sensor2['data_humid'].resample("10m").max().fillna(0)
        df_sensor2_volt  = df_sensor2['volt'].resample("10m").max().fillna(0)

        df_sensor2_co    = df_sensor2_co.reset_index()
        df_sensor2_o2    = df_sensor2_o2.reset_index()
        df_sensor2_ch4   = df_sensor2_ch4.reset_index()
        df_sensor2_temp  = df_sensor2_temp.reset_index()
        df_sensor2_humid = df_sensor2_humid.reset_index()
        df_sensor2_volt  = df_sensor2_volt.reset_index()

        # For Xenon3
        df_sensor3_co    = df_sensor3['data_co'].resample("10m").max().fillna(0)
        df_sensor3_o2    = df_sensor3['data_o2'].resample("10m").max().fillna(0)
        df_sensor3_ch4   = df_sensor3['data_ch4'].resample("10m").max().fillna(0)
        df_sensor3_temp  = df_sensor3['data_temp'].resample("10m").max().fillna(0)
        df_sensor3_humid = df_sensor3['data_humid'].resample("10m").max().fillna(0)
        df_sensor3_volt  = df_sensor3['volt'].resample("10m").max().fillna(0)

        df_sensor3_co    = df_sensor3_co.reset_index()
        df_sensor3_o2    = df_sensor3_o2.reset_index()
        df_sensor3_ch4   = df_sensor3_ch4.reset_index()
        df_sensor3_temp  = df_sensor3_temp.reset_index()
        df_sensor3_humid = df_sensor3_humid.reset_index()
        df_sensor3_volt  = df_sensor3_volt.reset_index()

        # For Xenon4
        # df_sensor4_co    = df_sensor4['data_co'].resample("30s").max().fillna(0)
        # df_sensor4_o2    = df_sensor4['data_o2'].resample("30s").max().fillna(0)
        # df_sensor4_ch4   = df_sensor4['data_ch4'].resample("30s").max().fillna(0)
        # df_sensor4_temp  = df_sensor4['data_temp'].resample("30s").max().fillna(0)
        # df_sensor4_humid = df_sensor4['data_humid'].resample("30s").max().fillna(0)
        # df_sensor4_volt  = df_sensor4['volt'].resample("30s").max().fillna(0)
        #
        # df_sensor4_co    = df_sensor4_co.reset_index()
        # df_sensor4_o2    = df_sensor4_o2.reset_index()
        # df_sensor4_ch4   = df_sensor4_ch4.reset_index()
        # df_sensor4_temp  = df_sensor4_temp.reset_index()
        # df_sensor4_humid = df_sensor4_humid.reset_index()
        # df_sensor4_volt  = df_sensor4_volt.reset_index()

        sensor1_o2_per = df_sensor1_o2['data_o2'].tolist()[-1]
        sensor1_o2_val = round(sensor1_o2_per,1)
        sensor2_o2_per = df_sensor2_o2['data_o2'].tolist()[-1]
        sensor2_o2_val = round(sensor2_o2_per,1)
        sensor3_o2_per = df_sensor3_o2['data_o2'].tolist()[-1]
        sensor3_o2_val = round(sensor3_o2_per,1)
        # sensor4_o2_per = df_sensor4_o2['data_o2'].tolist()[-1]/10.0
        # sensor4_o2_val = round(sensor4_o2_per,1)

        sensor1_co_val = df_sensor1_co['data_co'].tolist()[-1]
        sensor2_co_val = df_sensor2_co['data_co'].tolist()[-1]
        sensor3_co_val = df_sensor3_co['data_co'].tolist()[-1]
        # sensor4_co_val = df_sensor4_co['data_co'].tolist()[-1]

        sensor1_ch4_val = df_sensor1_ch4['data_ch4'].tolist()[-1]
        sensor2_ch4_val = df_sensor2_ch4['data_ch4'].tolist()[-1]
        sensor3_ch4_val = df_sensor3_ch4['data_ch4'].tolist()[-1]
        # sensor4_ch4_val = df_sensor4_ch4['data_ch4'].tolist()[-1]

        sensor1_temp_val = df_sensor1_temp['data_temp'].tolist()[-1]
        sensor2_temp_val = df_sensor2_temp['data_temp'].tolist()[-1]
        sensor3_temp_val = df_sensor3_temp['data_temp'].tolist()[-1]
        # sensor4_temp_val = df_sensor4_temp['data_temp'].tolist()[-1]

        sensor1_humid_val = df_sensor1_humid['data_humid'].tolist()[-1]
        sensor2_humid_val = df_sensor2_humid['data_humid'].tolist()[-1]
        sensor3_humid_val = df_sensor3_humid['data_humid'].tolist()[-1]
        # sensor4_humid_val = df_sensor4_humid['data_humid'].tolist()[-1]

        sensor1_volt_val = df_sensor1_volt['volt'].tolist()[-1]
        sensor2_volt_val = df_sensor2_volt['volt'].tolist()[-1]
        sensor3_volt_val = df_sensor3_volt['volt'].tolist()[-1]
        # sensor4_volt_val = df_sensor4_volt['volt'].tolist()[-1]/100.0

        context['sensor1_data_co']    = int(sensor1_co_val)
        context['sensor1_data_o2']    = sensor1_o2_val
        context['sensor1_data_ch4']   = sensor1_ch4_val
        context['sensor1_data_temp']  = sensor1_temp_val
        context['sensor1_data_humid'] = sensor1_humid_val
        context['sensor1_volt']       = sensor1_volt_val
        context['sensor1_datetime']   = df_sensor1_o2['datetime'][0] - datetime.timedelta(hours=9)

        context['sensor2_data_co']    = int(sensor2_co_val)
        context['sensor2_data_o2']    = sensor2_o2_val
        context['sensor2_data_ch4']   = sensor2_ch4_val
        context['sensor2_data_temp']  = sensor2_temp_val
        context['sensor2_data_humid'] = sensor2_humid_val
        context['sensor2_volt']       = sensor2_volt_val
        context['sensor2_datetime']   = df_sensor2_o2['datetime'][0] - datetime.timedelta(hours=9)

        context['sensor3_data_co']    = int(sensor3_co_val)
        context['sensor3_data_o2']    = sensor3_o2_val
        context['sensor3_data_ch4']   = sensor3_ch4_val
        context['sensor3_data_temp']  = sensor3_temp_val
        context['sensor3_data_humid'] = sensor3_humid_val
        context['sensor3_volt']       = sensor3_volt_val
        context['sensor3_datetime']   = df_sensor3_o2['datetime'][0] - datetime.timedelta(hours=9)

        # context['sensor4_data_co']    = int(sensor4_co_val)
        # context['sensor4_data_o2']    = sensor4_o2_val
        # context['sensor4_data_ch4']   = sensor4_ch4_val
        # context['sensor4_data_temp']  = sensor4_temp_val
        # context['sensor4_data_humid'] = sensor4_humid_val
        # context['sensor4_volt']       = sensor4_volt_val
        # context['sensor4_datetime']   = df_sensor4_o2['datetime'][0] - datetime.timedelta(hours=9)

        return context


class DashboardNumbersView(TemplateView):
    template_name = 'dashboard_numbers.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        with connection.cursor() as cursor:
            cursor.execute("select id, event, data_co, data_h2s, data_o2, data_ch4, created, volt from multiple_mesh_data where device_name = 'xenon1' order by created desc limit 5")
            xenon1_meshes = cursor.fetchall()

        with connection.cursor() as cursor:
            cursor.execute("select id, event, data_co, data_h2s, data_o2, data_ch4, created, volt from multiple_mesh_data where device_name = 'xenon2' order by created desc limit 5")
            xenon2_meshes = cursor.fetchall()

        with connection.cursor() as cursor:
            cursor.execute("select id, event, data_co, data_h2s, data_o2, data_ch4, created, volt from multiple_mesh_data where device_name = 'xenon2' order by created desc limit 5")
            xenon3_meshes = cursor.fetchall()

        with connection.cursor() as cursor:
            cursor.execute("select id, event, data_co, data_h2s, data_o2, data_ch4, created, volt from multiple_mesh_data where device_name = 'xenon2' order by created desc limit 5")
            xenon4_meshes = cursor.fetchall()

        df_xenon1 = pd.DataFrame(xenon1_meshes)
        df_xenon1.columns = ['id', 'event', 'data_co', 'data_h2s', 'data_o2', 'data_ch4', 'created', 'volt']
        df_xenon1['datetime'] = pd.to_datetime(df_xenon1['created'])
        df_xenon1=df_xenon1.set_index(pd.DatetimeIndex(df_xenon1['datetime']))

        df_xenon2 = pd.DataFrame(xenon2_meshes)
        df_xenon2.columns = ['id', 'event', 'data_co', 'data_h2s', 'data_o2', 'data_ch4', 'created', 'volt']
        df_xenon2['datetime'] = pd.to_datetime(df_xenon2['created'])
        df_xenon2=df_xenon2.set_index(pd.DatetimeIndex(df_xenon2['datetime']))

        df_xenon3 = pd.DataFrame(xenon3_meshes)
        df_xenon3.columns = ['id', 'event', 'data_co', 'data_h2s', 'data_o2', 'data_ch4', 'created', 'volt']
        df_xenon3['datetime'] = pd.to_datetime(df_xenon3['created'])
        df_xenon3=df_xenon3.set_index(pd.DatetimeIndex(df_xenon3['datetime']))

        df_xenon4 = pd.DataFrame(xenon4_meshes)
        df_xenon4.columns = ['id', 'event', 'data_co', 'data_h2s', 'data_o2', 'data_ch4', 'created', 'volt']
        df_xenon4['datetime'] = pd.to_datetime(df_xenon4['created'])
        df_xenon4=df_xenon4.set_index(pd.DatetimeIndex(df_xenon4['datetime']))

        df_xenon1 = df_xenon1[df_xenon1['datetime']>'2019-04-25 15:00']
        df_xenon2 = df_xenon2[df_xenon2['datetime']>'2019-04-25 15:00']
        df_xenon3 = df_xenon3[df_xenon3['datetime']>'2019-04-25 15:00']
        df_xenon4 = df_xenon4[df_xenon4['datetime']>'2019-04-25 15:00']

        # For Xenon1
        df_xenon1_co = df_xenon1['data_co'].resample("10s").max().fillna(0)
        df_xenon1_h2s = df_xenon1['data_h2s'].resample("10s").max().fillna(0)
        df_xenon1_o2 = df_xenon1['data_o2'].resample("10s").max().fillna(0)
        df_xenon1_ch4 = df_xenon1['data_ch4'].resample("10s").max().fillna(0)
        df_xenon1_volt = df_xenon1['volt'].resample("10s").max().fillna(0)
        df_xenon1_co = df_xenon1_co.reset_index()
        df_xenon1_h2s = df_xenon1_h2s.reset_index()
        df_xenon1_o2 = df_xenon1_o2.reset_index()
        df_xenon1_ch4 = df_xenon1_ch4.reset_index()
        df_xenon1_volt = df_xenon1_volt.reset_index()

        # For Xenon2
        df_xenon2_co = df_xenon2['data_co'].resample("10s").max().fillna(0)
        df_xenon2_h2s = df_xenon2['data_h2s'].resample("10s").max().fillna(0)
        df_xenon2_o2 = df_xenon2['data_o2'].resample("10s").max().fillna(0)
        df_xenon2_ch4 = df_xenon2['data_ch4'].resample("10s").max().fillna(0)
        df_xenon2_volt = df_xenon2['volt'].resample("10s").max().fillna(0)
        df_xenon2_co = df_xenon2_co.reset_index()
        df_xenon2_h2s = df_xenon2_h2s.reset_index()
        df_xenon2_o2 = df_xenon2_o2.reset_index()
        df_xenon2_ch4 = df_xenon2_ch4.reset_index()
        df_xenon2_volt = df_xenon2_volt.reset_index()

        # For Xenon3
        df_xenon3_co = df_xenon3['data_co'].resample("10s").max().fillna(0)
        df_xenon3_h2s = df_xenon3['data_h2s'].resample("10s").max().fillna(0)
        df_xenon3_o2 = df_xenon3['data_o2'].resample("10s").max().fillna(0)
        df_xenon3_ch4 = df_xenon3['data_ch4'].resample("10s").max().fillna(0)
        df_xenon3_co = df_xenon3_co.reset_index()
        df_xenon3_h2s = df_xenon3_h2s.reset_index()
        df_xenon3_o2 = df_xenon3_o2.reset_index()
        df_xenon3_ch4 = df_xenon3_ch4.reset_index()

        # For Xenon4
        df_xenon4_co = df_xenon4['data_co'].resample("10s").max().fillna(0)
        df_xenon4_h2s = df_xenon4['data_h2s'].resample("10s").max().fillna(0)
        df_xenon4_o2 = df_xenon4['data_o2'].resample("10s").max().fillna(0)
        df_xenon4_ch4 = df_xenon4['data_ch4'].resample("10s").max().fillna(0)
        df_xenon4_co = df_xenon4_co.reset_index()
        df_xenon4_h2s = df_xenon4_h2s.reset_index()
        df_xenon4_o2 = df_xenon4_o2.reset_index()
        df_xenon4_ch4 = df_xenon4_ch4.reset_index()

        xenon1_o2_per = df_xenon1_o2['data_o2'].tolist()[-1]*20.9/2400.0
        xenon1_o2_per = round(xenon1_o2_per,1)
        xenon2_o2_per = df_xenon2_o2['data_o2'].tolist()[-1]*20.9/2350.0
        xenon2_o2_per = round(xenon2_o2_per,1)
        xenon3_o2_per = df_xenon3_o2['data_o2'].tolist()[-1]*20.9/2350.0
        xenon3_o2_per = round(xenon3_o2_per,1)
        xenon4_o2_per = df_xenon4_o2['data_o2'].tolist()[-1]*20.9/2350.0
        xenon4_o2_per = round(xenon4_o2_per,1)

        xenon1_co_val = df_xenon1_co['data_co'].tolist()[-1]
        xenon2_co_val = df_xenon2_co['data_co'].tolist()[-1]

        if xenon1_co_val < 1900 :
            xenon1_co_val = 1900

        if xenon2_co_val < 1900 :
            xenon2_co_val = 1900

        co_voff = 1900.0 * 0.0011224
        co_v_diff = 3.3 - co_voff
        xenon1_co_ppm = 1000.0 / co_v_diff * (xenon1_co_val * 0.0011224 - co_voff)
        xenon2_co_ppm = 1000.0 / co_v_diff * (xenon2_co_val * 0.0011224 - co_voff)

        context['xenon1_data_co'] = int(xenon1_co_ppm)
        # context['xenon1_data_co'] = df_xenon1_co['data_co'].tolist()[-1]
        context['xenon1_data_h2s'] = df_xenon1_h2s['data_h2s'].tolist()[0]
        # context['xenon1_data_o2'] = df_xenon1_o2['data_o2'].tolist()[-1]
        context['xenon1_data_o2'] = xenon1_o2_per
        context['xenon1_data_ch4'] = df_xenon1_ch4['data_ch4'].tolist()[0]
        context['xenon1_volt'] = df_xenon1_volt['volt'].tolist()[0]
        context['xenon1_datetime'] = df_xenon1['datetime'][0] - datetime.timedelta(hours=9)
        # context['xenon1_labels'] = xenon1_labels

        # context['xenon2_data_co'] = df_xenon2_co['data_co'].tolist()[-1]
        context['xenon2_data_co'] = int(xenon2_co_ppm)
        context['xenon2_data_h2s'] = df_xenon2_h2s['data_h2s'].tolist()[0]
        # context['xenon2_data_o2'] = df_xenon2_o2['data_o2'].tolist()[-1]
        context['xenon2_data_o2'] = xenon2_o2_per
        context['xenon2_data_ch4'] = df_xenon2_ch4['data_ch4'].tolist()[0]
        context['xenon2_volt'] = df_xenon2_volt['volt'].tolist()[0]
        context['xenon2_datetime'] = df_xenon2['datetime'][0] - datetime.timedelta(hours=9)
        # context['xenon2_labels'] = xenon2_labels

        context['xenon3_data_co'] = df_xenon3_co['data_co'].tolist()[-1]
        context['xenon3_data_h2s'] = df_xenon3_h2s['data_h2s'].tolist()[-1]
        # context['xenon3_data_o2'] = df_xenon3_o2['data_o2'].tolist()[-1]
        context['xenon3_data_o2'] = xenon3_o2_per
        context['xenon3_data_ch4'] = df_xenon3_ch4['data_ch4'].tolist()[-1]
        # context['xenon3_labels'] = xenon3_labels

        context['xenon4_data_co'] = df_xenon4_co['data_co'].tolist()[-1]
        context['xenon4_data_h2s'] = df_xenon4_h2s['data_h2s'].tolist()[-1]
        # context['xenon4_data_o2'] = df_xenon4_o2['data_o2'].tolist()[-1]
        context['xenon4_data_o2'] = xenon4_o2_per
        context['xenon4_data_ch4'] = df_xenon4_ch4['data_ch4'].tolist()[-1]
        # context['xenon4_labels'] = xenon4_labels

        return context


class CloudDashboardUpdateView(View):

    def get(self, request, *args, **kwargs):

        if request.is_ajax():
            with connection.cursor() as cursor:
                cursor.execute(
                    "select id, event, data_co, data_o2, data_ch4, data_temp, data_humid, volt, created from cloud_mesh_data where device_name = 'xenon1' order by created asc")
                sensor1_meshes = cursor.fetchall()

            with connection.cursor() as cursor:
                cursor.execute(
                    "select id, event, data_co, data_o2, data_ch4, data_temp, data_humid, volt, created from cloud_mesh_data where device_name = 'xenon2' order by created asc")
                sensor2_meshes = cursor.fetchall()

            with connection.cursor() as cursor:
                cursor.execute(
                    "select id, event, data_co, data_o2, data_ch4, data_temp, data_humid, volt, created from cloud_mesh_data where device_name = 'xenon3' order by created asc")
                sensor3_meshes = cursor.fetchall()
            #
            # with connection.cursor() as cursor:
            #     cursor.execute("select id, event, data_co, data_h2s, data_o2, data_ch4, created, volt from multiple_mesh_data where device_name = 'xenon2' order by created asc")
            #     xenon4_meshes = cursor.fetchall()

            df_sensor1 = pd.DataFrame(sensor1_meshes)
            df_sensor1.columns = ['id', 'event', 'data_co', 'data_o2', 'data_ch4', 'data_temp', 'data_humid', 'volt', 'created']
            df_sensor1['datetime'] = pd.to_datetime(df_sensor1['created'])
            df_sensor1 = df_sensor1.set_index(pd.DatetimeIndex(df_sensor1['datetime']))

            df_sensor2 = pd.DataFrame(sensor2_meshes)
            df_sensor2.columns = ['id', 'event', 'data_co', 'data_o2', 'data_ch4', 'data_temp', 'data_humid', 'volt', 'created']
            df_sensor2['datetime'] = pd.to_datetime(df_sensor2['created'])
            df_sensor2 = df_sensor2.set_index(pd.DatetimeIndex(df_sensor2['datetime']))

            df_sensor3 = pd.DataFrame(sensor3_meshes)
            df_sensor3.columns = ['id', 'event', 'data_co', 'data_o2', 'data_ch4', 'data_temp', 'data_humid', 'volt', 'created']
            df_sensor3['datetime'] = pd.to_datetime(df_sensor3['created'])
            df_sensor3=df_sensor3.set_index(pd.DatetimeIndex(df_sensor3['datetime']))
            #
            # df_sensor4 = pd.DataFrame(sensor4_meshes)
            # df_sensor4.columns = ['id', 'event', 'data_co', 'data_o2', 'data_ch4', 'data_temp', 'data_humid', 'volt', 'created']
            # df_sensor4['datetime'] = pd.to_datetime(df_sensor4['created'])
            # df_sensor4=df_sensor4.set_index(pd.DatetimeIndex(df_sensor4['datetime']))

            df_sensor1 = df_sensor1[df_sensor1['datetime'] > '2019-10-09 13:00']
            df_sensor2 = df_sensor2[df_sensor2['datetime'] > '2019-10-09 13:00']
            df_sensor3 = df_sensor3[df_sensor3['datetime'] > '2019-10-09 13:00']
            # df_sensor4 = df_sensor4[df_sensor4['datetime']>'2019-04-25 15:00']

            # For Sensor1
            df_sensor1_co = df_sensor1['data_co'].resample("600s").median().fillna(0)
            df_sensor1_o2 = df_sensor1['data_o2'].resample("600s").median().fillna(0)
            df_sensor1_ch4 = df_sensor1['data_ch4'].resample("600s").median().fillna(0)
            df_sensor1_temp = df_sensor1['data_temp'].resample("600s").median().fillna(0)
            df_sensor1_humid = df_sensor1['data_humid'].resample("600s").median().fillna(0)
            df_sensor1_volt = df_sensor1['volt'].resample("600s").median().fillna(0)

            df_sensor1_co = df_sensor1_co.reset_index()
            df_sensor1_o2 = df_sensor1_o2.reset_index()
            df_sensor1_ch4 = df_sensor1_ch4.reset_index()
            df_sensor1_volt = df_sensor1_volt.reset_index()

            # For Sensor2
            df_sensor2_co = df_sensor2['data_co'].resample("600s").median().fillna(0)
            df_sensor2_o2 = df_sensor2['data_o2'].resample("600s").median().fillna(0)
            df_sensor2_ch4 = df_sensor2['data_ch4'].resample("600s").median().fillna(0)
            df_sensor2_temp = df_sensor2['data_temp'].resample("600s").median().fillna(0)
            df_sensor2_humid = df_sensor2['data_humid'].resample("600s").median().fillna(0)
            df_sensor2_volt = df_sensor2['volt'].resample("600s").median().fillna(0)

            df_sensor2_co = df_sensor2_co.reset_index()
            df_sensor2_o2 = df_sensor2_o2.reset_index()
            df_sensor2_ch4 = df_sensor2_ch4.reset_index()
            df_sensor2_volt = df_sensor2_volt.reset_index()

            # For Sensor3
            df_sensor3_co       = df_sensor3['data_co'].resample("600s").median().fillna(0)
            df_sensor3_o2       = df_sensor3['data_o2'].resample("600s").median().fillna(0)
            df_sensor3_ch4      = df_sensor3['data_ch4'].resample("600s").median().fillna(0)
            df_sensor3_temp     = df_sensor3['data_temp'].resample("600s").median().fillna(0)
            df_sensor3_humid    = df_sensor3['data_humid'].resample("600s").median().fillna(0)
            df_sensor3_volt     = df_sensor3['volt'].resample("600s").median().fillna(0)

            df_sensor3_co       = df_sensor3_co.reset_index()
            df_sensor3_o2       = df_sensor3_o2.reset_index()
            df_sensor3_ch4      = df_sensor3_ch4.reset_index()
            df_sensor3_volt     = df_sensor3_volt.reset_index()
            #
            # # For Sensor4
            # df_sensor4_co       = df_sensor4['data_co'].resample("10s").max().fillna(0)
            # df_sensor4_o2       = df_sensor4['data_o2'].resample("10s").max().fillna(0)
            # df_sensor4_ch4      = df_sensor4['data_ch4'].resample("10s").max().fillna(0)
            # df_sensor4_temp     = df_sensor4['data_temp'].resample("10s").max().fillna(0)
            # df_sensor4_humid    = df_sensor4['data_humid'].resample("10s").max().fillna(0)
            # df_sensor4_volt     = df_sensor4['data_volt'].resample("10s").max().fillna(0)
            #
            # df_sensor4_co   = df_sensor4_co.reset_index()
            # df_sensor4_o2   = df_sensor4_o2.reset_index()
            # df_sensor4_ch4  = df_sensor4_ch4.reset_index()
            # df_sensor4_volt = df_sensor4_volt.reset_index()

            sensor1_dts = df_sensor1_co['datetime'].tolist()
            sensor2_dts = df_sensor2_co['datetime'].tolist()
            sensor3_dts = df_sensor3_co['datetime'].tolist()
            # sensor4_dts = df_sensor4_co['datetime'].tolist()

            sensor1_o2_per = df_sensor1_o2['data_o2'].tolist()[-1]
            sensor2_o2_per = df_sensor2_o2['data_o2'].tolist()[-1]
            sensor3_o2_per = df_sensor3_o2['data_o2'].tolist()[-1]
            # sensor4_o2_per = df_sensor4_o2['data_o2'].tolist()[-1]

            sensor1_co_per = df_sensor1_co['data_co'].tolist()[-1]
            sensor2_co_per = df_sensor2_co['data_co'].tolist()[-1]
            sensor3_co_per = df_sensor3_co['data_co'].tolist()[-1]
            # sensor4_co_per = df_sensor4_co['data_co'].tolist()[-1]

            sensor1_ch4_per = df_sensor1_ch4['data_ch4'].tolist()[-1]
            sensor2_ch4_per = df_sensor2_ch4['data_ch4'].tolist()[-1]
            sensor3_ch4_per = df_sensor3_ch4['data_ch4'].tolist()[-1]
            # sensor4_ch4_per = df_sensor4_ch4['data_ch4'].tolist()[-1]

            sensor1_volt_per = df_sensor1_volt['volt'].tolist()[-1]
            sensor2_volt_per = df_sensor2_volt['volt'].tolist()[-1]
            sensor3_volt_per = df_sensor3_volt['volt'].tolist()[-1]

            # print('sensor1_dts')
            # print(str(sensor1_dts[-1])[:19])
            # print('sensor1_o2_per')
            # print(sensor1_o2_per)
            # print('sensor1_co_per')
            # print(sensor1_co_per)
            # print('sensor1_ch4_per')
            # print(sensor1_ch4_per)

            data = {'sensor1_label': str(sensor1_dts[-1])[:19],
                    'sensor1_data_co': sensor1_co_per,
                    'sensor1_data_o2': sensor1_o2_per,
                    'sensor1_data_ch4': sensor1_ch4_per,
                    'sensor1_volt': sensor1_volt_per,
                    'sensor2_label': str(sensor2_dts[-1])[:19],
                    'sensor2_data_co': sensor2_co_per,
                    'sensor2_data_o2': sensor2_o2_per,
                    'sensor2_data_ch4': sensor2_ch4_per,
                    'sensor2_volt': sensor2_volt_per,
                    'sensor3_label': str(sensor3_dts[-1])[:19],
                    'sensor3_data_co': sensor3_co_per,
                    'sensor3_data_o2': sensor3_o2_per,
                    'sensor3_data_ch4': sensor3_ch4_per,
                    'sensor3_volt': sensor3_volt_per,
                    }

            return JsonResponse(data)


class DashboardUpdateView(View):

    def get(self, request, *args, **kwargs):
        if request.is_ajax():
            with connection.cursor() as cursor:
                cursor.execute(
                    "select id, event, data_co, data_h2s, data_o2, data_ch4, created, volt from multiple_mesh_data where device_name = 'xenon1' order by created asc")
                xenon1_meshes = cursor.fetchall()

            with connection.cursor() as cursor:
                cursor.execute(
                    "select id, event, data_co, data_h2s, data_o2, data_ch4, created, volt from multiple_mesh_data where device_name = 'xenon2' order by created asc")
                xenon2_meshes = cursor.fetchall()

            with connection.cursor() as cursor:
                cursor.execute(
                    "select id, event, data_co, data_h2s, data_o2, data_ch4, created, volt from multiple_mesh_data where device_name = 'xenon2' order by created asc")
                xenon3_meshes = cursor.fetchall()

            with connection.cursor() as cursor:
                cursor.execute(
                    "select id, event, data_co, data_h2s, data_o2, data_ch4, created, volt from multiple_mesh_data where device_name = 'xenon2' order by created asc")
                xenon4_meshes = cursor.fetchall()

            df_xenon1 = pd.DataFrame(xenon1_meshes)
            df_xenon1.columns = ['id', 'event', 'data_co', 'data_h2s', 'data_o2', 'data_ch4', 'created', 'volt']
            df_xenon1['datetime'] = pd.to_datetime(df_xenon1['created'])
            df_xenon1 = df_xenon1.set_index(pd.DatetimeIndex(df_xenon1['datetime']))

            df_xenon2 = pd.DataFrame(xenon2_meshes)
            df_xenon2.columns = ['id', 'event', 'data_co', 'data_h2s', 'data_o2', 'data_ch4', 'created', 'volt']
            df_xenon2['datetime'] = pd.to_datetime(df_xenon2['created'])
            df_xenon2 = df_xenon2.set_index(pd.DatetimeIndex(df_xenon2['datetime']))

            df_xenon3 = pd.DataFrame(xenon3_meshes)
            df_xenon3.columns = ['id', 'event', 'data_co', 'data_h2s', 'data_o2', 'data_ch4', 'created', 'volt']
            df_xenon3['datetime'] = pd.to_datetime(df_xenon3['created'])
            df_xenon3 = df_xenon3.set_index(pd.DatetimeIndex(df_xenon3['datetime']))

            df_xenon4 = pd.DataFrame(xenon4_meshes)
            df_xenon4.columns = ['id', 'event', 'data_co', 'data_h2s', 'data_o2', 'data_ch4', 'created', 'volt']
            df_xenon4['datetime'] = pd.to_datetime(df_xenon4['created'])
            df_xenon4 = df_xenon4.set_index(pd.DatetimeIndex(df_xenon4['datetime']))

            df_xenon1 = df_xenon1[df_xenon1['datetime'] > '2019-04-25 15:00']
            df_xenon2 = df_xenon2[df_xenon2['datetime'] > '2019-04-25 15:00']
            df_xenon3 = df_xenon3[df_xenon3['datetime'] > '2019-04-25 15:00']
            df_xenon4 = df_xenon4[df_xenon4['datetime'] > '2019-04-25 15:00']

            # For Xenon1
            df_xenon1_co = df_xenon1['data_co'].resample("10s").max().fillna(0)
            df_xenon1_h2s = df_xenon1['data_h2s'].resample("10s").max().fillna(0)
            df_xenon1_o2 = df_xenon1['data_o2'].resample("10s").max().fillna(0)
            df_xenon1_ch4 = df_xenon1['data_ch4'].resample("10s").max().fillna(0)
            df_xenon1_co = df_xenon1_co.reset_index()
            df_xenon1_h2s = df_xenon1_h2s.reset_index()
            df_xenon1_o2 = df_xenon1_o2.reset_index()
            df_xenon1_ch4 = df_xenon1_ch4.reset_index()

            # For Xenon2
            df_xenon2_co = df_xenon2['data_co'].resample("10s").max().fillna(0)
            df_xenon2_h2s = df_xenon2['data_h2s'].resample("10s").max().fillna(0)
            df_xenon2_o2 = df_xenon2['data_o2'].resample("10s").max().fillna(0)
            df_xenon2_ch4 = df_xenon2['data_ch4'].resample("10s").max().fillna(0)
            df_xenon2_co = df_xenon2_co.reset_index()
            df_xenon2_h2s = df_xenon2_h2s.reset_index()
            df_xenon2_o2 = df_xenon2_o2.reset_index()
            df_xenon2_ch4 = df_xenon2_ch4.reset_index()

            # For Xenon3
            df_xenon3_co = df_xenon3['data_co'].resample("10s").max().fillna(0)
            df_xenon3_h2s = df_xenon3['data_h2s'].resample("10s").max().fillna(0)
            df_xenon3_o2 = df_xenon3['data_o2'].resample("10s").max().fillna(0)
            df_xenon3_ch4 = df_xenon3['data_ch4'].resample("10s").max().fillna(0)
            df_xenon3_co = df_xenon3_co.reset_index()
            df_xenon3_h2s = df_xenon3_h2s.reset_index()
            df_xenon3_o2 = df_xenon3_o2.reset_index()
            df_xenon3_ch4 = df_xenon3_ch4.reset_index()

            # For Xenon4
            df_xenon4_co = df_xenon4['data_co'].resample("10s").max().fillna(0)
            df_xenon4_h2s = df_xenon4['data_h2s'].resample("10s").max().fillna(0)
            df_xenon4_o2 = df_xenon4['data_o2'].resample("10s").max().fillna(0)
            df_xenon4_ch4 = df_xenon4['data_ch4'].resample("10s").max().fillna(0)
            df_xenon4_co = df_xenon4_co.reset_index()
            df_xenon4_h2s = df_xenon4_h2s.reset_index()
            df_xenon4_o2 = df_xenon4_o2.reset_index()
            df_xenon4_ch4 = df_xenon4_ch4.reset_index()

            xenon1_dts = df_xenon1_co['datetime'].tolist()
            xenon2_dts = df_xenon2_co['datetime'].tolist()
            xenon3_dts = df_xenon3_co['datetime'].tolist()
            xenon4_dts = df_xenon4_co['datetime'].tolist()

            xenon1_o2_per = df_xenon1_o2['data_o2'].tolist()[-1] * 20.9/2400.0
            xenon1_o2_per = round(xenon1_o2_per,1)
            xenon2_o2_per = df_xenon2_o2['data_o2'].tolist()[-1] * 20.9/2350.0
            xenon2_o2_per = round(xenon2_o2_per,1)
            xenon3_o2_per = df_xenon3_o2['data_o2'].tolist()[-1] * 20.9/2350.0
            xenon3_o2_per = round(xenon3_o2_per,1)
            xenon4_o2_per = df_xenon4_o2['data_o2'].tolist()[-1] * 20.9/2350.0
            xenon4_o2_per = round(xenon4_o2_per,1)

            xenon1_co_val = df_xenon4_co['data_co'].tolist()[-1]

            if xenon1_co_val < 1900 :
                xenon1_co_val = 1900

            co_voff = 1900.0 * 0.0011224
            co_v_diff = 3.3 - co_voff
            xenon1_co_ppm = 1000.0 / co_v_diff * (xenon1_co_val * 0.0011224 - co_voff)

            print(str(xenon1_dts[-1])[:19], '****')

            data = {'xenon1_label': str(xenon1_dts[-1])[:19],
                    'xenon1_data_co': int(xenon1_co_ppm), 'xenon1_data_h2s': df_xenon1_h2s['data_h2s'].tolist()[-1],
                    'xenon1_data_o2': xenon1_o2_per, 'xenon1_data_ch4': df_xenon1_ch4['data_ch4'].tolist()[-1],
                    'xenon2_label': str(xenon2_dts[-1])[:19],
                    'xenon2_data_co': df_xenon2_co['data_co'].tolist()[-1], 'xenon2_data_h2s': df_xenon2_h2s['data_h2s'].tolist()[-1],
                    'xenon2_data_o2': xenon2_o2_per, 'xenon2_data_ch4': df_xenon2_ch4['data_ch4'].tolist()[-1],
                    'xenon3_label': str(xenon3_dts[-1])[:19],
                    'xenon3_data_co': df_xenon3_co['data_co'].tolist()[-1], 'xenon3_data_h2s': df_xenon3_h2s['data_h2s'].tolist()[-1],
                    'xenon3_data_o2': xenon3_o2_per, 'xenon3_data_ch4': df_xenon3_ch4['data_ch4'].tolist()[-1],
                    'xenon4_label': str(xenon4_dts[-1])[:19],
                    'xenon4_data_co': df_xenon4_co['data_co'].tolist()[-1], 'xenon4_data_h2s': df_xenon4_h2s['data_h2s'].tolist()[-1],
                    'xenon4_data_o2': xenon4_o2_per, 'xenon4_data_ch4': df_xenon4_ch4['data_ch4'].tolist()[-1],
                    }

            return JsonResponse(data)


class CloudDataboardUpdateView(View):

    def get(self, request, *args, **kwargs):
        if request.is_ajax():
            with connection.cursor() as cursor:
                cursor.execute(
                    "select id, event, data_co, data_o2, data_ch4, data_temp, data_humid, volt, created from cloud_mesh_data where device_name = 'xenon1' order by created desc limit 5")
                sensor1_meshes = cursor.fetchall()

            with connection.cursor() as cursor:
                cursor.execute(
                    "select id, event, data_co, data_o2, data_ch4, data_temp, data_humid, volt, created from cloud_mesh_data where device_name = 'xenon2' order by created desc limit 5")
                sensor2_meshes = cursor.fetchall()

            with connection.cursor() as cursor:
                cursor.execute(
                    "select id, event, data_co, data_o2, data_ch4, data_temp, data_humid, volt, created from cloud_mesh_data where device_name = 'xenon3' order by created desc limit 5")
                sensor3_meshes = cursor.fetchall()

            with connection.cursor() as cursor:
                cursor.execute(
                    "select id, event, data_co, data_o2, data_ch4, data_temp, data_humid, volt, created from cloud_mesh_data where device_name = 'xenon3' order by created desc limit 5")
                sensor4_meshes = cursor.fetchall()

            df_sensor1 = pd.DataFrame(sensor1_meshes)
            df_sensor1.columns = ['id', 'event', 'data_co', 'data_o2', 'data_ch4', 'data_temp', 'data_humid', 'volt',
                                  'created']
            df_sensor1['datetime'] = pd.to_datetime(df_sensor1['created'])
            df_sensor1 = df_sensor1.set_index(pd.DatetimeIndex(df_sensor1['datetime']))

            df_sensor2 = pd.DataFrame(sensor2_meshes)
            df_sensor2.columns = ['id', 'event', 'data_co', 'data_o2', 'data_ch4', 'data_temp', 'data_humid', 'volt',
                                  'created']
            df_sensor2['datetime'] = pd.to_datetime(df_sensor2['created'])
            df_sensor2 = df_sensor2.set_index(pd.DatetimeIndex(df_sensor2['datetime']))

            df_sensor3 = pd.DataFrame(sensor3_meshes)
            df_sensor3.columns = ['id', 'event', 'data_co', 'data_o2', 'data_ch4', 'data_temp', 'data_humid', 'volt',
                                  'created']
            df_sensor3['datetime'] = pd.to_datetime(df_sensor3['created'])
            df_sensor3 = df_sensor3.set_index(pd.DatetimeIndex(df_sensor3['datetime']))

            df_sensor4 = pd.DataFrame(sensor4_meshes)
            df_sensor4.columns = ['id', 'event', 'data_co', 'data_o2', 'data_ch4', 'data_temp', 'data_humid', 'volt',
                                  'created']
            df_sensor4['datetime'] = pd.to_datetime(df_sensor4['created'])
            df_sensor4 = df_sensor4.set_index(pd.DatetimeIndex(df_sensor4['datetime']))

            df_sensor1 = df_sensor1[df_sensor1['datetime'] > '2019-09-27 18:00']
            df_sensor2 = df_sensor2[df_sensor2['datetime'] > '2019-09-27 18:00']
            df_sensor3 = df_sensor3[df_sensor3['datetime'] > '2019-09-27 18:00']
            df_sensor4 = df_sensor4[df_sensor4['datetime'] > '2019-09-27 18:00']

            # For Sensor1
            df_sensor1_co = df_sensor1['data_co'].resample("600s").max().fillna(0)
            df_sensor1_o2 = df_sensor1['data_o2'].resample("600s").max().fillna(0)
            df_sensor1_ch4 = df_sensor1['data_ch4'].resample("600s").max().fillna(0)
            df_sensor1_temp = df_sensor1['data_temp'].resample("600s").max().fillna(0)
            df_sensor1_humid = df_sensor1['data_humid'].resample("600s").max().fillna(0)
            df_sensor1_volt = df_sensor1['volt'].resample("600s").max().fillna(0)

            df_sensor1_co = df_sensor1_co.reset_index()
            df_sensor1_o2 = df_sensor1_o2.reset_index()
            df_sensor1_ch4 = df_sensor1_ch4.reset_index()
            df_sensor1_temp = df_sensor1_temp.reset_index()
            df_sensor1_humid = df_sensor1_humid.reset_index()
            df_sensor1_volt = df_sensor1_volt.reset_index()

            # For Xenon2
            df_sensor2_co = df_sensor2['data_co'].resample("600s").max().fillna(0)
            df_sensor2_o2 = df_sensor2['data_o2'].resample("600s").max().fillna(0)
            df_sensor2_ch4 = df_sensor2['data_ch4'].resample("600s").max().fillna(0)
            df_sensor2_temp = df_sensor2['data_temp'].resample("600s").max().fillna(0)
            df_sensor2_humid = df_sensor2['data_humid'].resample("600s").max().fillna(0)
            df_sensor2_volt = df_sensor2['volt'].resample("600s").max().fillna(0)

            df_sensor2_co = df_sensor2_co.reset_index()
            df_sensor2_o2 = df_sensor2_o2.reset_index()
            df_sensor2_ch4 = df_sensor2_ch4.reset_index()
            df_sensor2_temp = df_sensor2_temp.reset_index()
            df_sensor2_humid = df_sensor2_humid.reset_index()
            df_sensor2_volt = df_sensor2_volt.reset_index()

            # For Xenon3
            df_sensor3_co = df_sensor3['data_co'].resample("600s").max().fillna(0)
            df_sensor3_o2 = df_sensor3['data_o2'].resample("600s").max().fillna(0)
            df_sensor3_ch4 = df_sensor3['data_ch4'].resample("600s").max().fillna(0)
            df_sensor3_temp = df_sensor3['data_temp'].resample("600s").max().fillna(0)
            df_sensor3_humid = df_sensor3['data_humid'].resample("600s").max().fillna(0)
            df_sensor3_volt = df_sensor3['volt'].resample("600s").max().fillna(0)

            df_sensor3_co = df_sensor3_co.reset_index()
            df_sensor3_o2 = df_sensor3_o2.reset_index()
            df_sensor3_ch4 = df_sensor3_ch4.reset_index()
            df_sensor3_temp = df_sensor3_temp.reset_index()
            df_sensor3_humid = df_sensor3_humid.reset_index()
            df_sensor3_volt = df_sensor3_volt.reset_index()

            # For Xenon4
            df_sensor4_co = df_sensor4['data_co'].resample("600s").max().fillna(0)
            df_sensor4_o2 = df_sensor4['data_o2'].resample("600s").max().fillna(0)
            df_sensor4_ch4 = df_sensor4['data_ch4'].resample("600s").max().fillna(0)
            df_sensor4_temp = df_sensor4['data_temp'].resample("600s").max().fillna(0)
            df_sensor4_humid = df_sensor4['data_humid'].resample("600s").max().fillna(0)
            df_sensor4_volt = df_sensor4['volt'].resample("600s").max().fillna(0)

            df_sensor4_co = df_sensor4_co.reset_index()
            df_sensor4_o2 = df_sensor4_o2.reset_index()
            df_sensor4_ch4 = df_sensor4_ch4.reset_index()
            df_sensor4_temp = df_sensor4_temp.reset_index()
            df_sensor4_humid = df_sensor4_humid.reset_index()
            df_sensor4_volt = df_sensor4_volt.reset_index()

            sensor1_o2_per = df_sensor1_o2['data_o2'].tolist()[-1]
            sensor1_o2_val = round(sensor1_o2_per, 1)
            sensor2_o2_per = df_sensor2_o2['data_o2'].tolist()[-1]
            sensor2_o2_val = round(sensor2_o2_per, 1)
            sensor3_o2_per = df_sensor3_o2['data_o2'].tolist()[-1]
            sensor3_o2_val = round(sensor3_o2_per, 1)
            sensor4_o2_per = df_sensor4_o2['data_o2'].tolist()[-1]
            sensor4_o2_val = round(sensor4_o2_per, 1)

            sensor1_co_val = df_sensor1_co['data_co'].tolist()[-1]
            sensor2_co_val = df_sensor2_co['data_co'].tolist()[-1]
            sensor3_co_val = df_sensor3_co['data_co'].tolist()[-1]
            sensor4_co_val = df_sensor4_co['data_co'].tolist()[-1]

            sensor1_ch4_val = df_sensor1_ch4['data_ch4'].tolist()[-1]
            sensor2_ch4_val = df_sensor2_ch4['data_ch4'].tolist()[-1]
            sensor3_ch4_val = df_sensor3_ch4['data_ch4'].tolist()[-1]
            sensor4_ch4_val = df_sensor4_ch4['data_ch4'].tolist()[-1]

            sensor1_temp_val = df_sensor1_temp['data_temp'].tolist()[-1]
            sensor2_temp_val = df_sensor2_temp['data_temp'].tolist()[-1]
            sensor3_temp_val = df_sensor3_temp['data_temp'].tolist()[-1]
            sensor4_temp_val = df_sensor4_temp['data_temp'].tolist()[-1]

            sensor1_humid_val = df_sensor1_humid['data_humid'].tolist()[-1]
            sensor2_humid_val = df_sensor2_humid['data_humid'].tolist()[-1]
            sensor3_humid_val = df_sensor3_humid['data_humid'].tolist()[-1]
            sensor4_humid_val = df_sensor4_humid['data_humid'].tolist()[-1]

            sensor1_volt_val = df_sensor1_volt['volt'].tolist()[-1]
            sensor2_volt_val = df_sensor2_volt['volt'].tolist()[-1]
            sensor3_volt_val = df_sensor3_volt['volt'].tolist()[-1]
            sensor4_volt_val = df_sensor4_volt['volt'].tolist()[-1]

            sensor1_datetime = df_sensor1_o2['datetime'][0]
            sensor2_datetime = df_sensor2_o2['datetime'][0]
            sensor3_datetime = df_sensor3_o2['datetime'][0]
            sensor4_datetime = df_sensor4_o2['datetime'][0]

            data = {'sensor1_label'     : str(sensor1_datetime)[:19],
                    'sensor1_data_co'   : int(sensor1_co_val),
                    'sensor1_data_o2'   : sensor1_o2_val,
                    'sensor1_data_ch4'  : sensor1_ch4_val,
                    'sensor1_data_temp' : sensor1_temp_val,
                    'sensor1_data_humid': sensor1_humid_val,
                    'sensor1_volt'      : sensor1_volt_val,
                    'sensor1_datetime'  : sensor1_datetime,
                    'sensor2_label'     : str(sensor2_datetime)[:19],
                    'sensor2_data_co'   : int(sensor2_co_val),
                    'sensor2_data_o2'   : sensor2_o2_val,
                    'sensor2_data_ch4'  : sensor2_ch4_val,
                    'sensor2_data_temp' : sensor2_temp_val,
                    'sensor2_data_humid': sensor2_humid_val,
                    'sensor2_volt'      : sensor2_volt_val,
                    'sensor2_datetime'  : sensor2_datetime,
                    'sensor3_label'     : str(sensor3_datetime)[:19],
                    'sensor3_data_co'   : int(sensor3_co_val),
                    'sensor3_data_o2'   : sensor3_o2_val,
                    'sensor3_data_ch4'  : sensor3_ch4_val,
                    'sensor3_data_temp' : sensor3_temp_val,
                    'sensor3_data_humid': sensor3_humid_val,
                    'sensor3_volt'      : sensor3_volt_val,
                    'sensor3_datetime'  : sensor3_datetime,
                    'sensor4_label'     : str(sensor4_datetime)[:19],
                    'sensor4_data_co'   : int(sensor4_co_val),
                    'sensor4_data_o2'   : sensor4_o2_val,
                    'sensor4_data_ch4'  : sensor4_ch4_val,
                    'sensor4_data_temp' : sensor4_temp_val,
                    'sensor4_data_humid': sensor4_humid_val,
                    'sensor4_volt'      : sensor4_volt_val,
                    'sensor4_datetime'  : sensor4_datetime,
                    }

            return JsonResponse(data)


class DashboardNumnersUpdateView(View):

    def get(self, request, *args, **kwargs):
        if request.is_ajax():
            with connection.cursor() as cursor:
                cursor.execute(
                    "select id, event, data_co, data_h2s, data_o2, data_ch4, created, volt from multiple_mesh_data where device_name = 'xenon1' order by created desc limit 5")
                xenon1_meshes = cursor.fetchall()

            with connection.cursor() as cursor:
                cursor.execute(
                    "select id, event, data_co, data_h2s, data_o2, data_ch4, created, volt from multiple_mesh_data where device_name = 'xenon2' order by created desc limit 5")
                xenon2_meshes = cursor.fetchall()

            with connection.cursor() as cursor:
                cursor.execute(
                    "select id, event, data_co, data_h2s, data_o2, data_ch4, created, volt from multiple_mesh_data where device_name = 'xenon2' order by created desc limit 5")
                xenon3_meshes = cursor.fetchall()

            with connection.cursor() as cursor:
                cursor.execute(
                    "select id, event, data_co, data_h2s, data_o2, data_ch4, created, volt from multiple_mesh_data where device_name = 'xenon2' order by created desc limit 5")
                xenon4_meshes = cursor.fetchall()

            df_xenon1 = pd.DataFrame(xenon1_meshes)
            df_xenon1.columns = ['id', 'event', 'data_co', 'data_h2s', 'data_o2', 'data_ch4', 'created', 'volt']
            df_xenon1['datetime'] = pd.to_datetime(df_xenon1['created'])
            df_xenon1 = df_xenon1.set_index(pd.DatetimeIndex(df_xenon1['datetime']))

            df_xenon2 = pd.DataFrame(xenon2_meshes)
            df_xenon2.columns = ['id', 'event', 'data_co', 'data_h2s', 'data_o2', 'data_ch4', 'created', 'volt']
            df_xenon2['datetime'] = pd.to_datetime(df_xenon2['created'])
            df_xenon2 = df_xenon2.set_index(pd.DatetimeIndex(df_xenon2['datetime']))

            df_xenon3 = pd.DataFrame(xenon3_meshes)
            df_xenon3.columns = ['id', 'event', 'data_co', 'data_h2s', 'data_o2', 'data_ch4', 'created', 'volt']
            df_xenon3['datetime'] = pd.to_datetime(df_xenon3['created'])
            df_xenon3 = df_xenon3.set_index(pd.DatetimeIndex(df_xenon3['datetime']))

            df_xenon4 = pd.DataFrame(xenon4_meshes)
            df_xenon4.columns = ['id', 'event', 'data_co', 'data_h2s', 'data_o2', 'data_ch4', 'created', 'volt']
            df_xenon4['datetime'] = pd.to_datetime(df_xenon4['created'])
            df_xenon4 = df_xenon4.set_index(pd.DatetimeIndex(df_xenon4['datetime']))

            df_xenon1 = df_xenon1[df_xenon1['datetime'] > '2019-04-25 15:00']
            df_xenon2 = df_xenon2[df_xenon2['datetime'] > '2019-04-25 15:00']
            df_xenon3 = df_xenon3[df_xenon3['datetime'] > '2019-04-25 15:00']
            df_xenon4 = df_xenon4[df_xenon4['datetime'] > '2019-04-25 15:00']

            # For Xenon1
            df_xenon1_co = df_xenon1['data_co'].resample("10s").max().fillna(0)
            df_xenon1_h2s = df_xenon1['data_h2s'].resample("10s").max().fillna(0)
            df_xenon1_o2 = df_xenon1['data_o2'].resample("10s").max().fillna(0)
            df_xenon1_ch4 = df_xenon1['data_ch4'].resample("10s").max().fillna(0)
            df_xenon1_volt = df_xenon1['volt'].resample("10s").max().fillna(0)
            df_xenon1_co = df_xenon1_co.reset_index()
            df_xenon1_h2s = df_xenon1_h2s.reset_index()
            df_xenon1_o2 = df_xenon1_o2.reset_index()
            df_xenon1_ch4 = df_xenon1_ch4.reset_index()
            df_xenon1_volt = df_xenon1_volt.reset_index()

            # For Xenon2
            df_xenon2_co = df_xenon2['data_co'].resample("10s").max().fillna(0)
            df_xenon2_h2s = df_xenon2['data_h2s'].resample("10s").max().fillna(0)
            df_xenon2_o2 = df_xenon2['data_o2'].resample("10s").max().fillna(0)
            df_xenon2_ch4 = df_xenon2['data_ch4'].resample("10s").max().fillna(0)
            df_xenon2_volt = df_xenon2['volt'].resample("10s").max().fillna(0)
            df_xenon2_co = df_xenon2_co.reset_index()
            df_xenon2_h2s = df_xenon2_h2s.reset_index()
            df_xenon2_o2 = df_xenon2_o2.reset_index()
            df_xenon2_ch4 = df_xenon2_ch4.reset_index()
            df_xenon2_volt = df_xenon2_volt.reset_index()

            # For Xenon3
            df_xenon3_co = df_xenon3['data_co'].resample("10s").max().fillna(0)
            df_xenon3_h2s = df_xenon3['data_h2s'].resample("10s").max().fillna(0)
            df_xenon3_o2 = df_xenon3['data_o2'].resample("10s").max().fillna(0)
            df_xenon3_ch4 = df_xenon3['data_ch4'].resample("10s").max().fillna(0)
            df_xenon3_co = df_xenon3_co.reset_index()
            df_xenon3_h2s = df_xenon3_h2s.reset_index()
            df_xenon3_o2 = df_xenon3_o2.reset_index()
            df_xenon3_ch4 = df_xenon3_ch4.reset_index()

            # For Xenon4
            df_xenon4_co = df_xenon4['data_co'].resample("10s").max().fillna(0)
            df_xenon4_h2s = df_xenon4['data_h2s'].resample("10s").max().fillna(0)
            df_xenon4_o2 = df_xenon4['data_o2'].resample("10s").max().fillna(0)
            df_xenon4_ch4 = df_xenon4['data_ch4'].resample("10s").max().fillna(0)
            df_xenon4_co = df_xenon4_co.reset_index()
            df_xenon4_h2s = df_xenon4_h2s.reset_index()
            df_xenon4_o2 = df_xenon4_o2.reset_index()
            df_xenon4_ch4 = df_xenon4_ch4.reset_index()

            # print(df_xenon2_co)

            xenon1_dts = df_xenon1_co['datetime'].tolist()
            xenon2_dts = df_xenon2_co['datetime'].tolist()
            xenon3_dts = df_xenon3_co['datetime'].tolist()
            xenon4_dts = df_xenon4_co['datetime'].tolist()

            xenon1_o2_per = df_xenon1_o2['data_o2'].tolist()[0]*20.9/2400.0
            xenon1_o2_per = round(xenon1_o2_per,1)

            xenon2_o2_per = df_xenon2_o2['data_o2'].tolist()[0]*20.9/2350.0
            xenon2_o2_per = round(xenon2_o2_per,1)

            xenon3_o2_per = df_xenon3_o2['data_o2'].tolist()[0]*20.9/2350.0
            xenon3_o2_per = round(xenon3_o2_per,1)

            xenon4_o2_per = df_xenon4_o2['data_o2'].tolist()[0]*20.9/2350.0
            xenon4_o2_per = round(xenon4_o2_per,1)

            xenon1_co_val = df_xenon4_co['data_co'].tolist()[0]

            xenon1_datetime = str(xenon1_dts[0])[:19]
            xenon2_datetime = str(xenon2_dts[0])[:19]

            if xenon1_co_val < 1900:
                xenon1_co_val = 1900

            co_voff = 1900.0 * 0.0011224
            co_v_diff = 3.3 - co_voff
            xenon1_co_ppm = 1000.0 / co_v_diff * (xenon1_co_val * 0.0011224 - co_voff)

            xenon1_volt = df_xenon1_volt['volt'].tolist()[0]
            xenon2_volt = df_xenon2_volt['volt'].tolist()[0]

            print(xenon1_datetime, xenon2_datetime)

            data = {'xenon1_label': str(xenon1_dts[0])[:19],
                    'xenon1_data_co': int(xenon1_co_ppm), 'xenon1_data_h2s': df_xenon1_h2s['data_h2s'].tolist()[0],
                    'xenon1_data_o2': xenon1_o2_per, 'xenon1_data_ch4': df_xenon1_ch4['data_ch4'].tolist()[0],
                    'xenon1_volt': xenon1_volt, 'xenon1_datetime' : xenon1_datetime,
                    'xenon2_label': str(xenon2_dts[0])[:19],
                    'xenon2_data_co': df_xenon2_co['data_co'].tolist()[0], 'xenon2_data_h2s': df_xenon2_h2s['data_h2s'].tolist()[0],
                    'xenon2_data_o2': xenon2_o2_per, 'xenon2_data_ch4': df_xenon2_ch4['data_ch4'].tolist()[0],
                    'xenon2_volt': xenon2_volt, 'xenon2_datetime' : xenon2_datetime,
                    'xenon3_label': str(xenon3_dts[0])[:19],
                    'xenon3_data_co': df_xenon3_co['data_co'].tolist()[0], 'xenon3_data_h2s': df_xenon3_h2s['data_h2s'].tolist()[0],
                    'xenon3_data_o2': xenon3_o2_per, 'xenon3_data_ch4': df_xenon3_ch4['data_ch4'].tolist()[0],
                    'xenon4_label': str(xenon4_dts[-1])[:19],
                    'xenon4_data_co': df_xenon4_co['data_co'].tolist()[0], 'xenon4_data_h2s': df_xenon4_h2s['data_h2s'].tolist()[0],
                    'xenon4_data_o2': xenon4_o2_per, 'xenon4_data_ch4': df_xenon4_ch4['data_ch4'].tolist()[0],
                    }

            return JsonResponse(data)

class CloudTestTemplateView(TemplateView):
    template_name = 'layouts-preloader.html'

class MapTestview(TemplateView):
    template_name = 'map_view.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        data = CatM1SensorDataMdodel.objects.order_by('-created').values('id', 'device_name', 'created')[:5]
        locs = CatM1LocationMdodel.objects.order_by('-created').values('id', 'device_name', 'latitude', 'longitude', 'created')[:5]

        sensor_data = [ (d['id'], d['device_name'], str(d['created']+datetime.timedelta(hours=9))[:19] ) for d in data ]
        loc_data = [ (l['id'], l['device_name'], l['latitude'], l['longitude'], str(l['created']+datetime.timedelta(hours=9))[:19] ) for l in locs ]

        context['data'] = sensor_data
        context['locations'] = loc_data

        return context
