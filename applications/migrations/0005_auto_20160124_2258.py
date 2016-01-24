# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0004_auto_20151027_0011'),
    ]

    operations = [
        migrations.AlterField(
            model_name='answer',
            name='text',
            field=models.TextField(),
        ),
    ]
