'''
Created on 26 Aug 2017

@author: Christopher Williams
'''
import nltk, string, threading, gc
from s4j import serializers
from s4j import models
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from s4j.models import FieldModel, GenreModel, BookModel, AnswerModel
from random import randint
from sklearn.feature_extraction.text import TfidfVectorizer
from django.utils.six import BytesIO
from rest_framework.parsers import JSONParser

class ClearDatabaseView(APIView):
    
    def post(self, request, format=None):
        print("post")
        thread = threading.Thread(target=self.process, args=())
        thread.daemon = True                            # Daemonize thread
        thread.start()                                  # Start the execution
        return Response("clear", status=status.HTTP_200_OK)
    
    def process(self):
        self.deleteObjects(FieldModel.objects)
        self.deleteObjects(AnswerModel.objects)
        self.deleteObjects(GenreModel.objects)
        self.deleteObjects(BookModel.objects)
        
        
    def deleteObjects(self, objects):
        for r in objects.all():
            r.delete()
            
class ClearFieldsView(APIView):
    
    def post(self, request, format=None):
        print("post")
        thread = threading.Thread(target=self.process, args=())
        thread.daemon = True                            # Daemonize thread
        thread.start()                                  # Start the execution
        return Response("clear", status=status.HTTP_200_OK)
    
    def process(self):
        self.deleteObjects(FieldModel.objects)
        
    def deleteObjects(self, objects):
        for r in objects.all():
            r.delete()

class ClearAnswersView(APIView):
    
    def post(self, request, format=None):
        print("post")
        thread = threading.Thread(target=self.process, args=())
        thread.daemon = True                            # Daemonize thread
        thread.start()                                  # Start the execution
        return Response("clear", status=status.HTTP_200_OK)
    
    def process(self):
        self.deleteObjects(AnswerModel.objects)
        
    def deleteObjects(self, objects):
        for r in objects.all():
            r.delete()            
            
class LoadAnswersView(APIView):
    
    def post(self, request, format=None):
        print("post")
        thread = threading.Thread(target=self.process, args=())
        thread.daemon = True                            # Daemonize thread
        thread.start()                                  # Start the execution
        return Response("k", status=status.HTTP_200_OK)
        
    def process(self):
        
        print(FieldModel.objects.all().count())
        
        for f in FieldModel.objects.filter(bibleName='kjv'):
            bookNumber = f.book
            chapter = f.chapter
            verse = f.verse
            passage = f.passage
            bibleName = f.bibleName
            
            b = BookModel.objects.filter(bookNumber=bookNumber).first()
            book = b.book
            g = GenreModel.objects.filter(genreNumber = b.genreNumber).first()
            genre = g.genre
            genreNumber = g.genreNumber
            
            bible = FieldModel.objects.filter(bibleName='asv', book=bookNumber, chapter=chapter, verse=verse, passage=passage).first()
            print(bible)
            processed = bible.passage
            print(processed)
            
            mapping = {'genre':genre, 'genreNumber':genreNumber, 'book':book, 'bookNumber':bookNumber, 'chapter':f.chapter, 'verse':f.verse, 'passage':passage, 'processed':processed}
            print(mapping)
            AnswerModel.objects.create(**mapping)
            
        print("answers:"+str(AnswerModel.objects.all().count()))
        self.deleteObjects(FieldModel.objects)
        print("feilds:"+str(FieldModel.objects.all().count()))
        
    def deleteObjects(self, objects):
        for r in objects.all():
            r.delete()

