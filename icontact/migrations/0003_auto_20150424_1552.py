# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('icontact', '0002_auto_20150423_1938'),
    ]

    operations = [
        migrations.CreateModel(
            name='SpamCheck',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('raw_score', models.FloatField(default=0.0)),
            ],
        ),
        migrations.CreateModel(
            name='SpamCheckDetail',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('score', models.FloatField(default=0.0)),
                ('name', models.TextField(null=True, blank=True)),
                ('description', models.TextField(null=True, blank=True)),
                ('spam_check', models.ForeignKey(to='icontact.SpamCheck')),
            ],
        ),
        migrations.CreateModel(
            name='Statistics',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('bounces', models.IntegerField(default=0)),
                ('delivered', models.IntegerField(default=0)),
                ('unsubscribes', models.IntegerField(default=0)),
                ('unique_opens', models.IntegerField(default=0)),
                ('total_opens', models.IntegerField(default=0)),
                ('unique_clicks', models.IntegerField(default=0)),
                ('total_clicks', models.IntegerField(default=0)),
                ('forwards', models.IntegerField(default=0)),
                ('comments', models.IntegerField(default=0)),
                ('complaints', models.IntegerField(default=0)),
            ],
        ),
        migrations.AddField(
            model_name='message',
            name='statistics_last_updated',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='messageclick',
            name='click_link',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='statistics',
            name='message',
            field=models.ForeignKey(to='icontact.Message'),
        ),
        migrations.AddField(
            model_name='message',
            name='spam_check',
            field=models.ForeignKey(blank=True, to='icontact.SpamCheck', null=True),
        ),
    ]
