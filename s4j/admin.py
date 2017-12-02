import nltk, string, threading, gc, ast, logging, time
from s4j import serializers
from s4j.models import *
from django.contrib import admin
from nltk.corpus import stopwords
from rest_framework.parsers import JSONParser
from django.utils.six import BytesIO
from django.conf.urls import url
from django.contrib.admin import AdminSite
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from s4j.loaders import BibleLoader

def load(request):
    print "for fucks sake"

class AnswerModelAdmin(admin.ModelAdmin):
    list_display = ['bookNumber', 'chapter', 'verse', 'passage']
    ordering = ['bookNumber', 'chapter', 'verse']

    def get_urls(self):
        urls = super(AnswerModelAdmin, self).get_urls()
        my_urls = [
            url(r'^load/$', self.admin_site.admin_view(self.load))
        ]
        return my_urls + urls

    def load(self, request):
        messages.success(request, 'Loading up the bible...')
        bibleLoader = BibleLoader()
        thread = threading.Thread(target=bibleLoader.process, args=())
        thread.daemon = True                            # Daemonize thread
        thread.start()                                  # Start the execution
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        
    

admin.site.register(AnswerModel, AnswerModelAdmin)
admin.site.register(WordModel)
admin.site.register(PrayerModel)
admin.site.register(FieldModel)