"""
Django settings for derby project.

Generated by 'django-admin startproject' using Django 2.2.5.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os
from collections import namedtuple

IdRange = namedtuple("IdRange", "start end")

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESOURCES_DIR = os.path.join(BASE_DIR, "resources")
COMMANDS_DIR = os.path.join(BASE_DIR, "derby", "commands")
# DATABASE_DIR = "/mnt/c/users/david/Projects/GrandPrix"
DATABASE_DIR = "/home/dave/Projects/PinewoodDerby"


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "y_qesc04(+t&smk6b&(k209y+da#a97@k-8z99nlq@hr%s4ocq"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "derby.core",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "derby.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "derby.wsgi.application"


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

PRISTINE_DB = os.path.join(BASE_DIR, "resources", "pristine.sqlite")
# LIVE_DB = os.path.join(BASE_DIR, "live.sqlite")
LIVE_DB = os.path.join(DATABASE_DIR, "live.sqlite")
BACKUPS_DIR = os.path.join(BASE_DIR, "backups")

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": LIVE_DB,
    }
}


# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "US/Pacific"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = "/static/"

DENS_EX_SIBLINGS = [
    "1. Lion",
    "2. Tiger",
    "3. Wolf",
    "4. Bear",
    "5. Webelo 1",
    "6. Webelo 2",
]
SIBLINGS = "7. Siblings"
PARENTS = "8. Parents"
DENS = DENS_EX_SIBLINGS + [SIBLINGS, PARENTS]
PACK_SLOWEST = "Pack Slowest"
PACK_FASTEST = "Pack Fastest"

LANES = 8
MIN_CARS_PER_HEAT = 4
DNF_THRESHOLD = 7.0

BACKUP_BEFORE = [
    "db",
    "rounds",
    "prelims",
    "mockprelims",
    "dens",
    "autodq",
    "mockdens",
    "slowest",
    "semis",
    "mocksemis",
    "final",
]

ROUND_CONFIG = {
    "prelims": {
        "class_id": 1,
        "class_name": "1. Prelims",
        "ranks_id_range": IdRange(1, 10),
        "ranks": DENS,
        "registrationinfo_id_range": IdRange(1, 1000),
        "round_id": 50,
        "round_number": 1,
        "chart_type": -1,
        "phase": 1,
        "racechart_id_range": IdRange(1, 1000),
    },
    "dens": {
        "class_id": 2,
        "class_name": "2. Den Finals",
        "ranks_id_range": IdRange(11, 20),
        "ranks": DENS,
        "registrationinfo_id_range": IdRange(1001, 2000),
        "round_id": 60,
        "round_number": 2,
        "chart_type": -1,
        "phase": 1,
        "racechart_id_range": IdRange(1001, 2000),
    },
    "slowest": {
        "class_id": 3,
        "class_name": "3. Pack Slowest",
        "ranks_id_range": IdRange(21, 30),
        "ranks": [PACK_SLOWEST],
        "registrationinfo_id_range": IdRange(2001, 3000),
        "round_id": 70,
        "round_number": 3,
        "chart_type": -1,
        "phase": 1,
        "racechart_id_range": IdRange(2001, 3000),
        "count": 8,
    },
    "semis": {
        "class_id": 4,
        "class_name": "4. Fastest - Semi Finals",
        "ranks_id_range": IdRange(31, 40),
        "ranks": ["Semi-Finals"],
        "registrationinfo_id_range": IdRange(3001, 4000),
        "round_id": 80,
        "round_number": 4,
        "chart_type": -1,
        "phase": 1,
        "racechart_id_range": IdRange(3001, 4000),
        "count": 18,
    },
    "final": {
        "class_id": 5,
        "class_name": "5. Fastest - Grand Final",
        "ranks_id_range": IdRange(41, 50),
        "ranks": ["Final"],
        "registrationinfo_id_range": IdRange(4001, 5000),
        "round_id": 90,
        "round_number": 5,
        "chart_type": -1,
        "phase": 1,
        "racechart_id_range": IdRange(4001, 5000),
    },
}

# Allow for cars to be automatically DQ'd (by increasing their finish time to be outside DNF_THRESHOLD)
# This is to allow (for example) overweight cars to be raced, but to be excluded from trophies, etc.
# For example: AUTO_DQ = [173, 597]
AUTO_DQ = []
