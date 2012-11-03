#-*- coding: utf-8 -*-

from medias.models.media import Media
from django.db import models
from model_utils import Choices
from helpers.ffmpeg import webm, thumbnail, metadata
from django.core.files.base import ContentFile
import os
from medias.models.mixins.models import ThumbAccessors
from subprocess import CalledProcessError
from django.db.models import permalink
from model_utils.managers import PassThroughManager
from django.db.models.query import QuerySet
from medias.models.mixins.manager import PermissionManager


class VideoQuerySet(PermissionManager, QuerySet):
    pass

class Video(ThumbAccessors, Media):
    
    objects = PassThroughManager.for_queryset_class(VideoQuerySet)()
    
    @permalink
    def get_absolute_uri(self):
        return 'media_view', None, {'pk': self.pk}
    
    def save(self, *args, **kwargs):
        
        if self._state.adding:
            self.meta_date = getattr(metadata(self.file.path), 'date')
        
        super(Video, self).save(*args, **kwargs)
       
    
    def toJSON(self):
        
        return {
                'id' : self.pk,
                'name' : self.name,
                'description' : self.description,
                'date' : str(self.date),
                'is_an_album' : self.is_an_album,
                'parent_album' : self.parent_album.pk if self.parent_album is not None else None,
                'thumbnails' : {
                                'small' : self.thumbnail_small(),
                                'medium' : self.thumbnail_medium(),
                                'large' : self.thumbnail_large()
                                }}
    
    def generate_thumbnails(self):
        try:
            retcode,tmp_file = thumbnail(self.file.path)
        except Exception:
            self.status = Media.STATUSES.failed
            self.save()
            return
        
        if retcode == 0:
            self.generate_thumbnail('small', tmp_file)
            self.generate_thumbnail('medium', tmp_file)
            self.generate_thumbnail('large', tmp_file)
            
            os.remove(tmp_file)
            
    def generate_versions(self):
        meta = metadata(self.file.path)
        size = int(meta.get('size')[1]) if meta.get('size') is not None else None
        
        if size is None:
            return
        
        for s in VideoVersion.SIZES:
            if int(s[0]) <= size:
        
                if not self.video_versions.filter(type=VideoVersion.TYPES.webm, size=s[0]).exists():
                    try:
                        retcode,  tmp_file = webm(self.file.path, s[0])
                    except Exception, CalledProcessError:
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
        verbose_name = u'Vidéo'
        
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