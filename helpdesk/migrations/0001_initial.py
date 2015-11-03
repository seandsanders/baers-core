# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_auto_20151005_0210'),
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField()),
                ('text', models.CharField(max_length=5000)),
                ('auto_generated', models.BooleanField(default=False)),
                ('private', models.BooleanField()),
                ('author', models.ForeignKey(related_name='ticketcomment', to='core.UserProfile')),
            ],
        ),
        migrations.CreateModel(
            name='Ticket',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=200)),
                ('text', models.CharField(max_length=10000)),
                ('token', models.CharField(max_length=8)),
                ('status', models.IntegerField(default=0, choices=[(0, b'New'), (1, b'In Progress'), (2, b'Resolved')])),
                ('author', models.ForeignKey(to='core.UserProfile', null=True)),
            ],
        ),
        migrations.AddField(
            model_name='comment',
            name='ticket',
            field=models.ForeignKey(to='helpdesk.Ticket'),
        ),
    ]
