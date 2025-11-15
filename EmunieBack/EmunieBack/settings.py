"""
Django settings for EmunieBack project.
Configuration optimisée pour déploiement VPS sur emunie-market.com
"""

from pathlib import Path
from datetime import timedelta
from decouple import config
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# ========================================
# SÉCURITÉ
# ========================================

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='django-insecure-e5=uop2dftv!oz!ahuz&e1sjtr72mp#iarqzv*fu6(3+_&q=qk')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=False, cast=bool)

# Hosts autorisés - depuis variable d'environnement
ALLOWED_HOSTS = config(
    'ALLOWED_HOSTS',
    default='localhost,127.0.0.1,emunie-market.com,www.emunie-market.com',
    cast=lambda v: [s.strip() for s in v.split(',')]
)

# ========================================
# APPLICATIONS
# ========================================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party apps
    'rest_framework',
    'rest_framework.authtoken',
    'rest_framework_simplejwt',
    'corsheaders',
    'django_filters',
    'mptt',
    'phonenumber_field',
    'django_extensions',
    'drf_spectacular',

    # Local apps
    'user',
    'produit',
    'monetisation',
    'premium',
]

# ========================================
# MIDDLEWARE
# ========================================

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # DOIT être en PREMIER
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'EmunieBack.urls'

# ========================================
# TEMPLATES
# ========================================

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'EmunieBack.wsgi.application'

# ========================================
# BASE DE DONNÉES
# ========================================

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': config('DB_NAME', default='Emunie_db'),
        'USER': config('DB_USER', default='root'),
        'PASSWORD': config('DB_PASSWORD', default='123456789'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='3306'),
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

# ========================================
# REST FRAMEWORK
# ========================================

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# ========================================
# JWT CONFIGURATION
# ========================================

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
}

# ========================================
# CORS CONFIGURATION
# ========================================

# Environnement de développement
CORS_ALLOWED_ORIGINS_DEV = [
    "http://localhost:4200",
    "http://127.0.0.1:4200",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
]

# Environnement de production
CORS_ALLOWED_ORIGINS_PROD = [
    "https://emunie-market.com",
    "https://www.emunie-market.com",
]

# Sélection selon l'environnement
if DEBUG:
    CORS_ALLOWED_ORIGINS = CORS_ALLOWED_ORIGINS_DEV
else:
    CORS_ALLOWED_ORIGINS = CORS_ALLOWED_ORIGINS_PROD

CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# ========================================
# CSRF & COOKIES (PRODUCTION)
# ========================================

# CSRF Protection
if not DEBUG:
    CSRF_TRUSTED_ORIGINS = [
        'https://emunie-market.com',
        'https://www.emunie-market.com',
    ]

    # Cookies sécurisés (HTTPS uniquement)
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    CSRF_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    CSRF_COOKIE_SAMESITE = 'Lax'

    # Force HTTPS
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

    # HSTS (HTTP Strict Transport Security)
    SECURE_HSTS_SECONDS = 31536000  # 1 an
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

# ========================================
# PASSWORD VALIDATION
# ========================================

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

# ========================================
# INTERNATIONALISATION
# ========================================

LANGUAGE_CODE = 'fr-FR'
TIME_ZONE = 'Africa/Abidjan'
USE_I18N = True
USE_TZ = False

# ========================================
# FICHIERS STATIQUES
# ========================================

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Dossiers statiques additionnels (si nécessaire)
# STATICFILES_DIRS = [
#     BASE_DIR / 'static',
# ]

# ========================================
# FICHIERS MÉDIA
# ========================================

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ========================================
# CONFIGURATION EMAIL
# ========================================

# URL du frontend (pour les liens de réinitialisation)
FRONTEND_URL = config('FRONTEND_URL', default='http://localhost:4200')

# Configuration Email selon l'environnement
if DEBUG:
    # Développement - Console
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
    DEFAULT_FROM_EMAIL = 'noreply@emunie-market.com'
else:
    # Production - SMTP
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
    EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
    EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
    EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
    EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
    DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='Emunie Market <noreply@emunie-market.com>')

# ========================================
# GOOGLE OAUTH
# ========================================

GOOGLE_CLIENT_ID = config('GOOGLE_CLIENT_ID', default='')
GOOGLE_CLIENT_SECRET = config('GOOGLE_CLIENT_SECRET', default='')

