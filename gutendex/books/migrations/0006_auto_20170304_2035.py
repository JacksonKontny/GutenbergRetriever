# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-04 20:35
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0005_auto_20170304_1953'),
    ]

    operations = [
        migrations.AlterField(
            model_name='token',
            name='name',
            field=models.CharField(max_length=128, unique=True),
        ),
    ]
