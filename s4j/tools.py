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