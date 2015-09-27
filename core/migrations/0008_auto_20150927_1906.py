# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_auto_20150925_0927'),
    ]

    operations = [
        migrations.AlterField(
            model_name='charactermail',
            name='toCharacterIDs',
            field=models.CharField(max_length=1000),
        ),
        migrations.AlterField(
            model_name='charactermail',
            name='toCorpOrAllianceID',
            field=models.CharField(max_length=1000),
        ),
        migrations.AlterField(
            model_name='charactermail',
            name='toListID',
            field=models.CharField(max_length=1000),
        ),
        migrations.AlterField(
            model_name='walletjournal',
            name='argName1',
            field=models.CharField(max_length=100),
        ),
    ]
