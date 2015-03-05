# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_apikey_lastrefresh'),
    ]

    operations = [
        migrations.AlterField(
            model_name='apikey',
            name='lastRefresh',
            field=models.DateTimeField(default=datetime.datetime(1900, 1, 1, 0, 0)),
        ),
        migrations.AlterField(
            model_name='characterasset',
            name='itemID',
            field=models.BigIntegerField(),
        ),
        migrations.AlterField(
            model_name='charactercontract',
            name='contractID',
            field=models.BigIntegerField(),
        ),
        migrations.AlterField(
            model_name='charactermarketorder',
            name='orderID',
            field=models.BigIntegerField(),
        ),
        migrations.AlterField(
            model_name='characternotification',
            name='notificationID',
            field=models.BigIntegerField(),
        ),
        migrations.AlterField(
            model_name='contractitem',
            name='recordID',
            field=models.BigIntegerField(),
        ),
        migrations.AlterField(
            model_name='corpmember',
            name='roles',
            field=models.BigIntegerField(),
        ),
        migrations.AlterField(
            model_name='corpstarbase',
            name='itemID',
            field=models.BigIntegerField(),
        ),
        migrations.AlterField(
            model_name='notificationtext',
            name='notificationID',
            field=models.BigIntegerField(),
        ),
        migrations.AlterField(
            model_name='walletjournal',
            name='refID',
            field=models.BigIntegerField(),
        ),
        migrations.AlterField(
            model_name='wallettransactions',
            name='journalTransactionID',
            field=models.BigIntegerField(),
        ),
        migrations.AlterField(
            model_name='wallettransactions',
            name='transactionID',
            field=models.BigIntegerField(),
        ),
    ]
