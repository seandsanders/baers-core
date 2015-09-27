# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_auto_20150925_0927'),
    ]

    operations = [
        migrations.CreateModel(
            name='RedditAccount',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('owner', models.OneToOneField(null=True, to='core.UserProfile')),
            ],
        ),
    ]
