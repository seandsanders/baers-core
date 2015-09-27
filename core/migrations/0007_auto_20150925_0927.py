# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_auto_20150305_0118'),
    ]

    operations = [
        migrations.CreateModel(
            name='CCPinvType',
            fields=[
                ('typeID', models.IntegerField(serialize=False, primary_key=True)),
                ('typeName', models.CharField(max_length=100)),
            ],
            options={
                'db_table': 'invTypes',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='AccountingEntry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField()),
                ('balance', models.BigIntegerField()),
                ('name', models.CharField(max_length=15)),
            ],
        ),
        migrations.CreateModel(
            name='CorpAsset',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('itemID', models.BigIntegerField()),
                ('locationID', models.IntegerField()),
                ('typeID', models.IntegerField()),
                ('quantity', models.IntegerField()),
                ('flag', models.IntegerField()),
                ('singleton', models.IntegerField()),
                ('rawQuantity', models.IntegerField(null=True)),
                ('parentID', models.BigIntegerField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Haiku',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('author', models.CharField(max_length=100)),
                ('text', models.CharField(max_length=1000)),
            ],
        ),
        migrations.CreateModel(
            name='StarbaseNote',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('starbaseID', models.BigIntegerField()),
                ('note', models.CharField(max_length=1000)),
            ],
        ),
        migrations.CreateModel(
            name='StarbaseOwner',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('starbaseID', models.BigIntegerField()),
            ],
        ),
        migrations.AddField(
            model_name='characterasset',
            name='parentID',
            field=models.BigIntegerField(null=True),
        ),
        migrations.AddField(
            model_name='corpmember',
            name='altCorp',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='corpmember',
            name='shipType',
            field=models.CharField(default=1, max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='corpstarbase',
            name='altCorp',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='mentor',
            field=models.ForeignKey(to='core.UserProfile', null=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='theme',
            field=models.CharField(default=b'Flatly', max_length=15),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='tzoffset',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='character',
            name='walletBalance',
            field=models.BigIntegerField(null=True),
        ),
        migrations.AddField(
            model_name='starbaseowner',
            name='owner',
            field=models.ForeignKey(to='core.UserProfile', null=True),
        ),
    ]
