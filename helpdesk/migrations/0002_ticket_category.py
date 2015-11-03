# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('helpdesk', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='ticket',
            name='category',
            field=models.IntegerField(default=0, choices=[(0, b'Request'), (1, b'Feedback')]),
        ),
    ]
