'''
Created on 26 Aug 2017

@author: Christopher Williams
'''
from rest_framework import serializers
from s4j.models import PrayerModel, FieldModel, BibleModel

class FieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = FieldModel()
        fields = ('id', 'book', 'chapter', 'verse', 'passage',)


class RowsSerializer(serializers.Serializer):
    field = serializers.ListField(child=serializers.CharField())

class ResultSetSerializer(serializers.Serializer):
    row = RowsSerializer(required=False, many=True)

class BibleSerializer(serializers.Serializer):
    resultset = ResultSetSerializer(required=False)
    
    def create(self, validated_data):
        resultset_data = validated_data.pop('resultset')
        for orderedDictionaryField in resultset_data.pop('row'):
            listing = orderedDictionaryField.pop('field')
            mapping = {'book':listing[1], 'chapter':listing[2], 'verse':listing[3], 'passage':listing[4]}
            FieldModel.objects.create(**mapping)
        return BibleModel.objects.create()

class PrayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrayerModel
        fields = ('id', 'prayer')