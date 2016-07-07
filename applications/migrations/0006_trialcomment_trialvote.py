# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0011_auto_20160426_0238'),
        ('applications', '0005_auto_20160124_2258'),
    ]

    operations = [
        migrations.CreateModel(
            name='TrialComment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('text', models.CharField(max_length=800)),
                ('author', models.ForeignKey(to='core.UserProfile')),
                ('trial_member', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='TrialVote',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('approve', models.BooleanField()),
                ('trial_member', models.ForeignKey(related_name='trial_votes_received', to=settings.AUTH_USER_MODEL)),
                ('voter', models.ForeignKey(related_name='trial_votes_given', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
