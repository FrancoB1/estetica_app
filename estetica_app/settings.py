"""
Django settings for estetica_app project.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
import dj_database_url

# --------------------------------------------------
# BASE
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")

# --------------------------------------------------
# SEGURIDAD
# --------------------------------------------------

SECRET_KEY = os.getenv("SECRET_KEY")

DEBUG = os.getenv("DEBUG", "False") == "True"

ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    ".onrender.com",
]

# --------------------------------------------------
# APLICACIONES
# --------------------------------------------------

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'usuarios.apps.UsuariosConfig',


    'servicios',
    'turnos',
    'cobros',
    'clientes',
]

# --------------------------------------------------
# MIDDLEWARE
# --------------------------------------------------

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',

    # necesario para producción
    'whitenoise.middleware.WhiteNoiseMiddleware',

    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# --------------------------------------------------
# URLS
# --------------------------------------------------

ROOT_URLCONF = 'estetica_app.urls'

# --------------------------------------------------
# TEMPLATES
# --------------------------------------------------

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# --------------------------------------------------
# WSGI
# --------------------------------------------------

WSGI_APPLICATION = 'estetica_app.wsgi.application'

# --------------------------------------------------
# BASE DE DATOS
# --------------------------------------------------

DATABASES = {
    "default": dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600,
    )
}

# --------------------------------------------------
# VALIDACIÓN DE PASSWORD
# --------------------------------------------------

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

# --------------------------------------------------
# INTERNACIONALIZACIÓN
# --------------------------------------------------

LANGUAGE_CODE = 'es-ar'

TIME_ZONE = 'America/Argentina/Buenos_Aires'

USE_I18N = True
USE_TZ = True

# --------------------------------------------------
# ARCHIVOS ESTÁTICOS
# --------------------------------------------------

STATIC_URL = "/static/"

STATICFILES_DIRS = [
    BASE_DIR / "static",
]

STATIC_ROOT = BASE_DIR / "staticfiles"

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# --------------------------------------------------
# USUARIO PERSONALIZADO
# --------------------------------------------------

AUTH_USER_MODEL = 'usuarios.Usuario'

LOGIN_URL = "/login/"
