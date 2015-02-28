# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_character_sp'),
    ]

    operations = [
        migrations.AddField(
            model_name='apikey',
            name='lastRefresh',
            field=models.DateTimeField(null=True),
        ),
    ]
