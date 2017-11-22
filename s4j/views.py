'''
Created on 26 Aug 2017

@author: Christopher Williams
'''
import nltk, string, threading, gc, ast, logging
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
        bible = open("json/asv.json").read()
        
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
        j = 0
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
            processed = self.processWords(bible.passage)
            
            mapping = {'genre':genre, 'genreNumber':genreNumber, 'book':book, 'bookNumber':bookNumber, 'chapter':f.chapter, 'verse':f.verse, 'passage':passage, 'processed':processed}
            AnswerModel.objects.create(**mapping)
            
            if (j != int(float(i)/float(count)*100)):
                print("Progress: " + str(j) + "%")
                j = int(float(i)/float(count)*100)
                
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
        
    def stemSentence(self, text):
        stemmer = nltk.stem.porter.PorterStemmer()
        stemmedSentence = ""
        for word in text.split():
            stemmedSentence = stemmedSentence + " " + stemmer.stem(word)
        return stemmedSentence
	
    '''remove punctuation, lowercase, stem'''
    def processWords(self, text):
        remove_punctuation_map = dict((ord(char), None) for char in string.punctuation)
        return self.stemSentence(text.lower().translate(remove_punctuation_map))
    
class PrayerView(APIView):
    
    def post(self, request, format=None):
        print("prayer request")
        serializer = serializers.PrayerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            print("prayer saved: " + request.data.get("prayer"))
            theBible = list(AnswerModel.objects.all())
            stemmed = self.process(request.data.get("prayer"))
            #bestMatch = max(theBible, key=lambda item: self.cosine_sim(stemmed, item.processed))
            
            ts = 100
            chunk = len(theBible)/ts
            threads = []
            bestMatch = BestMatch()
            for i in range(ts):
                j = i + 1
                t = threading.Thread(target=worker, args=(theBible, stemmed, i*chunk, j*chunk, bestMatch,))
                threads.append(t)
                t.start()
                t.join()
            
            serializer = serializers.AnswerSerializer(bestMatch.bestMatch)
            print(serializer.data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            print(serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
    def stemSentence(self, text):
        stemmer = nltk.stem.porter.PorterStemmer()
        stemmedSentence = ""
        for word in text.split():
            stemmedSentence = stemmedSentence + " " + stemmer.stem(word)
        return stemmedSentence
	
    '''remove punctuation, lowercase, stem'''
    def process(self, text):
        remove_punctuation_map = dict((ord(char), None) for char in string.punctuation)
        return self.stemSentence(text.lower().translate(remove_punctuation_map))
    	
def cosine_sim(text1, text2):
    vectorizer = TfidfVectorizer(norm='l2',min_df=1, use_idf=True, smooth_idf=False, sublinear_tf=True, tokenizer=tokenize, stop_words='english')
    tfidf = vectorizer.fit_transform([text1, text2])
    return ((tfidf * tfidf.T).A)[0,1]

logging.basicConfig(level=logging.DEBUG,
                    format='(%(threadName)-10s) %(message)s',
                    )
        
def worker(theBible, stemmed, x, y, bestMatch):
    logging.debug("processing: " + str(x) + " to " + str(x))
    bestMatch.set(max(theBible[x:y], key=lambda item: cosine_sim(stemmed, item.processed)), stemmed)
    logging.debug("processing complete")
        
tokenize = lambda doc: doc.split()

class BestMatch():
    
    def __init__(self):
        self.bestMatch = None
        
    def set(self, bestMatch, stemmed):
        if(self.bestMatch == None):
            self.bestMatch = bestMatch
        else:
            self.bestMatch = max([self.bestMatch, bestMatch], key=lambda item: cosine_sim(stemmed, item.processed))