# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-11 02:41
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0007_auto_20170311_0109'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='tokens',
            field=models.ManyToManyField(through='books.Posting', to='books.Token'),
        ),
    ]