# Redirect URIs selon l'environnement
if DEBUG:
    GOOGLE_REDIRECT_URIS = [
        "http://localhost:4200",
        "http://localhost:4200/auth/google/callback",
    ]
else:
    GOOGLE_REDIRECT_URIS = [
        "https://emunie-market.com",
        "https://emunie-market.com/auth/google/callback",
    ]

# ========================================
# MODÈLES PERSONNALISÉS
# ========================================

# Custom user model
AUTH_USER_MODEL = 'user.CustomUser'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Phone number configuration
PHONENUMBER_DEFAULT_REGION = 'CI'  # Côte d'Ivoire

# ========================================
# DRF SPECTACULAR (SWAGGER)
# ========================================

SPECTACULAR_SETTINGS = {
    'TITLE': 'Emunie Market API',
    'DESCRIPTION': 'API pour la plateforme Emunie - Petites annonces en Côte d\'Ivoire',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    'SORT_OPERATIONS': False,
    'ENUM_NAME_OVERRIDES': {
        'AdTypeEnum': 'produit.models.AdType',
        'AdStatusEnum': 'produit.models.AdStatus',
    },
    'SCHEMA_PATH_PREFIX': '/api/',
    'SWAGGER_UI_SETTINGS': {
        'deepLinking': True,
        'persistAuthorization': True,
        'displayOperationId': False,
        'defaultModelsExpandDepth': -1,
        'defaultModelExpandDepth': 2,
        'displayRequestDuration': True,
        'docExpansion': 'none',
        'filter': True,
        'showExtensions': True,
        'showCommonExtensions': True,
    },
}

# ========================================
# SÉCURITÉ ADDITIONNELLE
# ========================================

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# ========================================
# LOGGING
# ========================================

# Créer le dossier logs s'il n'existe pas
logs_dir = BASE_DIR / 'logs'
if not os.path.exists(logs_dir):
    os.makedirs(logs_dir)

# Configuration des logs selon l'environnement
if DEBUG:
    # Développement - Logs détaillés
    LOG_LEVEL = 'DEBUG'
    LOG_FILE = logs_dir / 'django_dev.log'
else:
    # Production - Logs uniquement erreurs
    LOG_LEVEL = 'INFO'
    LOG_FILE = logs_dir / 'django_prod.log'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {asctime} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': LOG_LEVEL,
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOG_FILE,
            'maxBytes': 1024 * 1024 * 10,  # 10 MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'console': {
            'level': LOG_LEVEL,
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': logs_dir / 'django_errors.log',
            'maxBytes': 1024 * 1024 * 10,  # 10 MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file', 'error_file'],
            'level': LOG_LEVEL,
            'propagate': False,
        },
        'django.request': {
            'handlers': ['error_file'],
            'level': 'ERROR',
            'propagate': False,
        },
        'user': {
            'handlers': ['console', 'file'],
            'level': LOG_LEVEL,
            'propagate': False,
        },
        'produit': {
            'handlers': ['console', 'file'],
            'level': LOG_LEVEL,
            'propagate': False,
        },
        'monetisation': {
            'handlers': ['console', 'file'],
            'level': LOG_LEVEL,
            'propagate': False,
        },
        'premium': {
            'handlers': ['console', 'file'],
            'level': LOG_LEVEL,
            'propagate': False,
        },
    },
}

# ========================================
# CONFIGURATION SUPPLÉMENTAIRE PRODUCTION
# ========================================

# Désactiver le browsable API en production
if not DEBUG:
    REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] = [
        'rest_framework.renderers.JSONRenderer',
    ]

# ========================================
# INFORMATIONS DE DÉBOGAGE
# ========================================

if DEBUG:
    print("=" * 60)
    print("CONFIGURATION DJANGO - MODE DÉVELOPPEMENT")
    print("=" * 60)
    print(f"DEBUG: {DEBUG}")
    print(f"ALLOWED_HOSTS: {ALLOWED_HOSTS}")
    print(f"DATABASE: {DATABASES['default']['NAME']} @ {DATABASES['default']['HOST']}")
    print(f"CORS_ALLOWED_ORIGINS: {len(CORS_ALLOWED_ORIGINS)} origines")
    print(f"FRONTEND_URL: {FRONTEND_URL}")
    print("=" * 60)