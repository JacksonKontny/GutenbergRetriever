# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-04 19:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0004_book_is_parsed'),
    ]

    operations = [
        migrations.AlterField(
            model_name='posting',
            name='tf',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='token',
            name='df',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='token',
            name='total_occurances',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
