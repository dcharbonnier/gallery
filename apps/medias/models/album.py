from django.db import models
from medias.models import Media

class Album(Media):
    media_ptr = models.OneToOneField('medias.Media', primary_key=True, related_name='albums')
    end_date = models.DateTimeField(null=True)
    
    old_id = models.PositiveIntegerField()
    
    
    def get_ancestors(self):
        
        ancestors = []
        current = self.album
        while current is not None:
            ancestors.append(current)
            current = current.album
            
        return ancestors
        
    
    def get_children(self):
        
        return Album.objects.filter(album=self)
    
    @property
    def display_name(self):
        if self.is_user_root is True:
            return self.owner.get_full_name()
        else:
            return self.name
    
    @property
    def is_root(self):
        return self.name=='root' and self.parent is None
    
    @property
    def is_user_root(self):
        try:
            return self.album.is_root()
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

#Post signal to autocreate profile
from django.contrib.auth.models import User
from django.db.models.signals import post_save

def create_user_root_album(sender, instance, created, **kwargs):
    if created:
        root, created =  Album.objects.get_or_create(name='root',parent=None)
        Album.objects.create(name=instance.pk ,created_by=instance, modified_by=instance, parent=root)

post_save.connect(create_user_root_album, sender=User)    