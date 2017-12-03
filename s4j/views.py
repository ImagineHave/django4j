'''
Created on 26 Aug 2017

@author: Christopher Williams
'''
import nltk, string, threading, gc, ast, logging, time, random
from s4j.serializers import *
from s4j.models import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from random import randint
from sklearn.feature_extraction.text import TfidfVectorizer
from django.utils.six import BytesIO
from rest_framework.parsers import JSONParser
from nltk.corpus import stopwords
from django.http import HttpResponse
from s4j.tools import *

logging.basicConfig(level=logging.DEBUG,
                    format='(%(threadName)-10s) %(message)s',
                    )
    
class PrayerView(APIView):
    
    def post(self, request, format=None):
        nltk.download('stopwords')
        stopwords.ensure_loaded()
        print("prayer request")
        serializer = PrayerSerializer(data=request.data)
        if serializer.is_valid():
            print("prayer: " + request.data.get("prayer"))
            
            if PrayerModel.objects.filter(prayer=request.data.get("prayer")).exists():
                prayerModel = PrayerModel.objects.filter(prayer=request.data.get("prayer"), rank=1).first()
                serializer = PrayerSerializer(prayerModel)
                print("Already saved :")
                return Response(serializer.data, status=status.HTTP_200_OK)
            
            stemmed = processWords(request.data.get("prayer"))
            answers = []
            
            for word in tokenize(stemmed):
                answers = answers + list(AnswerModel.objects.filter(words=word))
                
            if len(answers) == 0:
                print("No words in database returning random answer")
                answers = list(AnswerModel.objects.all())
                x = 0
                while x <= 99:
                    randomAnswer = random.choice(answers)
                    if PrayerModel.objects.filter(answer=randomAnswer).exists():
                        pass
                    else:
                        prayerModel = PrayerModel.objects.create(prayer=request.data.get("prayer"), rank=x, answer=randomAnswer)
                        x += 1
                
                prayerModel = PrayerModel.objects.filter(prayer=request.data.get("prayer"), rank=1).first()
                answer = prayerModel.answers.first()
                serializer = PrayerSerializer(prayerModel)
                return Response(serializer.data, status=status.HTTP_200_OK)
              
            print("Processing non unique " + str(len(answers)) + " answers")  
                
            answers = list(set(answers))
                
            print("Processing unique " + str(len(answers)) + " answers")
            
            ranked = []
            for answer in answers:
                ranked.append(RankAnswer(stemmed, answer))
                
            ranked.sort(key=lambda x: x.rank, reverse=True)
            
            #get top 100
            x = len(ranked)
            i = 0
            p = 0
            while i <= x && p <= 100:
                rank = ranked[i]
                if PrayerModel.objects.filter(amswer=rank.getAnswer()).exists():
                    i+=1
                else:
                    prayerModel = PrayerModel.objects.create(prayer=request.data.get("prayer"), rank=i, answer=rank.getAnswer())
                    p+=1
                    i+=1
                
            
            prayerModel = PrayerModel.objects.filter(prayer=request.data.get("prayer"), rank=1).first()
            serializer = PrayerSerializer(prayerModel)
            gc.enable()
            return Response(serializer.data, status=status.HTTP_200_OK)
            
def w2a(request):
    
    output = ""
    for word in list(WordModel.objects.all()):
        answers = list(AnswerModel.objects.filter(words=word))
        output += word.word + ":" + str(len(answers)) + '<br>'
    
    return HttpResponse(output)