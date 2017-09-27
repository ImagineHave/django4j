'''
Created on 26 Aug 2017

@author: Christopher Williams
'''
from django.db import models

    
class PrayerModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    prayer = models.TextField()
    
    class Meta:
        ordering = ('created',)
    
class FieldModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    book = models.IntegerField()
    chapter = models.IntegerField()
    verse = models.IntegerField()
    passage = models.TextField()
    
        
class BibleModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
