'''
Created on 26 Aug 2017

@author: Christopher Williams
'''
from rest_framework import serializers
from s4j.models import PrayerModel, FieldModel, GenreModel, BookModel, BibleModel

class FieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = FieldModel()
        fields = ('id', 'book', 'chapter', 'verse', 'passage', 'bible',)

class RowsSerializer(serializers.Serializer):
    field = serializers.ListField(child=serializers.CharField())

class ResultSetSerializer(serializers.Serializer):
    row = RowsSerializer(required=False, many=True)

class BibleSerializer(serializers.Serializer):
    resultset = ResultSetSerializer(required=False)
    def create(self, validated_data):
        resultset_data = validated_data.pop('resultset')
        bibleName = validated_data.pop('bibleName')
        rows = resultset_data.pop('row')
        print("bible: " + bibleName)
        for orderedDictionaryField in rows:
            listing = orderedDictionaryField.pop('field')
            mapping = {'book':listing[1], 'chapter':listing[2], 'verse':listing[3], 'passage':listing[4], 'bibleName':bibleName}
            FieldModel.objects.create(**mapping)
            if(FieldModel.objects.all().count() % 100 == 0):
                print(str(int(float(FieldModel.objects.all().count())/float(len(rows)) * 100)) + "%")
        print(bibleName + " completed")
        return BibleModel.objects.create(**validated_data)
            
class PrayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrayerModel
        fields = ('id', 'prayer')
        
class GenreSerializer(serializers.ModelSerializer):
    n = serializers.CharField(source='genre')
    g = serializers.IntegerField(source='genreNumber')
    
    class Meta:
        model = GenreModel
        fields = ('g','n')
        
class BookSerializer(serializers.ModelSerializer):
    n = serializers.CharField(source='book')
    b = serializers.IntegerField(source='bookNumber')
    g = serializers.CharField(source='genreNumber')
    
    class Meta:
        model = BookModel
        fields = ('b','n','g')