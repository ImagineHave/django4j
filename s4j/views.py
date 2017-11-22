'''
Created on 26 Aug 2017

@author: Christopher Williams
'''
import nltk, string, threading, gc, ast
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

class ClearAndLoadDatabaseView(APIView):
    
    def post(self, request, format=None):
        print("Clearing and loading database")
        thread = threading.Thread(target=self.process, args=())
        thread.daemon = True                            # Daemonize thread
        thread.start()                                  # Start the execution
        return Response("setting up", status=status.HTTP_202_ACCEPTED)
        
    def process(self):
        print("clearing...")
        self.clear()
        print("loading...")
        self.load()
        print("loaded.")
    
    def clear(self):
        print("clearing objects")
        self.deleteObjects(FieldModel.objects)
        print("Field model clear")
        self.deleteObjects(AnswerModel.objects)
        print("Answer model clear")
        self.deleteObjects(GenreModel.objects)
        print("Genre model clear")
        self.deleteObjects(BookModel.objects)
        print("Book model clear")
        
    def load(self):
        print("opening .json")
        bookKey  = open("json/key_english.json").read()
        genreKey  = open("json/key_genre_english.json").read()
        bible = open("json/testbible1.json").read()
        
        print("processing genre")
        data = self.c2j(genreKey)
        s = serializers.GenreSerializer(data=data, many=True)
        if(s.is_valid()):
            s.save()
        
        print("processing book")
        data = self.c2j(bookKey)
        s = serializers.BookSerializer(data=data, many=True)
        if(s.is_valid()):
            s.save()
        
        print("processing bible")
        data = self.c2j(bible)
        s = serializers.BibleSerializer(data=data)
        if(s.is_valid()):
            s.save(bibleName="asv")
        else:
            print(s.errors)
            
        print("now loading up answers")
        count = FieldModel.objects.filter(bibleName='asv').count()
        i = float(0)
        for f in FieldModel.objects.filter(bibleName='asv'):
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
            processed = self.normalize(bible.passage)
            
            mapping = {'genre':genre, 'genreNumber':genreNumber, 'book':book, 'bookNumber':bookNumber, 'chapter':f.chapter, 'verse':f.verse, 'passage':passage, 'processed':processed}
            AnswerModel.objects.create(**mapping)
            print("Progress: " + str(int(float(i)/float(count)*100)) + "%")
            i = i + 1
            
        
    #convert to json
    def c2j(self, input):
        return JSONParser().parse(BytesIO(input))
        
    def get(self, request, format=None):
        print("get")
        return Response("k", status=status.HTTP_200_OK)

    def deleteObjects(self, objects):
        for r in objects.all():
            r.delete()     
            
    def stem_tokens(self, tokens):
        stemmer = nltk.stem.porter.PorterStemmer()
        return [stemmer.stem(item) for item in tokens]
        
    '''remove punctuation, lowercase, stem'''
    def normalize(self, text):
        remove_punctuation_map = dict((ord(char), None) for char in string.punctuation)
        return self.stem_tokens(nltk.word_tokenize(text.lower().translate(remove_punctuation_map)))
    
class PrayerView(APIView):
    def post(self, request, format=None):
        print("prayer request")
        serializer = serializers.PrayerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            print("prayer saved")
            #jesus fuck, this was hard to get right. 
            #how does one make a Model iteratble?!?!
            print(request.data.get("prayer"))
            theBible = list(AnswerModel.objects.all())
            #print(len(data.theBible))
            #print(data.theBible)
            random_index = randint(0, len(theBible) - 1)
            #print(random_index)
            #print(data.theBible[random_index])
            print(ast.literal_eval(theBible[random_index].processed))
            stemmed = self.normalize(request.data.get("prayer"))
            bestMatch = max(theBible, key=lambda item: self.cosine_sim(" ".join(stemmed), " ".join(ast.literal_eval(item.processed))))		
            #field = bestMatch.passage
            #field = theBible[random_index]
            #print(field)
            serializer = serializers.AnswerSerializer(bestMatch)
            print(serializer.data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            print(serializer.error)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
    def stem_tokens(self, tokens):
        stemmer = nltk.stem.porter.PorterStemmer()
        return [stemmer.stem(item) for item in tokens]
	
    '''remove punctuation, lowercase, stem'''
    def normalize(self, text):
        remove_punctuation_map = dict((ord(char), None) for char in string.punctuation)
        return self.stem_tokens(nltk.word_tokenize(text.lower().translate(remove_punctuation_map)))
    	
    def cosine_sim(self, text1, text2):
        vectorizer = TfidfVectorizer(tokenizer=normalize, stop_words='english')
        tfidf = vectorizer.fit_transform([text1, text2])
        return ((tfidf * tfidf.T).A)[0,1]

def normalize(text):
    remove_punctuation_map = dict((ord(char), None) for char in string.punctuation)
    return stem_tokens(nltk.word_tokenize(text.lower().translate(remove_punctuation_map)))
    
def stem_tokens(tokens):
    stemmer = nltk.stem.porter.PorterStemmer()
    return [stemmer.stem(item) for item in tokens]