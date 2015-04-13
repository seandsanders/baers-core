# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('srp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='srprequest',
            name='approver',
            field=models.ForeignKey(related_name='approvedsrps', to='core.UserProfile', null=True),
        ),
        migrations.AlterField(
            model_name='srprequest',
            name='ship',
            field=models.CharField(max_length=100, null=True),
        ),
    ]
