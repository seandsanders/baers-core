# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_auto_20150927_1906'),
    ]

    operations = [
        migrations.CreateModel(
            name='CCPinvFlags',
            fields=[
                ('flagID', models.IntegerField(serialize=False, primary_key=True)),
                ('flagName', models.TextField()),
            ],
            options={
                'db_table': 'invFlags',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='CCPmapDenormalize',
            fields=[
                ('itemID', models.IntegerField(serialize=False, primary_key=True)),
                ('itemName', models.TextField()),
            ],
            options={
                'db_table': 'mapDenormalize',
                'managed': False,
            },
        ),
    ]
