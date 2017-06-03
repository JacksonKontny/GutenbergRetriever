# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-06-03 01:31
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0023_sentence'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cluster',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('n_clusters', models.SmallIntegerField()),
                ('n', models.SmallIntegerField()),
                ('clustered_on', models.CharField(max_length=64)),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='books.Book')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='cluster',
            unique_together=set([('book', 'n_clusters', 'clustered_on')]),
        ),
    ]
