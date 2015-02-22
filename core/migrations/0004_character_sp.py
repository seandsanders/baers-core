# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_auto_20150126_0025'),
    ]

    operations = [
        migrations.AddField(
            model_name='character',
            name='sp',
            field=models.IntegerField(null=True),
        ),
    ]
