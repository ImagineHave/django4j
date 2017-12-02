import nltk, tools, serializers, logging
from models import *
from django.db import connection
from s4j.tools import *

logging.basicConfig(level=logging.DEBUG,
                    format='(%(threadName)-10s) %(message)s',
                    )

class BibleLoader():
    
    def process(self):
        print("Loading Bible")
        nltk.download('stopwords')
        print("clearing...")
        self.clear()
        print("loading...")
        self.load()
        print("loaded.")
        
    def clear(self):
        print("clearing objects")
        deleteObjects(FieldModel.objects)
        print("Field model clear")
        deleteObjects(AnswerModel.objects)
        print("Answer model clear")
        deleteObjects(GenreModel.objects)
        print("Genre model clear")
        deleteObjects(BookModel.objects)
        print("Book model clear")
        deleteObjects(WordModel.objects)
        print("Word model clear")

    def load(self):
        print("opening .json")
        bookKey  = open("json/key_english.json").read()
        genreKey  = open("json/key_genre_english.json").read()
        bible = open("json/asv.json").read()
        
        print("processing genre")
        data = c2j(genreKey)
        s = serializers.GenreSerializer(data=data, many=True)
        if(s.is_valid()):
            s.save()
        
        print("processing book")
        data = c2j(bookKey)
        s = serializers.BookSerializer(data=data, many=True)
        if(s.is_valid()):
            s.save()
        
        print("processing bible")
        data = c2j(bible)
        s = serializers.BibleSerializer(data=data)
        if(s.is_valid()):
            s.save(bibleName="asv")
        else:
            print(s.errors)
            
        print("now loading up answers")
    
        fields = list(FieldModel.objects.filter(bibleName='asv'))

        i = float(0)
        j = float(0)        
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
        
        print("clearing objects")
        deleteObjects(FieldModel.objects)
        print("Field model clear")
        deleteObjects(GenreModel.objects)
        print("Genre model clear")
        deleteObjects(BookModel.objects)
        print("Book model clear")