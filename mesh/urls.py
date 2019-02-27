# -*- coding: utf-8 -*-

from django.conf.urls import url

from . import views

from django.urls import path

urlpatterns = [
    path('', views.HomePageView.as_view(), name='home'),
    path('mesh/data/', views.ReceiveMeshDataView.as_view(), name='mesh'),
]