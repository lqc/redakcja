# -*- coding: utf-8 -*-
import os.path

PROJECT_ROOT = os.path.realpath(os.path.dirname(__file__))

DEBUG = False
TEMPLATE_DEBUG = DEBUG

MAINTENANCE_MODE = False

ADMINS = (
    # (u'Marek Stępniowski', 'marek@stepniowski.com'),
    (u'Łukasz Rekucki', 'lrekucki@gmail.com'),
)

MANAGERS = ADMINS

DATABASE_ENGINE = 'sqlite3'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = PROJECT_ROOT + '/dev.sqlite'             # Or path to database file if using sqlite3.
DATABASE_USER = ''             # Not used with sqlite3.
DATABASE_PASSWORD = ''         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Warsaw'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'pl'

#import locale
#locale.setlocale(locale.LC_ALL, '')

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = PROJECT_ROOT + '/media/dynamic'
STATIC_ROOT = PROJECT_ROOT + '/static/'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media/dynamic/'
STATIC_URL = '/media/static/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/admin-media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'ife@x^_lak+x84=lxtr!-ur$5g$+s6xt85gbbm@e_fk6q3r8=+'
SESSION_COOKIE_NAME = "redakcja_sessionid"

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.core.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "redakcja.context_processors.settings", # this is instead of media 
    "django.core.context_processors.request",
)


MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',

    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django_cas.middleware.CASMiddleware',

    'django.middleware.doc.XViewMiddleware',
    'maintenancemode.middleware.MaintenanceModeMiddleware',
    # 'debug_toolbar.middleware.DebugToolbarMiddleware' #
)

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'django_cas.backends.CASBackend',
)

ROOT_URLCONF = 'redakcja.urls'

TEMPLATE_DIRS = (
    PROJECT_ROOT + '/templates',
)


#
# Central Auth System
#
## Set this to where the CAS server lives
# CAS_SERVER_URL = "http://cas.fnp.pl/
CAS_LOGOUT_COMPLETELY = True

from compress_settings import *

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.admindocs',

    'django_cas',
    'compress',
    'south',
    'sorl.thumbnail',
    'filebrowser',

    'wiki',
    'toolbar',
)


#
# Nose tests
#

TEST_RUNNER = 'django_nose.run_tests'
TEST_MODULES = ('wiki', 'toolbar', 'vstorage')
NOSE_ARGS = (
    '--tests=' + ','.join(TEST_MODULES),
    '--cover-package=' + ','.join(TEST_MODULES),
    '-d',
    '--with-coverage',
    '--with-doctest',
)


FILEBROWSER_URL_FILEBROWSER_MEDIA = STATIC_URL + 'filebrowser/'
FILEBROWSER_DIRECTORY = 'images/'
FILEBROWSER_ADMIN_VERSIONS = []
FILEBROWSER_VERSIONS_BASEDIR = 'thumbnails/'
FILEBROWSER_DEFAULT_ORDER = "path_relative"

# REPOSITORY_PATH = '/Users/zuber/Projekty/platforma/files/books'
IMAGE_DIR = 'images'


WL_API_CONFIG = {
    "URL": "http://localhost:7000/api/",
    "AUTH_REALM": "WL API",
    "AUTH_USER": "platforma",
    "AUTH_PASSWD": "platforma",
}

# Import localsettings file, which may override settings defined here
try:
    from localsettings import *
except ImportError:
    pass

try:
    LOGGING_CONFIG_FILE
except NameError:
    LOGGING_CONFIG_FILE = os.path.join(PROJECT_ROOT, 'config',
                                ('logging.cfg' if not DEBUG else 'logging.cfg.dev'))
try:
    import logging

    if os.path.isfile(LOGGING_CONFIG_FILE):
        import logging.config
        logging.config.fileConfig(LOGGING_CONFIG_FILE)
    else:
        import sys
        logging.basicConfig(stream=sys.stderr)
except ImportError as exc:
    raise