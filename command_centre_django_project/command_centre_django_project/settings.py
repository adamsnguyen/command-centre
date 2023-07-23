"""
Django settings for command_centre_django_project project.

Generated by 'django-admin startproject' using Django 4.1.10.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""

from pathlib import Path
import os
import json
from os.path import dirname, abspath

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-civpu*h-yx2(eqg1++yno2w337zxd81d$7-$(pd99dp$lu(x&='

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'bootstrap4',
    'device_scheduler',
    "bootstrap_datepicker_plus",
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'command_centre_django_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],

            'libraries':{
            'custom_filters': 'device_scheduler.comma_filter.custom_filters',
            
            }
        },
    },
]

WSGI_APPLICATION = 'command_centre_django_project.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

path = dirname((dirname(abspath(__file__))))
secret = os.path.join(path, 'common', 'config.json')
# secret = "./common/config.json"

# Read the contents of the JSON file
# try:
with open(secret) as file:
    database = json.load(file)
# except Exception as e:

#     print(os.listdir("/"))
#     quit()

# Extract the username, password, and database from the JSON data
engine = database["django_database_settings"]["DATABASE_ENGINE"]
name = database["django_database_settings"]["NAME"]
username = database["django_database_settings"]["USER"]
password = database["django_database_settings"]["PASSWORD"]
host = database["django_database_settings"]["HOST"]
port = database["django_database_settings"]["PORT"]

DATABASES = {
    'default': {
        'ENGINE': engine,
        'NAME': name, 
        'USER': password, 
        'PASSWORD': password,
        'HOST': host, 
        'PORT': port,
        },
    }



# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

USE_L1ON = True

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static')
]


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = 'static/'

# Add the following line to set the STATIC_ROOT
STATIC_ROOT = os.path.join(BASE_DIR, 'static')  # Or specify your desired directory

# Remove the STATIC_ROOT setting from STATICFILES_DIRS
STATICFILES_DIRS = [
    # Add any additional directories here if needed for development
]

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

ALLOWED_HOSTS = ['*']
