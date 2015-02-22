# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='character',
            name='activeShip',
        ),
        migrations.AddField(
            model_name='character',
            name='activeShipName',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='character',
            name='activeShipTypeName',
            field=models.CharField(max_length=100, null=True),
        ),
    ]