class TestLoadBiblesView(APIView):
    
    def post(self, request, format=None):
        print("post")
        thread = threading.Thread(target=self.process, args=())
        thread.daemon = True                            # Daemonize thread
        thread.start()                                  # Start the execution
        return Response("k", status=status.HTTP_200_OK)
        
    def process(self):
        bookKey  = open("json/key_english.json").read()
        genreKey  = open("json/key_genre_english.json").read()
        passageBible = open("json/testbible1.json").read()
        processBible = open("json/testbible2.json").read()
        
        self.deleteObjects(FieldModel.objects)
        self.deleteObjects(AnswerModel.objects)
        self.deleteObjects(GenreModel.objects)
        self.deleteObjects(BookModel.objects)
        
        print("feilds:" + str(FieldModel.objects.all().count()))
        print("answers:" + str(AnswerModel.objects.all().count()))
        
        data = self.c2j(genreKey)
        s = serializers.GenreSerializer(data=data, many=True)
        if(s.is_valid()):
            self.deleteObjects(GenreModel.objects)
            s.save()
        
        s = serializers.GenreSerializer(GenreModel.objects.all(), many=True)
        
        data = self.c2j(bookKey)
        s = serializers.BookSerializer(data=data, many=True)
        if(s.is_valid()):
            self.deleteObjects(BookModel.objects)
            s.save()
        
        data = self.c2j(passageBible)
        s = serializers.BibleSerializer(data=data)
        if(s.is_valid()):
            s.save(bibleName="kjv")
        else:
            print(s.errors)
            
        print("first bible processed")
            
        data = self.c2j(processBible)
        s = serializers.BibleSerializer(data=data)
        if(s.is_valid()):
            s.save(bibleName="asv")
        else:
            print(s.errors)
            
        print("second bible processed")
            
        print(FieldModel.objects.all().count())
        
        
    #convert to json
    def c2j(self, input):
        return JSONParser().parse(BytesIO(input))
        
    def get(self, request, format=None):
        print("get")
        return Response("k", status=status.HTTP_200_OK)

    def deleteObjects(self, objects):
        for r in objects.all():
            r.delete()

class LoadBiblesView(APIView):
    
    def post(self, request, format=None):
        print("post")
        thread = threading.Thread(target=self.process, args=(request,))
        thread.daemon = True                            # Daemonize thread
        thread.start()                                  # Start the execution
        return Response("k", status=status.HTTP_200_OK)
        
    def process(self, request):
        
        folder = "json/"
        
        bookKey  = open(folder+"key_english.json").read()
        genreKey  = open(folder+"key_genre_english.json").read()
        passageBible = open(folder+"t_asv.json").read()
        processBible = open(folder+"t_asv.json").read()
    
        
        data = self.c2j(genreKey)
        s = serializers.GenreSerializer(data=data, many=True)
        if(s.is_valid()):
            self.deleteObjects(GenreModel.objects)
            s.save()
        
        s = serializers.GenreSerializer(GenreModel.objects.all(), many=True)
        
        data = self.c2j(bookKey)
        s = serializers.BookSerializer(data=data, many=True)
        if(s.is_valid()):
            self.deleteObjects(BookModel.objects)
            s.save()
        
        data = self.c2j(passageBible)
        s = serializers.BibleSerializer(data=data)
        if(s.is_valid()):
            s.save(bibleName="kjv")
        else:
            print(s.errors)
            
        print("first bible processed")
            
        data = self.c2j(passageBible)
        s = serializers.BibleSerializer(data=data)
        if(s.is_valid()):
            s.save(bibleName="asv")
        else:
            print(s.errors)
            
        print("second bible processed")
            
        print(FieldModel.objects.all().count())
        
        
    #convert to json
    def c2j(self, input):
        return JSONParser().parse(BytesIO(input))
        
    def get(self, request, format=None):
        print("get")
        return Response("k", status=status.HTTP_200_OK)

    def deleteObjects(self, objects):#
        for r in objects.all():
            r.delete()

class BibleView(APIView):
    
    def post(self, request, format=None):
        print("here")
        thread = threading.Thread(target=self.process, args=(request,))
        thread.daemon = True                            # Daemonize thread
        thread.start()                                  # Start the execution
        return Response("k")
        
    def process(self, request):
        print("bible processing")
        d = request.data
        print("well")
        serializer = serializers.BibleSerializer(data=d)
        print("serialised")
        if serializer.is_valid():
            FieldModel.objects.all().delete()
            serializer.save()
            print("bible uploaded")
        else:
            print("bible upload failed")
        
    def get(self, request, format=None):
        return Response("neg")
    
class PrayerView(APIView):
    def post(self, request, format=None):
        print("post")
        serializer = serializers.PrayerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            print("post save")
            #jesus fuck, this was hard to get right. 
            #how does one make a Model iteratble?!?!
            print(request.data.get("prayer"))
            theBible = list(AnswerModel.objects.all())
            print(len(theBible))
            random_index = randint(0, len(theBible) - 1)
            print(theBible[random_index])
            #bestMatch = max(theBible, key=lambda item: cosine_sim(request.data.get("prayer"),item.get("processed")))		
            #field = bestMatch.get("passage")
            field = theBible[random_index]
            serializer = serializers.AnswerSerializer(field)
            print(Response(serializer.data, status=status.HTTP_200_OK))
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            print(serializer.error)
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
