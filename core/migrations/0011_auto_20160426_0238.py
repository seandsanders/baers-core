# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_auto_20151005_0210'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='targetUsers',
            field=models.ManyToManyField(related_name='core_notifications', to=settings.AUTH_USER_MODEL),
        ),
    ]
