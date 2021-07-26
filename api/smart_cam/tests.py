from smart_cam.settings import BASE_DIR
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from smart_cam.models import Stream
import os


class TestViews(APITestCase):

    users = []
    def setUp(self):
        #create test streams for the update, delete and fetch tests
        stream = {"url": "192.168.43.1:4747/video?640x480", "enabled": "True"}
        self.users.append(Stream.objects.create(**stream))

    def test_create(self):

        #create three test streams
        stream = {"url": "192.168.43.1:4747/video?640x480", "enabled": "True"}    
        response = self.client.post(reverse("stream"),stream)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED) 


    def test_fetch(self):

        #fetch all streams
        response = self.client.get(reverse("stream"))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        #fetch stream by id
        response = self.client.get(reverse("stream_with_id", args=[1]))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        

    def test_update(self):

        #update the test stream
        data = {"enabled": "False"}
        response = self.client.put(reverse("stream_with_id", args=[1]),data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK) 

        #update the test stream
        data = {"enabled": "True"}
        response = self.client.put(reverse("stream_with_id", args=[1]),data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK) 

    def test_delete(self):

        #delete the test stream
        response = self.client.delete(reverse("stream_with_id", args=[1]))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)    

    def tearDown(self):
        for i in range(1,4):
            os.remove(f"{i}.mp4")

