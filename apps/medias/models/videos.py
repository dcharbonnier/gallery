from medias.models.media import Media
from django.db import models
from model_utils import Choices
from helpers.ffmpeg import webm, thumbnail, metadata
from django.core.files.base import ContentFile
import os
from medias.models.mixins import ThumbAccessors

class Video(ThumbAccessors, Media):
    
    def save(self, *args, **kwargs):
        
        super(Video, self).save(*args, **kwargs)
        #self.generate_versions()
        
    def generate_thumbnails(self):
        
        retcode,tmp_file = thumbnail(self.file.path)
        
        if retcode == 0:
            self.generate_thumbnail('small', tmp_file)
            self.generate_thumbnail('medium', tmp_file)
            self.generate_thumbnail('large', tmp_file)
            
            os.remove(tmp_file)
            
    def generate_versions(self):
        size = int(metadata(self.file.path).get('size')[1])
        
        for s in VideoVersion.SIZES:
            if int(s[0]) <= size:
        
                if not self.video_versions.filter(type=VideoVersion.TYPES.webm, size=s[0]).exists():
                    try:
                        retcode,  tmp_file = webm(self.file.path, s[0])
                    except Exception:
                        retcode = 1
                    
                    version = VideoVersion(video=self, type=VideoVersion.TYPES.webm, size=s[0])
                    
                    if retcode == 0:
                        version.status = VideoVersion.STATUSES.ready
                        f = open(tmp_file, 'r')
                        version.file.save("%s.%s.webm" % (self.pk, s[0]), ContentFile(f.read()), save=False)
                        f.close()
                        os.remove(tmp_file)
                    else:
                        version.status = VideoVersion.STATUSES.failed
                    version.save()
                break
                
    class Meta:
        app_label = 'medias'
        
        
class VideoVersion(models.Model):
    
    TYPES = Choices(('webm', 'video/webm'),)
    SIZES = Choices('1280', '720', '480', '360')
    STATUSES = Choices('ready', 'failed')
    
    
    video = models.ForeignKey(Video, related_name='video_versions')
    file = models.FileField(upload_to='videos-versions/%Y/%m/',  max_length=1024, null=False)
    type = models.CharField(max_length=10, choices=TYPES, null=True)
    
    size = models.CharField(max_length=20, choices=SIZES)
    
    status = models.CharField(max_length=50, choices=STATUSES)
    
    class Meta:
        app_label = 'medias'