from smart_cam.models import Stream
from smart_cam.serializers import StreamSerializer
from django.http.response import JsonResponse
from rest_framework.views import APIView
from rest_framework import status

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from smart_cam.scripts.recorder import (
    Video_Recorder,
    start_all_threads,
    join_all_threads,
)

recorders = {}


class StreamAPI(APIView):

    ##############################Utility functions##############################

    def safe_get(self,id):
        """
        Avoid Stream.DoesNotExist exception and return 'None' on getting the exception  
        """
        try:
            stream = Stream.objects.get(id=id)
        except Stream.DoesNotExist:
            stream = None 
        return stream

    def stream_not_found(self,id):
        """
        Respond when a get or put request is made for a stream that does not exist in the database
        """
        failure_message = {'error': f'Stream {id} not found'}
        return JsonResponse(failure_message, status = status.HTTP_400_BAD_REQUEST)

    def validate_and_save_serializer(self,serializer, success_message, success_status):
        """
        Validate the data, save to database if valid and respond accordingly
        """
        if serializer.is_valid():
            serializer.save()
            response_body = serializer.data
            response_body['message'] = success_message
            return JsonResponse(response_body, status=success_status)
        else:    
            return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)   

    
    ##############################CRUD functions##############################

    def get(self, request, stream_id=None):
        """
        Get all the stream objects in thr database or a single stream objects corresponding to the given 'stream_id'
        """
        if stream_id is None:                  #respond to urlpattern 'streams'
            streams = Stream.objects.all() 
            serializer = StreamSerializer(streams,many=True)
        else:                                  #respond to urlpattern 'streams/<int:stream_id>'
            streams = self.safe_get(id=stream_id) 
            if streams is None:   
                return self.stream_not_found(id=stream_id)
            else:
                serializer = StreamSerializer(streams)   
        return JsonResponse(serializer.data, safe=False)

    def post(self, request):
        """
        Create a new Stream
        """
        serializer = StreamSerializer(data=request.data)
        success_message = 'Stream created successfully'
        return self.validate_and_save_serializer(serializer, success_message, status.HTTP_201_CREATED)

    def put(self, request, stream_id):
        """
        Update the enabled status of a stream
        """
        stream = self.safe_get(id=stream_id)
        if stream is not None:
            serializer = StreamSerializer(stream, data=request.data)
            success_message = f'Stream {stream_id} updated successfully'
            return self.validate_and_save_serializer(serializer, success_message, status.HTTP_200_OK)
        else:
            return self.stream_not_found(id=stream_id)  
       
    def delete(self, request, stream_id):
        """
        Deletes the stream with given id
        """
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
        #Revert the 'enabled' to false if stream not found
        instance.enabled=False
        instance.save()
    else:        
        print("Started new recording")
