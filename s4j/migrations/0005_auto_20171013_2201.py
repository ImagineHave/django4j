# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-10-13 22:01
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('s4j', '0004_auto_20171013_2127'),
    ]

    operations = [
        migrations.AlterField(
            model_name='genremodel',
            name='genre',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='genremodel',
            name='genreNumber',
            field=models.CharField(max_length=100),
        ),
    ]