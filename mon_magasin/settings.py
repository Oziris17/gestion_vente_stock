"""
Réglages du projet mon_magasin.

Idée centrale : aucun secret (clé secrète, mot de passe de la base) n'est écrit
dans ce fichier. Ils sont lus dans des "variables d'environnement" :
  - en local : depuis un fichier `.env` (jamais envoyé sur GitHub)
  - en production (Render) : depuis le tableau de bord de l'hébergeur
"""
import os
from pathlib import Path

import dj_database_url
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Lit le fichier .env (s'il existe) et met son contenu dans os.environ
load_dotenv(BASE_DIR / '.env')

# --- Sécurité -------------------------------------------------------------
# DEBUG=True affiche les erreurs détaillées : utile en local, DANGEREUX en ligne.
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    if DEBUG:
        SECRET_KEY = 'cle-de-developpement-uniquement-ne-pas-utiliser-en-ligne'
    else:
        raise RuntimeError("La variable d'environnement SECRET_KEY est obligatoire.")

# Liste des noms de domaine autorisés, séparés par des virgules.
ALLOWED_HOSTS = [h.strip() for h in os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',') if h.strip()]
CSRF_TRUSTED_ORIGINS = [o.strip() for o in os.environ.get('CSRF_TRUSTED_ORIGINS', '').split(',') if o.strip()]

if not DEBUG:
    # En ligne : cookies de session/CSRF transmis uniquement en HTTPS
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')  # Render est derrière un proxy HTTPS

# --- Applications ---------------------------------------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'gestion',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'mon_magasin.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',  # fournit `user` et `perms` aux templates
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'mon_magasin.wsgi.application'

# --- Base de données ------------------------------------------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'gestion_stock'),
        'USER': os.environ.get('DB_USER', 'postgres'),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

# En production (Render) : une seule variable DATABASE_URL décrit toute la connexion.
_db_url = os.environ.get('DATABASE_URL')
if _db_url:
    DATABASES['default'] = dj_database_url.parse(
        _db_url, conn_max_age=600, ssl_require=_db_url.startswith('postgres')
    )

# --- Mots de passe --------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# --- Langue et heure ------------------------------------------------------
LANGUAGE_CODE = 'fr'
TIME_ZONE = 'Africa/Douala'
USE_I18N = True
USE_TZ = True
USE_THOUSAND_SEPARATOR = True

# --- Fichiers statiques ---------------------------------------------------
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STORAGES = {
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage'},
}

# --- Connexion / déconnexion ----------------------------------------------
LOGIN_URL = 'login'              # où envoyer un visiteur non connecté (clients)
LOGIN_REDIRECT_URL = 'accueil'
LOGOUT_REDIRECT_URL = 'accueil'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Les e-mails s'affichent dans la console (aucun envoi réel pour l'instant)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
