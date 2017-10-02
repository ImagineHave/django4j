'''
Created on 26 Aug 2017

@author: Christopher Williams
'''
import nltk, string
from s4j import serializers
from s4j import models
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from s4j.models import FieldModel
from random import randint
from sklearn.feature_extraction.text import TfidfVectorizer


class BibleView(APIView):
    def post(self, request, format=None):
        serializer = serializers.BibleSerializer(data=request.data)
        if serializer.is_valid():
            FieldModel.objects.all().delete()
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request, format=None):
        fields = models.FieldModel.objects.all()
        serializer = serializers.FieldSerializer(fields, many=True)
        return Response(serializer.data)
    
    
class PrayerView(APIView):
    def post(self, request, format=None):
        serializer = serializers.PrayerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            #jesus fuck, this was hard to get right. 
            #how does one make a Model iteratble?!?!
            print(request.data.get("prayer"))
            #random_index = randint(0, FieldModel.objects.count() - 1)
            #quote = FieldModel.objects.values("passage")[random_index]['passage']
            print("models:",FieldModel.objects.values("passage"))
            bestMatch = max(FieldModel.objects.values("passage"), key=lambda item: cosine_sim(request.data.get("prayer"),item.get("passage")))			
            print("best:",bestMatch)
            field = FieldModel.objects.filter(passage=bestMatch.get("passage"))
            print("field:", field)
            serializer = serializers.FieldSerializer(field, many=True)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def stem_tokens(tokens):
    stemmer = nltk.stem.porter.PorterStemmer()
    return [stemmer.stem(item) for item in tokens]
	
'''remove punctuation, lowercase, stem'''
def normalize(text):
    remove_punctuation_map = dict((ord(char), None) for char in string.punctuation)
    return stem_tokens(nltk.word_tokenize(text.lower().translate(remove_punctuation_map)))
	
def cosine_sim(text1, text2):
    vectorizer = TfidfVectorizer(tokenizer=normalize, stop_words='english')
    tfidf = vectorizer.fit_transform([text1, text2])
    return ((tfidf * tfidf.T).A)[0,1]