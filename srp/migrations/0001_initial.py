# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_auto_20150305_0118'),
    ]

    operations = [
        migrations.CreateModel(
            name='SRPRequest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('killID', models.IntegerField()),
                ('fc', models.CharField(max_length=100)),
                ('aar', models.CharField(max_length=1000)),
                ('learned', models.CharField(max_length=1000)),
                ('suggestions', models.CharField(max_length=1000)),
                ('value', models.IntegerField(null=True)),
                ('ship', models.CharField(max_length=100)),
                ('shipID', models.IntegerField(null=True)),
                ('status', models.IntegerField(default=0, choices=[(0, b'Pending'), (1, b'Approved'), (2, b'Denied')])),
                ('approver', models.ForeignKey(related_name='approvedsrps', to='core.UserProfile')),
                ('owner', models.ForeignKey(to='core.UserProfile')),
            ],
        ),
    ]
