# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-10-14 10:08
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('s4j', '0009_auto_20171014_1007'),
    ]

    operations = [
        migrations.RenameField(
            model_name='bookmodel',
            old_name='genre',
            new_name='genreNumber',
        ),
    ]