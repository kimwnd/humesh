# -*- coding: utf-8 -*-

from django.conf.urls import url

from . import views

from django.urls import path

urlpatterns = [
    path('', views.HomePageView.as_view(), name='home'),
    # path('mesh/data/', views.ReceiveMeshDataView.as_view(), name='mesh'),
    path('mesh/data/', views.mesh_notification, name='mesh'),
    path('wifi/data/', views.wifi_notification, name='wifi'),
    path('chart/', views.ChartView.as_view(), name='chart'),
    path('line/chart/', views.LineChartView.as_view(), name='line_chart'),
    path('line/chart/new/', views.NewLineChartView.as_view(), name='line_chart_new'),
    path('wifi/check/', views.WifiCheckChartView.as_view(), name='wifi_check_chart'),
    path('multi/chart/', views.MultiChartView.as_view(), name='multi_chart'),
    path('get/line/data/', views.GetLineDataView.as_view(), name='get_line_data'),
    path('get/mesh/data/', views.GetMeshDataView.as_view(), name='get_mesh_data'),
    path('get/wifi/update/', views.GetWifiDataUpdateView.as_view(), name='get_wifi_data_update'),
    path('control/led/', views.ControlLEDView.as_view(), name='control_led'),
    path('control/switch/', views.ControlSwitchView.as_view(), name='control_switch'),
]