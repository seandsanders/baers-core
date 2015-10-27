# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0003_auto_20150929_0349'),
    ]

    operations = [
        migrations.AlterField(
            model_name='doctrineship',
            name='group',
            field=models.ForeignKey(related_name='doctrineships', to='applications.DoctrineShipGroup'),
        ),
        migrations.AlterField(
            model_name='shiprequiredskill',
            name='ship',
            field=models.ForeignKey(related_name='skills', to='applications.DoctrineShip'),
        ),
    ]
