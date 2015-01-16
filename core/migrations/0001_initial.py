# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0005_alter_user_last_login_null'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ApiKey',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('keyID', models.IntegerField()),
                ('vCode', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Character',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('charID', models.IntegerField()),
                ('charName', models.CharField(max_length=200)),
                ('corpID', models.IntegerField()),
                ('corpName', models.CharField(max_length=200)),
                ('corpTicker', models.CharField(max_length=6)),
                ('allianceID', models.IntegerField()),
                ('allianceName', models.CharField(max_length=200)),
                ('allianceTicker', models.CharField(max_length=6)),
                ('api', models.ForeignKey(to='core.ApiKey')),
            ],
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('content', models.CharField(max_length=200)),
                ('targetGroup', models.ManyToManyField(to='auth.Group')),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('mainChar', models.IntegerField()),
                ('squad', models.IntegerField()),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='notification',
            name='targetUsers',
            field=models.ManyToManyField(to='core.UserProfile'),
        ),
        migrations.AddField(
            model_name='character',
            name='profile',
            field=models.ForeignKey(to='core.UserProfile'),
        ),
        migrations.AddField(
            model_name='apikey',
            name='profile',
            field=models.ForeignKey(to='core.UserProfile'),
        ),
    ]
