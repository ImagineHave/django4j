# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-10-13 21:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('s4j', '0003_auto_20170826_2350'),
    ]

    operations = [
        migrations.CreateModel(
            name='AnswerModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('genre', models.TextField()),
                ('genreNumber', models.IntegerField()),
                ('book', models.TextField()),
                ('bookNumber', models.IntegerField()),
                ('chapter', models.IntegerField()),
                ('verse', models.IntegerField()),
                ('passage', models.TextField()),
                ('processed', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='BookModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('book', models.TextField()),
                ('bookNumber', models.IntegerField()),
                ('genre', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='GenreModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('genre', models.TextField()),
                ('genreNumber', models.TextField()),
            ],
        ),
        migrations.AlterModelOptions(
            name='fieldmodel',
            options={},
        ),
    ]