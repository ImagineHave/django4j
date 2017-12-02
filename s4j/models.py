'''
Created on 26 Aug 2017

@author: Christopher Williams
'''
from django.db import models

class WordModel(models.Model):
    word = models.TextField(primary_key=True)
    
    def __str__(self): 
        return self.word
        
    class Meta:
        ordering = ('created',)
        
class AnswerModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    genre = models.TextField()
    genreNumber = models.IntegerField()
    book = models.TextField()
    bookNumber = models.IntegerField()
    chapter = models.IntegerField()
    verse = models.IntegerField()
    passage = models.TextField()
    processed = models.TextField(primary_key=True)
    words = models.ManyToManyField(WordModel, related_name='answers')
    
    def __str__(self): 
        return self.passage
    
class PrayerModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    prayer = models.TextField()
    answer = models.OneToOneField(AnswerModel,)
    
    class Meta:
        ordering = ('created',)
    
class FieldModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    book = models.IntegerField()
    chapter = models.IntegerField()
    verse = models.IntegerField()
    passage = models.TextField()
    bibleName = models.TextField(default="boo hoo I am not set")
    
    def __str__(self): 
        return self.passage
    
class GenreModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    genre = models.TextField()
    genreNumber = models.IntegerField()
    
class BookModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    book = models.TextField()
    bookNumber = models.IntegerField()
    genreNumber = models.IntegerField()
    
class BibleModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    name = models.TextField()
