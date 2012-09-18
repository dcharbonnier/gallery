# -*- coding: utf-8 -*-
from django.views.generic.base import TemplateView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.utils.timezone import utc, get_current_timezone
from django.http import HttpResponse, HttpResponseServerError
from django.views.decorators.csrf import csrf_exempt
from django.utils import simplejson
from django.core.files.uploadedfile import UploadedFile
from django.db.utils import IntegrityError

from PIL import Image as PILImage
from PIL.ExifTags import TAGS

from dateutil.parser import parse
import datetime

from ..models.image import Image
from ..forms import AlbumForm
from ..models.album import Album
from ..models.media import Media

class AlbumView(ListView):
    
    template_name = 'albums/album.html'
    paginate_by = 25
    _album = None
    
    
    @csrf_exempt
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(AlbumView, self).dispatch( request, *args, **kwargs)
        
    def post(self, request, *args, **kwargs):
        
        file = request.FILES[u'files[]']
        wrapped_file = UploadedFile(file)
        filename = wrapped_file.name
        
        img = PILImage.open(file)
        
        try:
            
            new_image = Image()
            exif = img._getexif()
            if exif is not None:
                for tag, value in exif.items():
                    decoded = TAGS.get(tag, tag)
                    if  decoded == 'DateTimeOriginal':
                        new_image.date = datetime.datetime.strptime(value, "%Y:%m:%d %H:%M:%S")
                        break
            
                
            name = filename.lower()
            new_image.name = name
            new_image.parent_album=self.get_album()
            
            if new_image.date is None:
                new_image.date= parse(request.POST.get(filename)).replace(tzinfo=utc).astimezone(get_current_timezone()).replace(tzinfo=None)
            
            new_image.file.save(
                          filename
                          , file, save=True)
            
            new_image.generate_thumbnails()
            
        except IntegrityError,e:
            print e
            return HttpResponseServerError(u"Le fichier \"%s\" est déja présent dans cet album" % filename) 
        
        
        return HttpResponse(simplejson.dumps({'name' : request.FILES.items()[0][1].name}), content_type="application/json")
    
    def render_to_response(self, context, **response_kwargs):
        """
        Returns a response with a template rendered with the given context.
        """
        if self.request.GET.get('thumbnails') is not None:
            
            template = 'albums/_inc/thumbnails.html'
        else:
            template = self.get_template_names()
            
        return self.response_class(
                request = self.request,
                template = template,
                context = context,
                **response_kwargs
            )
    
    def get_album(self):
        
        if self._album is None:
        
            pk = self.kwargs.get('pk', 19181)
            
            if pk is not None:
                self._album = Album.objects.get(pk=pk)
            else:
                self._album = Album.objects.get(parent_album=None)
        
        return self._album
        
    def get_queryset(self):
        return Media.objects.filter(parent_album=self.get_album()).select_subclasses()
        #return self.get_album().medias.select_subclasses()
        
    def get_context_data(self, **kwargs):
        
        context = super(AlbumView, self).get_context_data(**kwargs)
        context['album'] = self.get_album()
        # get facets
        
        
        # root album
        if self.get_album().parent_album is not None:
            context['breadcrumbs'] = self.get_album().get_ancestors()[2:] + [self.get_album()]
            
        return context
    
    
class GalleryView(TemplateView):
    
    template_name = 'gallery/gallery.html'
    
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(GalleryView, self).dispatch( request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super(GalleryView, self).get_context_data(**kwargs)
        
        context['medias'] = Album.objects.get(pk=kwargs.get('pk')).medias.select_subclasses()
        
        return context
   
class UpdateAlbum(UpdateView):
    template_name = 'albums/create_or_edit.html'
    model = Album
    form_class = AlbumForm
    
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(UpdateAlbum, self).dispatch( request, *args, **kwargs)
    
class CreateAlbum(CreateView):
    template_name = 'albums/create_or_edit.html'
    model = Album
    form_class = AlbumForm
    
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(CreateAlbum, self).dispatch( request, *args, **kwargs)
    
    def get_form_kwargs(self):
        
        data = super(CreateAlbum, self).get_form_kwargs()
        
        data['initial']['album'] = self.kwargs.get('pk')
        
        return data