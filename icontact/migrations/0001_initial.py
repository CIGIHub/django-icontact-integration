# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=20)),
                ('base_url', models.URLField()),
                ('username', models.CharField(max_length=50)),
                ('password', models.CharField(max_length=50)),
                ('app_id', models.CharField(max_length=200)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Action',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('action_type', models.CharField(max_length=50, null=True, blank=True)),
                ('action_time', models.CharField(max_length=50)),
                ('actor', models.CharField(max_length=50)),
                ('details', models.TextField(null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Campaign',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('campaign_id', models.IntegerField()),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(null=True, blank=True)),
                ('from_email', models.EmailField(max_length=75)),
                ('from_name', models.TextField()),
                ('forward_to_friend', models.IntegerField(default=0)),
                ('subscription_management', models.IntegerField(default=0)),
                ('click_track_mode', models.IntegerField(default=1)),
                ('use_account_address', models.IntegerField(default=0)),
                ('archive_by_default', models.IntegerField(default=1)),
                ('street', models.CharField(max_length=1024, null=True, blank=True)),
                ('city', models.CharField(max_length=255, null=True, blank=True)),
                ('state', models.CharField(max_length=255, null=True, blank=True)),
                ('zip', models.CharField(max_length=20, null=True, blank=True)),
                ('country', models.CharField(max_length=255, null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('contact_id', models.CharField(max_length=50)),
                ('first_name', models.CharField(max_length=255, null=True, blank=True)),
                ('last_name', models.CharField(max_length=255, null=True, blank=True)),
                ('email', models.EmailField(max_length=75)),
                ('status', models.CharField(max_length=30)),
                ('history_last_updated', models.DateTimeField(null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='List',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('list_id', models.IntegerField()),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(null=True, blank=True)),
                ('public_name', models.CharField(max_length=255, null=True, blank=True)),
                ('email_owner_on_change', models.IntegerField(default=1)),
                ('welcome_on_manual_add', models.IntegerField(default=0)),
                ('welcome_on_signup_add', models.IntegerField(default=0)),
                ('welcome_message_id', models.IntegerField(null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('message_id', models.IntegerField()),
                ('message_name', models.CharField(max_length=1024, null=True, blank=True)),
                ('message_type', models.CharField(max_length=25, null=True, blank=True)),
                ('subject', models.TextField(null=True, blank=True)),
                ('html_body', models.TextField(null=True, blank=True)),
                ('text_body', models.TextField(null=True, blank=True)),
                ('create_date', models.CharField(max_length=30, null=True, blank=True)),
                ('clicks_last_updated', models.DateTimeField(null=True, blank=True)),
                ('campaign', models.ForeignKey(blank=True, to='icontact_backup.Campaign', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MessageClick',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('unmatched_contact_id', models.IntegerField(null=True, blank=True)),
                ('click_time', models.CharField(max_length=30)),
                ('click_link', models.TextField()),
                ('contact', models.ForeignKey(blank=True, to='icontact_backup.Contact', null=True)),
                ('message', models.ForeignKey(to='icontact_backup.Message')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Offset',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('data_type', models.CharField(max_length=25)),
                ('offset', models.IntegerField(default=0)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Send',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('send_id', models.IntegerField()),
                ('recipient_count', models.IntegerField(null=True, blank=True)),
                ('status', models.CharField(max_length=25, null=True, blank=True)),
                ('released_time', models.CharField(max_length=50, null=True, blank=True)),
                ('list', models.ForeignKey(to='icontact_backup.List')),
                ('message', models.ForeignKey(to='icontact_backup.Message')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.CharField(max_length=30)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('contact', models.ForeignKey(to='icontact_backup.Contact')),
                ('list', models.ForeignKey(to='icontact_backup.List')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='action',
            name='contact',
            field=models.ForeignKey(to='icontact_backup.Contact'),
            preserve_default=True,
        ),
    ]
