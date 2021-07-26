from smart_cam.models import Stream
from rest_framework import serializers

class StreamSerializer(serializers.ModelSerializer):

    class Meta:
        model = Stream
        fields = ['url' , 'enabled']