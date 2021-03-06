# Django settings for project.

import sys
from path import path
from os import environ

PROJECT_ROOT = path(__file__).abspath().dirname().dirname()
SITE_ROOT = PROJECT_ROOT.dirname()
PROJECT_NAME = SITE_ROOT.basename()

sys.path.append(SITE_ROOT)
sys.path.append(PROJECT_ROOT / 'apps')
sys.path.append(PROJECT_ROOT / 'libs') 

DEBUG = True
TEMPLATE_DEBUG = DEBUG



SENTRY_SITE = None
SENTRY_DSN = environ.get('SENTRY_DNS', None)

EMAIL_HOST = 'smtp01.oxys.net'

ADMINS = (
    ('Oxys', 'admin@oxys.net'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE' : 'django.db.backends.mysql',
        'NAME' :  environ.get('APP_DATABASE_NAME', PROJECT_NAME),
        'USER' : environ.get('APP_DATABASE_USER', PROJECT_NAME),
        'PASSWORD' : environ.get('APP_DATABASE_PASSWORD', PROJECT_NAME),
        'HOST' : environ.get('APP_DATABASE_HOST', 'localhost'),
        'PORT' : environ.get('APP_DATABASE_PORT', ''),
        'OPTIONS' : {
           "init_command": "SET storage_engine=INNODB",
        }          
    },
}

TIME_ZONE = 'Europe/Paris'

LANGUAGE_CODE = 'fr-fr'

SITE_ID = 1

USE_I18N = True

USE_L10N = True

MEDIA_ROOT = SITE_ROOT / 'data/medias/'

TEMPORARY_DIR = MEDIA_ROOT / 'tmp'

MEDIA_URL = '/medias/'

STATIC_ROOT = SITE_ROOT / 'data/statics/'

STATIC_URL = '/statics/'

ADMIN_MEDIA_PREFIX = STATIC_URL+'grappelli/'

STATICFILES_DIRS = ()

STATICFILES_FINDERS = (
    'pipeline.finders.PipelineFinder',
    'dajaxice.finder.DajaxiceFinder',
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 's@j$hm#y_kr*!b&c#e5mn!y8lczuq8yz%a024&&h-(768fy*si'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.request',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.contrib.messages.context_processors.messages',
    'social_auth.context_processors.social_auth_by_name_backends',
    'social_auth.context_processors.social_auth_backends',
    'social_auth.context_processors.social_auth_by_type_backends',
    'social_auth.context_processors.social_auth_login_redirect',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'middleware.request.ThreadRequestMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
    PROJECT_ROOT / 'templates',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'grappelli.dashboard',
    'grappelli',    
    'django.contrib.admin',
    PROJECT_NAME,
    'apps',
    'pipeline',
    'uwsgi_admin',
    'dajaxice',
    'dajax',
    'bootstrap',
    'bootstrap_toolkit',
    'medias',
    'sorl.thumbnail',
    'helpers',
    'emailusernames',
    'auth',
    'south',
    'generic_confirmation',
    'social_auth',
    'profiles',
)

GRAPPELLI_INDEX_DASHBOARD = PROJECT_NAME+'.dashboard.CustomIndexDashboard'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'root': {
        'level': 'WARNING',
        'handlers': ['sentry'],
    },
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
    },
    'filters': {
     'require_debug_false': {
         '()': 'log.RequireDebugFalse',
     }
    },
    'handlers': {
        'sentry': {
            'level': 'ERROR',
            'class': 'raven.contrib.django.handlers.SentryHandler',
            'filters': ['require_debug_false']
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        }
    },
    'loggers': {
        
        'celery' : {
            'level': 'ERROR',
            'handlers': ['sentry'],
            'propagate': False,
        },
                
        'django.db.backends': {
            'level': 'ERROR',
            'handlers': ['console'],
            'propagate': False,
        },
        'raven': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
        'sentry.errors': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
    },
}

THUMBNAIL_SIZES = {'small' : {'width' : 150, 'height':120}, 'medium' : {'width' : 1024, 'height' : 768}, 'large' : {'width' : 2560, 'height':1920},}
THUMBNAIL_ENGINE = 'sorl.thumbnail.engines.convert_engine.Engine'

DAJAXICE_MEDIA_PREFIX = "dajaxice"
DAJAXICE_XMLHTTPREQUEST_JS_IMPORT = False
DAJAXICE_JSON2_JS_IMPORT = False

AUTH_PROFILE_MODULE = 'profiles.Profile'

AUTHENTICATION_BACKENDS = (
    'social_auth.backends.twitter.TwitterBackend',
    'social_auth.backends.google.GoogleOAuth2Backend',
    'social_auth.backends.facebook.FacebookBackend',
    'social_auth.backends.contrib.dropbox.DropboxBackend',
    'emailusernames.backends.EmailAuthBackend',
    'auth.backends.ForceAuthBackend',
)
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'

FACEBOOK_EXTENDED_PERMISSIONS = ['email']
FACEBOOK_APP_ID=environ.get('FACEBOOK_APP_ID', None)
FACEBOOK_API_SECRET=environ.get('FACEBOOK_API_SECRET', None)

GOOGLE_OAUTH_EXTRA_SCOPE = ['https://www.googleapis.com/auth/userinfo.profile']
GOOGLE_OAUTH2_CLIENT_ID = environ.get('GOOGLE_OAUTH2_CLIENT_ID', None)
GOOGLE_OAUTH2_CLIENT_SECRET = environ.get('GOOGLE_OAUTH2_CLIENT_SECRET', None)

DROPBOX_APP_ID = environ.get('DROPBOX_APP_ID', None)
DROPBOX_API_SECRET = environ.get('DROPBOX_API_SECRET', None)

TWITTER_CONSUMER_KEY = environ.get('TWITTER_CONSUMER_KEY', None)
TWITTER_CONSUMER_SECRET = environ.get('TWITTER_CONSUMER_SECRET', None)
SOCIAL_AUTH_NEW_USER_REDIRECT_URL = '/'
SOCIAL_AUTH_PROTECTED_USER_FIELDS = ['email', 'first_name', 'last_name', 'username']
SOCIAL_AUTH_PIPELINE = (
    'social_auth.backends.pipeline.social.social_auth_user',
    'social_auth.backends.pipeline.misc.save_status_to_session',
    'auth.pipeline.redirect_to_form',
    'auth.pipeline.email',
    'social_auth.backends.pipeline.associate.associate_by_email',
    'social_auth.backends.pipeline.user.get_username',
    'social_auth.backends.pipeline.user.create_user',
    'social_auth.backends.pipeline.social.associate_user',
    'social_auth.backends.pipeline.social.load_extra_data',
    'social_auth.backends.pipeline.user.update_user_details',
    'auth.pipeline.update_profile',
)
