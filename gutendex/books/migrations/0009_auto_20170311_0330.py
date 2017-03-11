# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-11 03:30
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0008_book_tokens'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='correlation_sim',
            field=models.ManyToManyField(related_name='_book_correlation_sim_+', through='books.Correlation', to='books.Book'),
        ),
        migrations.AlterField(
            model_name='book',
            name='euclidian_sim',
            field=models.ManyToManyField(related_name='_book_euclidian_sim_+', through='books.Euclidean', to='books.Book'),
        ),
    ]