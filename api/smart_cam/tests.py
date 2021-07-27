from smart_cam.settings import BASE_DIR
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from smart_cam.models import Stream
import os


class TestViews(APITestCase):

    userCnt = 0 #Stores the cnt of streams created while testing
    def setUp(self):
        #create test streams for the update, delete and fetch tests
        stream = {"url": "http://192.168.43.1:8010/video?640x480", "enabled": "True"}
        Stream.objects.create(**stream)
        self.userCnt+=1
        print()

    def test_create(self):
        print("Test_create")

        #create three test streams
        stream = {"url": "192.168.43.1:4747/video?640x480"}    
        response = self.client.post(reverse("stream"),stream)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED) 
        self.userCnt+=1


    def test_fetch(self):
        print("Test_fetch")

        #fetch all streams
        response = self.client.get(reverse("stream"))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        #fetch stream by id
        response = self.client.get(reverse("stream_with_id", args=[1]))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        

    def test_update(self):
        print("Test_update")

        #update the test stream
        data = {"enabled": "False"}
        response = self.client.put(reverse("stream_with_id", args=[1]),data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK) 

        #update the test stream
        data = {"enabled": "True"}
        response = self.client.put(reverse("stream_with_id", args=[1]),data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK) 

    def test_delete(self):
        print("Test_delete")

        #delete the test stream
        response = self.client.delete(reverse("stream_with_id", args=[1]))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)    

    def tearDown(self):
        
        print("Ending Test and Cleaning up")

        data = {"enabled": "False"}
        for i in range(1,self.userCnt+1):
            response = self.client.put(reverse("stream_with_id", args=[i]),data)

        for i in range(1,self.userCnt+1):
            path = f"smart_cam\stream_recordings\{i}.mp4"
            os.remove(path)

        print("Done\n")    

