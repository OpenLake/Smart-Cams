from smart_cam.models import Stream
from django.http.response import HttpResponse, JsonResponse
from rest_framework.views import APIView

from django.db.models.signals import post_save
from django.dispatch import receiver


from smart_cam.scripts.recorder import (
    Video_Recorder,
    start_all_threads,
    join_all_threads,
)

recorders = {}


class StreamAPI(APIView):
    def get(self,request):

        return HttpResponse("Get stream")

    def post(self, request):

        #Create a new Stream
        feed_url = request.data["url"]
        stream = Stream(url=feed_url, enabled=True)
        stream.save()

        return JsonResponse({"id": stream.id, "url": stream.url})

    def put(self, request):

        #Update the enabled status of a stream
        feed_url = request.data["url"]
        stream = Stream.objects.get(url=feed_url)
        stream.enabled = request.data["enabled"]
        stream.save()

        return HttpResponse("Update stream")


    def delete(self, request):
        
        #Stops the stream with given url
        feed_url = request.data["url"]
        stream = Stream.objects.get(url=feed_url)
        stream.enabled = False
        stream.save()

        return HttpResponse("Stream Stopped")



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
