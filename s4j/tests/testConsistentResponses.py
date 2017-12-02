from rest_framework import status
from rest_framework.test import APITestCase
import json

class AccountTests(APITestCase):
    
    def test_consistent_response(self):
        expectedResponse = {"id": 28, "prayer": "I pray that my enemies will die", "answer": {"genre": "Gospels", "genreNumber": 5, "book": "Matthew", "bookNumber": 40, "chapter": 5, "verse": 44, "passage": "but I say unto you, love your enemies, and pray for them that persecute you;", "processed": "say pray enemi unto persecut love"} }
        data = {'prayer': 'God Light'}
        response = self.client.post("/s4j/p", data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json.loads(response.content), expectedResponse)