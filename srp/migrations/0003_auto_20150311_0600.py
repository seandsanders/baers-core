# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('srp', '0002_auto_20150306_0220'),
    ]

    operations = [
        migrations.AddField(
            model_name='srprequest',
            name='corp',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='srprequest',
            name='pilot',
            field=models.CharField(max_length=100, null=True),
        ),
    ]
