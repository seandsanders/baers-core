# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_auto_20150126_0025'),
    ]

    operations = [
        migrations.CreateModel(
            name='Answer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('question', models.CharField(max_length=500)),
                ('text', models.CharField(max_length=1000)),
            ],
        ),
        migrations.CreateModel(
            name='Application',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.IntegerField(default=0, choices=[(0, b'Offered'), (1, b'Unprocessed'), (2, b'Accepted'), (3, b'On Hold'), (4, b'Denied')])),
                ('tag', models.IntegerField(default=0, choices=[(0, b'New Application'), (1, b'Review Requested: Looks Clean'), (2, b'Review Requested: Looks Suspicious'), (3, b'Action Requested: Interview'), (4, b'Action Requested: Rush'), (5, b'Waiting: Skills'), (6, b'In Progress: See notes'), (7, b'Completed: Spai, Awox Plz'), (8, b'Completed: See Status')])),
                ('applicationDate', models.DateTimeField(null=True)),
                ('timezone', models.IntegerField(null=True, choices=[(0, b'US (00:00-08:00 GMT)'), (1, b'AU (08:00-16:00 GMT)'), (2, b'EU (16:00-24:00 GMT)')])),
                ('applicantName', models.CharField(max_length=100, null=True)),
                ('token', models.CharField(max_length=20, null=True)),
                ('applicantProfile', models.OneToOneField(null=True, to='core.UserProfile')),
            ],
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField()),
                ('text', models.CharField(max_length=1000)),
                ('auto_generated', models.BooleanField(default=False)),
                ('author', models.ForeignKey(to='core.UserProfile')),
            ],
        ),
        migrations.AddField(
            model_name='answer',
            name='app',
            field=models.ForeignKey(to='applications.Application'),
        ),
    ]
