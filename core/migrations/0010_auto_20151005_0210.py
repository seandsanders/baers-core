# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_ccpinvflags_ccpmapdenormalize'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='theme',
            field=models.CharField(default=b'flatly', max_length=15),
        ),
    ]
