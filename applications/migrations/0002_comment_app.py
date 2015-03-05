# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='app',
            field=models.ForeignKey(default=0, to='applications.Application'),
            preserve_default=False,
        ),
    ]
