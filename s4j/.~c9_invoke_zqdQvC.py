from rest_framework.parsers import JSONParser
from django.utils.six import BytesIO
from s4j.models import *
from nltk.corpus import stopwords
import string, nltk

def c2j(input):
    return JSONParser().parse(BytesIO(input))
        
def deleteObjects(objects):
    for r in objects.all():
        r.delete()
        
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


















































