# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0002_comment_app'),
    ]

    operations = [
        migrations.CreateModel(
            name='DoctrineShip',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('shipID', models.IntegerField()),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='DoctrineShipGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='ShipRequiredSkill',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('skillID', models.BigIntegerField()),
                ('level', models.BigIntegerField()),
                ('ship', models.ForeignKey(to='applications.DoctrineShip')),
            ],
        ),
        migrations.AddField(
            model_name='doctrineship',
            name='group',
            field=models.ForeignKey(to='applications.DoctrineShipGroup'),
        ),
    ]
