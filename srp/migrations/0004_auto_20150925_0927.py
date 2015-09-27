# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_auto_20150925_0927'),
        ('srp', '0003_auto_20150311_0600'),
    ]

    operations = [
        migrations.CreateModel(
            name='SRPComment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('text', models.CharField(max_length=800)),
                ('author', models.ForeignKey(to='core.UserProfile')),
            ],
        ),
        migrations.AddField(
            model_name='srprequest',
            name='time',
            field=models.DateTimeField(default=datetime.datetime(2015, 9, 25, 9, 27, 13, 622884, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='srprequest',
            name='value',
            field=models.BigIntegerField(null=True),
        ),
        migrations.AddField(
            model_name='srpcomment',
            name='request',
            field=models.ForeignKey(to='srp.SRPRequest'),
        ),
    ]
