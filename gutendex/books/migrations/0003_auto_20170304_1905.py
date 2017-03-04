# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-04 19:05
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0002_book_text'),
    ]

    operations = [
        migrations.CreateModel(
            name='Posting',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tf', models.PositiveIntegerField()),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='books.Book')),
            ],
        ),
        migrations.CreateModel(
            name='Token',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64, unique=True)),
                ('df', models.PositiveIntegerField()),
                ('total_occurances', models.PositiveIntegerField()),
            ],
        ),
        migrations.AddField(
            model_name='posting',
            name='token',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='books.Token'),
        ),
    ]
