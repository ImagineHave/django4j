'''
Created on 26 Aug 2017

@author: Christopher Williams
'''
import nltk, string, threading, gc, ast, logging, time, random
from s4j import serializers
from s4j import models
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from s4j.models import FieldModel, GenreModel, BookModel, AnswerModel, WordModel, PrayerModel
from random import randint
from sklearn.feature_extraction.text import TfidfVectorizer
from django.utils.six import BytesIO
from rest_framework.parsers import JSONParser
from nltk.corpus import stopwords
from django.http import HttpResponse


class ClearAndLoadDatabaseView(APIView):

    nltk.download('stopwords')
    
    def post(self, request, format=None):
        stopwords.ensure_loaded()
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
        self.deleteObjects(WordModel.objects)
        print("Word model clear")

        
    def load(self):
        print("opening .json")
        bookKey  = open("json/key_english.json").read()
        genreKey  = open("json/key_genre_english.json").read()
        bible = open("json/tb.json").read()
        
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

        fields = list(FieldModel.objects.filter(bibleName='asv'))
        
        ts = 1
        if ts > len(fields):
            ts = len(fields)/2
                
        chunk = len(fields)/ts
        threads = []
        for i in range(ts):
            j = i + 1
            t = threading.Thread(target=worker2, args=(fields[i*chunk:j*chunk],))
            t.daemon = True  
            threads.append(t)
            t.start()
            
        print(str(ts) + " threads processing")
            
        for t in threads:
            t.join() 
            
    #convert to json
    def c2j(self, input):
        return JSONParser().parse(BytesIO(input))
        
    def get(self, request, format=None):
        print("get")
        return Response("k", status=status.HTTP_200_OK)

    def deleteObjects(self, objects):
        for r in objects.all():
            r.delete()     
    
class PrayerView(APIView):
    
    def post(self, request, format=None):
        stopwords.ensure_loaded()
        print("prayer request")
        serializer = serializers.PrayerSerializer(data=request.data)
        if serializer.is_valid():
            print("prayer: " + request.data.get("prayer"))
            
            if PrayerModel.objects.filter(prayer=request.data.get("prayer")).exists():
                prayerModel = PrayerModel.objects.filter(prayer=request.data.get("prayer")).first()
                serializer = serializers.PrayerSerializer(prayerModel)
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
                serializer = serializers.PrayerSerializer(prayerModel)
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
            serializer = serializers.AnswerSerializer(ranked[0].getAnswer())
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
            serializer = serializers.PrayerSerializer(prayerModel)
            print(serializer.data)

            gc.enable()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            print(serializer.errors)
            gc.enable()
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
def stemSentence(text):
    stemmer = nltk.stem.porter.PorterStemmer()
    stemmedSentence = ""
    for word in text:
        stemmedSentence = stemmedSentence + " " + stemmer.stem(word)
    return stemmedSentence

'''remove punctuation, lowercase, stem'''
def processWords(text):
    remove_punctuation_map = dict((ord(char), None) for char in string.punctuation)
    text = text.lower().translate(remove_punctuation_map)
    filtered_words = [word for word in text.split() if word not in stopwords.words('english')]
    return stemSentence(filtered_words)
    	
def cosine_sim(text1, text2):
    vectorizer = TfidfVectorizer(norm='l2',min_df=1, use_idf=True, smooth_idf=False, sublinear_tf=True, tokenizer=tokenize, stop_words='english')
    tfidf = vectorizer.fit_transform([text1, text2])
    return ((tfidf * tfidf.T).A)[0,1]

logging.basicConfig(level=logging.DEBUG,
                    format='(%(threadName)-10s) %(message)s',
                    )
        
def worker(theBible, stemmed, x, y, bestMatch):
    logging.debug("processing: " + str(x) + " to " + str(y) + " len: " + str(len(theBible[x:y])))
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
            
class RankAnswer():
    
    def __init__(self, prayer, answer):
        tokened = tokenize(prayer)
        self.answer = answer
        processed = tokenize(answer.processed)
        dict = {}
        count = {}
        self.rank = 0.0
        
        for x in processed:
            dict[x]=0.0
            count[x]=0
            
        for x in tokened:
            if x in dict:
                if(count[x] == 0):
                    dict[x] = 1
                    count[x] = 1
                else:
                    count[x] += 1
                    dict[x] += 1 ** (1/count[x])
                    

        for x in processed:
            self.rank += dict[x]
        
    def __str__(self): 
        return self.answer.passage
        
    def getAnswer(self):
        return self.answer
            
def worker2(fields):
    i = float(0)
    j = 0
    for f in fields:
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
        
        processed = " ".join(set(processWords(bible.passage).split()))
        
        for word in tokenize(processed):
            
            wordModel = WordModel()
            
            if WordModel.objects.filter(word=word).exists():
                wordModel = WordModel.objects.filter(word=word).first()
            else:
                wordModel = WordModel(word=word)
                wordModel.save()
            
            if AnswerModel.objects.filter(processed=processed).exists():
                answer = AnswerModel.objects.filter(processed=processed).first()
                wordModel.answers.add(answer)
            else:  
                answer = AnswerModel.objects.create(
                    genre = genre,
                    genreNumber = genreNumber,
                    book = book,
                    bookNumber = bookNumber,
                    chapter = f.chapter,
                    verse = f.verse,
                    passage = passage,
                    processed = processed)
                wordModel.answers.add(answer)
        
        i = i + 1
        
        if (j != int(float(i)/float(len(fields))*100)):
            logging.debug("Progress: " + str(j) + "%")
            j = int(float(i)/float(len(fields))*100)
            
def w2a(request):
    
    output = ""
    for word in list(WordModel.objects.all()):
        answers = list(AnswerModel.objects.filter(words=word))
        output += word.word + ":" + str(len(answers)) + '<br>'
    
    return HttpResponse(output)