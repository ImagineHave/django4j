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
    bibleName = models.TextField(default="boo hoo I am not set")
    
class GenreModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    genre = models.TextField()
    genreNumber = models.IntegerField()
    
class BookModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    book = models.TextField()
    bookNumber = models.IntegerField()
    genreNumber = models.IntegerField()

class WordModel(models.Model):
    word = models.TextField(primary_key=True)

class AnswerModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    genre = models.TextField()
    genreNumber = models.IntegerField()
    book = models.TextField()
    bookNumber = models.IntegerField()
    chapter = models.IntegerField()
    verse = models.IntegerField()
    passage = models.TextField()
    processed = models.TextField()
    word = models.ForeignKey(WordModel,)
    
    def __str__(self): 
        return self.passage
    
class BibleModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    name = models.TextField()
