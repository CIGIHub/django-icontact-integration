# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('icontact', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='contact',
            name='known_internal_person',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='campaign',
            name='from_email',
            field=models.EmailField(max_length=254),
        ),
        migrations.AlterField(
            model_name='contact',
            name='email',
            field=models.EmailField(max_length=254),
        ),
    ]
