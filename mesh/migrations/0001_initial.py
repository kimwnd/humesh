# Generated by Django 2.1 on 2019-02-27 12:38

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MeshDataModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event', models.CharField(max_length=255, verbose_name='event name')),
                ('data', models.IntegerField(verbose_name='데이터')),
                ('created', models.DateTimeField(default=django.utils.timezone.now, verbose_name='등록일자')),
                ('coreid', models.CharField(max_length=255, verbose_name='coreid')),
                ('device_name', models.CharField(max_length=255, verbose_name='coreid')),
            ],
        ),
    ]
