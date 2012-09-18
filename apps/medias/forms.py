from django.forms.models import ModelForm
from medias.models import Album
from django.forms.widgets import HiddenInput

class AlbumForm(ModelForm):
    
    class Meta:
        model = Album
        widgets = {
            'album': HiddenInput,
        }
        fields = ('name', 'description',)