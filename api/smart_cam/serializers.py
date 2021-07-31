from smart_cam.models import Stream
from rest_framework import serializers

class StreamSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        """
        Create and return a new `Stream` instance, given the validated data.
        """
        data = dict()
        data["url"] = validated_data['url']
        data["enabled"] = True #Add the enabled parameter

        return Stream.objects.create(**data)

    def update(self,instance, validated_data):
        """
        Updata, save and return the updated `Stream` instance, using the validated data.
        """
        instance.url = validated_data.get('url',instance.url)
        instance.enabled = validated_data.get('enabled',instance.enabled)
        instance.save()
        return instance


    class Meta:
        model = Stream
        fields = ['url' , 'enabled']