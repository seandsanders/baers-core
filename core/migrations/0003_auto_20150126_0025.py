# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20150126_0024'),
    ]

    operations = [
        migrations.AlterField(
            model_name='character',
            name='location',
            field=models.CharField(max_length=200, null=True),
        ),
    ]
