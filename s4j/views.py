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
        stopwords.ensure_loaded()
        print("prayer request")
        serializer = PrayerSerializer(data=request.data)
        if serializer.is_valid():
            print("prayer: " + request.data.get("prayer"))
            
            if PrayerModel.objects.filter(prayer=request.data.get("prayer")).exists():
                prayerModel = PrayerModel.objects.filter(prayer=request.data.get("prayer")).first()
                serializer = PrayerSerializer(prayerModel)
                print("Already saved")
                gc.enable()
                return Response(serializer.data, status=status.HTTP_200_OK)
            
            
            stemmed = processWords(request.data.get("prayer"))
            
            words = []
            answers = []
            
            for word in tokenize(stemmed):
                answers = answers + (list(set(AnswerModel.objects.filter(words=word))))
            
            if len(answers) == 0:
                print("Returning random answer")
                answers = list(AnswerModel.objects.all())
                randomAnswer = random.choice(answers)
                prayerModel = PrayerModel.objects.create(prayer=request.data.get("prayer"), answer=randomAnswer)
                serializer = PrayerSerializer(prayerModel)
                return Response(serializer.data, status=status.HTTP_200_OK)
                
                
            print("Processing " + str(len(answers)) + " answers")
            
            ranked = []
            for answer in answers:
                ranked.append(RankAnswer(stemmed, answer))
                
            ranked.sort(key=lambda x: x.rank, reverse=True)
            
            #get top 1000
            ranked = ranked[0:1000]
            
            answers = []
            for rank in ranked:
                answer = rank.getAnswer()
                answers.append(answer)
            
            print("Processing " + str(len(answers)) + " answers")
            serializer = AnswerSerializer(ranked[0].getAnswer())
            #return Response(serializer.data, status=status.HTTP_200_OK)
            
            ts = 10
            if len(answers) == 1:
                ts = 1
            
            if ts > len(answers):
                ts = len(answers)/2
                
            chunk = len(answers)/ts
            threads = []
            bestMatch = BestMatch()
            for i in range(ts):
                j = i + 1
                t = threading.Thread(target=worker, args=(answers, stemmed, i*chunk, j*chunk, bestMatch,))
                t.daemon = True  
                threads.append(t)
                t.start()
        
            print(str(ts) + " threads processing")
            
            for t in threads:
                t.join()
            
            prayerModel = PrayerModel.objects.create(prayer=request.data.get("prayer"), answer=bestMatch.bestMatch)
            serializer = PrayerSerializer(prayerModel)
            print(serializer.data)

            gc.enable()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            print(serializer.errors)
            gc.enable()
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
def w2a(request):
    
    output = ""
    for word in list(WordModel.objects.all()):
        answers = list(AnswerModel.objects.filter(words=word))
        output += word.word + ":" + str(len(answers)) + '<br>'
    
    return HttpResponse(output)