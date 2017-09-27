'''
Created on 26 Aug 2017

@author: Christopher Williams
'''
from s4j import serializers
from s4j import models
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from s4j.models import FieldModel
from random import randint


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
            random_index = randint(0, FieldModel.objects.count() - 1)
            quote = FieldModel.objects.values("passage")[random_index]['passage']
            print(quote)
            field = FieldModel.objects.filter(passage=quote)
            serializer = serializers.FieldSerializer(field, many=True)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
