from django.db import models
from medias.models import Media
from medias.models import Thumbnail
from medias.models.image import Image
from middleware.request import get_current_user

class Album(Media):
    #media_ptr = models.OneToOneField('medias.Media', primary_key=True, related_name='albums', parent_link=True)
    end_date = models.DateTimeField(null=True)
    
    #old_id = models.PositiveIntegerField()
    
    
    def get_ancestors(self):
        
        ancestors = []
        current = self.parent_album
        while current is not None:
            ancestors.insert(0,current)
            current = current.parent_album
          
        return ancestors
        
    
    def get_children(self):
        
        return self.medias
    
    def default_thumbnail(self):
        try:
            return Thumbnail.objects.get(media_id=self.get_children().models(Image)[0], size='small')
        except Exception,e:
            print e
            return '/pix.gif'
            
    
    @property
    def display_name(self):
        if self.is_user_root is True:
            
            if self.owner == get_current_user():
                return 'Mes albums'
            else:
                return self.owner.get_full_name()
        else:
            return self.name
    
    @property
    def is_root(self):
        return self.name=='root' and self.parent_album is None
    
    @property
    def is_user_root(self):
        try:
            return self.parent_album.is_root
        except:
            return False
    
    @models.permalink
    def get_absolute_uri(self):
        return 'album_view', None, {'pk': self.pk}
    
    def save(self, *args, **kwargs):
        created = False
        if self._state.adding:
            created = True
        
        super(Album, self).save(*args, **kwargs)
        #if created:
        #    self.consolidate_count()
        
    def consolidate_count(self):
        """
        from .image import Image
        self.album_count = self.get_descendant_count()
        self.images_count = Image.objects.filter(album__in=self.get_descendants(include_self=True)).count()
        if self.images_count > 0:
            self.start_date = Image.objects.filter(album__in=self.get_descendants(include_self=True)).order_by('date')[0].date
            self.end_date = Image.objects.filter(album__in=self.get_descendants(include_self=True)).order_by('-date')[0].date
        self.save()
        if self.parent is not None:
            self.parent.consolidate_count()
        """
        
    def __unicode__(self):
        if self.is_user_root:
            return self.owner.get_full_name()
        else:
            return self.name

    class Meta:
        app_label = 'medias'
