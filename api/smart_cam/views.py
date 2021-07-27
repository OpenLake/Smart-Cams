from smart_cam.models import Stream
from smart_cam.serializers import StreamSerializer
from django.http.response import JsonResponse
from rest_framework.views import APIView
from rest_framework import status

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

import json

from smart_cam.scripts.recorder import (
    Video_Recorder,
    start_all_threads,
    join_all_threads,
)

recorders = {}


class StreamAPI(APIView):

    def get(self, request, stream_id=None):
        if stream_id is None:
            responseData = Stream.objects.all() 
            serializer = StreamSerializer(responseData,many=True)
        else:
            responseData = Stream.objects.get(id=stream_id)    
            serializer = StreamSerializer(responseData)
        return JsonResponse(serializer.data, safe=False)

    def post(self, request):

        #Create a new Stream
        feed_url = request.data["url"]
        stream = Stream(url=feed_url, enabled=True)
        stream.save()

        streamIdAndUrl = {"id": stream.id, "url": stream.url}
        return JsonResponse(streamIdAndUrl,status=status.HTTP_201_CREATED)

    #safe_get to avoid Stream.DoesNotExist exception
    def safe_get(self,id):
        try:
            got = Stream.objects.get(id=id)
        except Stream.DoesNotExist:
            got = None 
        return got       

    def put(self, request, stream_id):

        #Update the enabled status of a stream
        stream = self.safe_get(id=stream_id)
        updatedEnabledVal = json.loads(request.data["enabled"].lower())

        if stream is not None:
            stream.enabled = updatedEnabledVal
            stream.save()
            updateMsg = {'message': f'Stream {stream_id} has been updated'}
            returnStatus = status.HTTP_200_OK
        else:
            updateMsg = {'error': f'Stream {stream_id} does not exist'}
            returnStatus = status.HTTP_404_NOT_FOUND

        return JsonResponse(updateMsg, status=returnStatus)


    def delete(self, request, stream_id):
        
        #Deletes the stream with given id
        stream = Stream.objects.get(id=stream_id)
        stream.enabled = False
        stream.delete()

        deleteMsg = {'message': f'Stream {stream_id} has been deleted'}

        return JsonResponse(deleteMsg)



@receiver([post_save, post_delete], sender=Stream)
def custom_handler(sender, instance, **kwargs):
    print("Stream updated")
    # Should create celery tasks
    if not instance.enabled:
        print("Instance disable requested by user")
        if instance.id in recorders.keys():
            recorder = recorders[instance.id]
            recorder.enabled = False
            join_all_threads([recorder])
            print("Stopped recording")
        return

    recorder = Video_Recorder(
        instance.url, instance.url, f"{instance.id}", f"smart_cam\stream_recordings\{instance.id}.mp4"
    )

    recorders[instance.id] = recorder
    try:
        start_all_threads([recorder])
    except:
        print("Stream not found")
    else:        
        print("Started new recording")
