from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

class TestViews(APITestCase):

    def test_create(self):

        #create a test stream
        data = {"url": "192.168.43.1:4747/video?640x480", "enabled": "True"}
        response = self.client.post(reverse("stream"),data)
        print(response)
        self.assertEqual(response.status_code, status.HTTP_200_OK) 

    def test_update(self):

        #create a test stream
        data = {"url": "192.168.43.1:4747/video?640x480", "enabled": "True"}
        response1 = self.client.post(reverse("stream"),data)
        self.assertEqual(response1.status_code, status.HTTP_200_OK)

        #update the test stream
        response = self.client.put(reverse("stream"),data)
        print(response)
        self.assertEqual(response.status_code, status.HTTP_200_OK) 

    def test_stop(self):

        #create a test stream
        data = {"url": "192.168.43.1:4747/video?640x480", "enabled": "True"}
        response1 = self.client.post(reverse("stream"),data)
        self.assertEqual(response1.status_code, status.HTTP_200_OK)

        #stop the test stream
        response = self.client.delete(reverse("stream"),data)
        print(response)
        self.assertEqual(response.status_code, status.HTTP_200_OK)     
