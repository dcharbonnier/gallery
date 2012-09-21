from .media import Media, Thumbnail
from sorl.thumbnail.shortcuts import get_thumbnail
from sorl.thumbnail import delete
from django.conf import settings
from medias.models.mixins import ThumbAccessors

class Image(ThumbAccessors, Media):
    
    def upload_path(self, filename):
        return '%s/%s' % ('/'.join([c.name for c in self.album.get_ancestors()] + [self.album.name]), filename)
    
    def generate_thumbnails(self):
        self.generate_thumbnail('small', self.file.file)
        self.generate_thumbnail('medium', self.file.file)
        self.generate_thumbnail('large', self.file.file)
    
        
    class Meta:
        app_label = 'medias'