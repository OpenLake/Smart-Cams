from smart_cam.models import Stream
from smart_cam.serializers import StreamSerializer
from django.http.response import JsonResponse
from rest_framework.views import APIView
from rest_framework import status

from django.db.models.signals import post_save
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

    def put(self, request, stream_id):

        #Update the enabled status of a stream
        stream = Stream.objects.get(id=stream_id)
        updatedEnabledVal = json.loads(request.data["enabled"].lower())
        stream.enabled = updatedEnabledVal
        stream.save()

        updateMsg = {'message': f'Stream {stream_id} has been updated'}

        return JsonResponse(updateMsg)


    def delete(self, request, stream_id):
        
        #Deletes the stream with given id
        stream = Stream.objects.get(id=stream_id)
        stream.delete()

        deleteMsg = {'message': f'Stream {stream_id} has been deleted'}

        return JsonResponse(deleteMsg)



@receiver(post_save, sender=Stream)
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
        instance.url, instance.url, f"{instance.id}", f"{instance.id}.mp4"
    )

    recorders[instance.id] = recorder
    start_all_threads([recorder])
    print("Started new recording")
