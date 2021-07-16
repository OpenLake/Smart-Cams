from django.db import models


class Stream(models.Model):
    url = models.CharField(default='192.168.43.1:4747/video?640x480', max_length=512)
    enabled = models.BooleanField(default=False)


