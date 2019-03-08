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