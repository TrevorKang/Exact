from django.db import models
from util.enums import FrameType

class FrameDescription(models.Model):

    FRAME_TYPES = (
        (FrameType.ZSTACK, 'z Stack'),
        (FrameType.TIMESERIES,'time series'),
        (FrameType.UNDEFINED,'undefined')
    )

    frame_type = models.IntegerField(choices=FRAME_TYPES, default=FrameType.ZSTACK)
    description = models.CharField(max_length=160)
    file_path = models.CharField(default='', max_length=320)
    frame_id = models.IntegerField(default=0)
    Image = models.ForeignKey('Image',  on_delete=models.CASCADE, related_name='FrameDescriptions')

class Image(models.Model):
    class ImageSourceTypes:
        DEFAULT = 0
        SERVER_GENERATED = 1
        FILE_LINK = 2
    SOURCE_TYPES = (
        (ImageSourceTypes.DEFAULT, 'Default'),
        (ImageSourceTypes.SERVER_GENERATED, 'Server Generated'),
        (ImageSourceTypes.FILE_LINK, 'File Link Generated')
    )

    thumbnail_extension = "_thumbnail.png"
    image_set = models.ForeignKey(
        'ImageSet', on_delete=models.CASCADE, related_name='images')
    name = models.CharField(max_length=256)
    filename = models.CharField(max_length=256)
    time = models.DateTimeField(auto_now_add=True)
    checksum = models.BinaryField()
    mpp = models.FloatField(default=0)
    objectivePower = models.FloatField(default=1)

    width = models.IntegerField(default=800) #x
    height = models.IntegerField(default=600) #y
    depth = models.IntegerField(default=1) #z
    frames = models.IntegerField(default=1) #z
    channels = models.IntegerField(default=3) 
    defaultFrame = models.IntegerField(default=0) # to set the frame that is loaded by default

    image_type = models.IntegerField(choices=SOURCE_TYPES, default=ImageSourceTypes.DEFAULT)