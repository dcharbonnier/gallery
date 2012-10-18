from django.contrib.auth.models import User
from medias.models import Album
import os
from django.db.utils import IntegrityError
import datetime
from middleware.request import set_current_user


def get_jobs(last=0):

    import_path = "/home/virtualenv/photos-nastux/"

    user = User.objects.get(pk=1)
    root_category = Album.objects.get( parent_id = 1, created_by=user)

    for rep, dirs, files in os.walk(import_path):

        # mpg, mov, avi

        images = [file for file in files if file.lower().split('.')[-1] in ['jpeg', 'jpg', 'png', 'mpg', 'avi', 'mov']]

        if len(images) > 0:
            path = rep.replace(import_path, '')

            if len(path) == 0:
                cat = root_category
                created = False
            else:
                p = path.split('/')[-1]
                cat, created = Album.objects.get_or_create(name=p, parent=root_category, created_by = user, modified_by=user)

            for image in images:
                yield cat.pk, rep, image, user.pk

def handle_job(data):
    from helpers import create_media
    album_pk, rep, name, user_pk = data

    set_current_user(User.objects.get(pk=user_pk))

    image_path = "%s/%s" % (rep, name)

    f = open(image_path, 'r')
    file_date = datetime.datetime.fromtimestamp(os.path.getmtime(image_path))

    try:

        create_media(Album.objects.get(pk=album_pk), f,name, file_date)

    except IntegrityError,e:
        pass

    except Exception,e:
        print e


    f.close()

