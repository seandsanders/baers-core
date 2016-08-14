# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0006_trialcomment_trialvote'),
    ]

    operations = [
        migrations.CreateModel(
            name='DoctrineShipGroupRequiredSkill',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('skillID', models.BigIntegerField()),
                ('level', models.BigIntegerField()),
                ('group', models.ForeignKey(to='applications.DoctrineShipGroup')),
            ],
        ),
        migrations.AlterField(
            model_name='trialvote',
            name='approve',
            field=models.BooleanField(default=False),
        ),
    ]
