# -*- coding: utf-8 -*-
from django.db import models
from django.utils import timezone

class MeshDataModel(models.Model):
    event = models.CharField(max_length=255, null=False, blank=False, verbose_name='event name')
    data = models.IntegerField(null=False, blank=False, verbose_name='데이터')
    created = models.DateTimeField(default=timezone.now, verbose_name='등록일자')
    coreid = models.CharField(max_length=255, null=False, blank=False, verbose_name='coreid')
    device_name = models.CharField(max_length=255, null=False, blank=False, verbose_name='coreid')

class WifiDataModel(models.Model):
    temp = models.IntegerField(null=False, blank=False, verbose_name='데이터')
    created = models.DateTimeField(default=timezone.now, verbose_name='등록일자')


class MultipleMeshDataMdodel(models.Model):
    event = models.CharField(max_length=255, null=False, blank=False, verbose_name='event name')
    device_name = models.CharField(max_length=255, null=False, blank=False, verbose_name='device name')
    data_co = models.IntegerField(null=False, blank=False, verbose_name='Co 가스 데이터')
    data_h2s = models.IntegerField(null=False, blank=False, verbose_name='H2S 가스 데이터')
    data_o2 = models.IntegerField(null=False, blank=False, verbose_name='O2 가스 데이터')
    data_ch4 = models.IntegerField(null=False, blank=False, verbose_name='CH4 가스 데이터')
    doc_name = models.CharField(max_length=128, null=False, blank=False, verbose_name='도크명')
    ship_name = models.CharField(max_length=128, null=False, blank=False, verbose_name='선박명')
    set_no = models.CharField(max_length=128, null=False, blank=False, verbose_name='세트순번')
    location = models.CharField(max_length=128, null=False, blank=False, verbose_name='설치위치')
    node_no = models.CharField(max_length=128, null=False, blank=False, verbose_name='노드순번')
    created = models.DateTimeField(default=timezone.now, verbose_name='등록일자')
    coreid = models.CharField(max_length=128, null=False, blank=False, verbose_name='coreid')

    class Meta:
        db_table = 'multiple_mesh_data'

    def __str__(self):
        return self.event


