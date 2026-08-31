"""
Django settings for CR8TIVEIQ project.
"""

import os
from pathlib import Path
from urllib.parse import urlparse
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(env_path)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-change-me-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'True') == 'True'

# ALLOWED_HOSTS configuration
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# Add Railway domain automatically
railway_domain = os.getenv('RAILWAY_PUBLIC_DOMAIN')
if railway_domain and railway_domain not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(railway_domain)

# Allow all hosts in development
if DEBUG:
    ALLOWED_HOSTS = ['*']


# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    # Django CMS
    'cms',
    'menus',
    'treebeard',
    # Third-party apps
    'ckeditor',
    # Local apps
    'apps.core',
    'apps.portfolio',
    'apps.services',
    'apps.blog',
    'apps.contact',
    'apps.analytics',
]

SITE_ID = 1

MIDDLEWARE = [
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'apps.analytics.middleware.AnalyticsMiddleware',
]

ROOT_URLCONF = 'config.urls'

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
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'apps.analytics.context_processors.analytics_context',
                'apps.services.context_processors.services_menu',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database
# Railway provides DATABASE_URL, parse it if available
import dj_database_url

DATABASE_URL = os.getenv('DATABASE_URL')

if DATABASE_URL:
    # Use Railway's DATABASE_URL (PostgreSQL)
    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    # Fall back to SQLite for local development
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


# Password validation
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
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Languages for Django CMS
LANGUAGES = [
    ('en-us', 'English'),
]

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

# WhiteNoise configuration for static files in production
if DEBUG:
    STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
else:
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Google Cloud Storage — production media (portfolio, blog, testimonials)
# Enable by setting GS_BUCKET_NAME. Local stays on disk when the name is empty
# or USE_GCS=False.
GS_BUCKET_NAME = os.getenv('GS_BUCKET_NAME', '').strip()
GS_PROJECT_ID = os.getenv('GS_PROJECT_ID', '').strip()
GS_LOCATION = os.getenv('GS_LOCATION', 'media').strip().strip('/')
GS_MEDIA_URL = os.getenv('GS_MEDIA_URL', '').strip()
USE_GCS = os.getenv('USE_GCS', 'True' if GS_BUCKET_NAME else 'False') == 'True' and bool(GS_BUCKET_NAME)

if USE_GCS:
    import json

    from google.oauth2 import service_account

    gcs_options = {
        'bucket_name': GS_BUCKET_NAME,
        'location': GS_LOCATION,
        'file_overwrite': False,
        'default_acl': None,
        'querystring_auth': os.getenv('GS_QUERYSTRING_AUTH', 'False') == 'True',
        'object_parameters': {
            'cache_control': 'public, max-age=86400',
        },
    }
    if GS_PROJECT_ID:
        gcs_options['project_id'] = GS_PROJECT_ID

    credentials_json = os.getenv('GCS_CREDENTIALS_JSON', '').strip()
    credentials_file = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', '').strip()
    if credentials_json:
        gcs_options['credentials'] = service_account.Credentials.from_service_account_info(
            json.loads(credentials_json)
        )
    elif credentials_file:
        gcs_options['credentials'] = service_account.Credentials.from_service_account_file(
            credentials_file
        )

    default_bucket_root = f'https://storage.googleapis.com/{GS_BUCKET_NAME}'
    default_media_url = f'{default_bucket_root}/{GS_LOCATION}/'
    if not GS_MEDIA_URL:
        GS_MEDIA_URL = default_media_url
    if not GS_MEDIA_URL.endswith('/'):
        GS_MEDIA_URL += '/'

    media_root = GS_MEDIA_URL.rstrip('/')
    location_suffix = f'/{GS_LOCATION}' if GS_LOCATION else ''
    if location_suffix and media_root.endswith(location_suffix):
        bucket_root = media_root[: -len(location_suffix)]
    else:
        bucket_root = media_root
    if bucket_root != default_bucket_root:
        gcs_options['custom_endpoint'] = bucket_root

    MEDIA_URL = GS_MEDIA_URL
    STORAGES = {
        'default': {
            'BACKEND': 'storages.backends.gcloud.GoogleCloudStorage',
            'OPTIONS': gcs_options,
        },
        'staticfiles': {
            'BACKEND': STATICFILES_STORAGE,
        },
    }

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Email configuration
EMAIL_BACKEND = os.getenv('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'noreply@cr8tiveiq.com')
ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'admin@cr8tiveiq.com')
SITE_URL = os.getenv('SITE_URL', 'http://localhost:8000')

# Redis Configuration - Must be defined before Celery
REDIS_URL = os.getenv('REDIS_URL', '')
USE_REDIS = os.getenv('USE_REDIS', 'False') == 'True'

# Celery Configuration
# Only configure Celery broker if Redis is disabled
if not USE_REDIS or not REDIS_URL:
    # Use in-memory broker for development (tasks execute immediately/synchronously)
    CELERY_TASK_ALWAYS_EAGER = True
    CELERY_TASK_EAGER_PROPAGATES = True
    CELERY_BROKER_URL = 'memory://'
    CELERY_RESULT_BACKEND = 'cache+memory://'
    CELERY_BROKER_CONNECTION_RETRY = False
    CELERY_BROKER_CONNECTION_MAX_RETRIES = 0
else:
    # Use Redis for production
    CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
    CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
    CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
    CELERY_BROKER_CONNECTION_MAX_RETRIES = 3

CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 minutes
CELERY_BROKER_CONNECTION_TIMEOUT = 4  # 4 seconds timeout
CELERY_RESULT_BACKEND_TRANSPORT_OPTIONS = {
    'socket_connect_timeout': 4,
    'socket_timeout': 4,
    'retry_on_timeout': False,
}
CELERY_BROKER_TRANSPORT_OPTIONS = {
    'socket_connect_timeout': 4,
    'socket_timeout': 4,
    'socket_keepalive': True,
    'retry_on_timeout': False,
}

# Cache Configuration
if USE_REDIS and REDIS_URL:
    try:
        CACHES = {
            'default': {
                'BACKEND': 'django_redis.cache.RedisCache',
                'LOCATION': REDIS_URL,
                'OPTIONS': {
                    'CLIENT_CLASS': 'django_redis.client.DefaultClient',
                    'SOCKET_CONNECT_TIMEOUT': 5,
                    'SOCKET_TIMEOUT': 5,
                    'IGNORE_EXCEPTIONS': True,  # Fail gracefully
                }
            }
        }
        # Session Configuration
        SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
        SESSION_CACHE_ALIAS = 'default'
    except Exception as e:
        # Fall back to local memory cache if Redis fails
        CACHES = {
            'default': {
                'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
                'LOCATION': 'unique-snowflake',
            }
        }
        SESSION_ENGINE = 'django.contrib.sessions.backends.db'
else:
    # Use local memory cache for development
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'unique-snowflake',
        }
    }
    SESSION_ENGINE = 'django.contrib.sessions.backends.db'

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}

# Security Settings
if not DEBUG:
    # Trust Railway's proxy headers
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    
    # Don't force SSL redirect - Railway handles HTTPS at proxy level
    SECURE_SSL_REDIRECT = False
    
    # Cookie security
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    gcs_host = urlparse(MEDIA_URL).netloc if USE_GCS else ''
    img_src = ["'self'", 'data:', 'https:']
    media_src = ["'self'"]
    if gcs_host:
        img_src.append(f'https://{gcs_host}')
        media_src.append(f'https://{gcs_host}')
    SECURE_CONTENT_SECURITY_POLICY = {
        'default-src': ("'self'",),
        'script-src': ("'self'", "'unsafe-inline'", 'cdn.jsdelivr.net'),
        'style-src': ("'self'", "'unsafe-inline'", 'fonts.googleapis.com'),
        'font-src': ("'self'", 'fonts.gstatic.com'),
        'img-src': tuple(img_src),
        'media-src': tuple(media_src),
        'frame-ancestors': ("'none'",),
    }
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    X_FRAME_OPTIONS = 'DENY'

# CSRF Settings
CSRF_TRUSTED_ORIGINS = [
    'http://localhost',
    'http://127.0.0.1',
    'http://localhost:8000',
    'http://127.0.0.1:8000',
]

# Add Railway domains if in production
if not DEBUG:
    railway_domain = os.getenv('RAILWAY_PUBLIC_DOMAIN')
    railway_static_url = os.getenv('RAILWAY_STATIC_URL')
    
    if railway_domain:
        # Ensure domain has scheme
        if not railway_domain.startswith(('http://', 'https://')):
            railway_domain = f'https://{railway_domain}'
        CSRF_TRUSTED_ORIGINS.append(railway_domain)
    
    if railway_static_url:
        # Ensure URL has scheme
        if not railway_static_url.startswith(('http://', 'https://')):
            railway_static_url = f'https://{railway_static_url}'
        CSRF_TRUSTED_ORIGINS.append(railway_static_url)
    
    # Add custom domains from environment
    custom_domains = os.getenv('CUSTOM_DOMAINS', '')
    if custom_domains:
        for domain in custom_domains.split(','):
            domain = domain.strip()
            if domain:
                # Ensure domain has scheme
                if not domain.startswith(('http://', 'https://')):
                    domain = f'https://{domain}'
                CSRF_TRUSTED_ORIGINS.append(domain)

CSRF_COOKIE_HTTPONLY = True

# Django CMS Configuration
CMS_CONFIRM_VERSION4 = True
CMS_TEMPLATES = [
    ('base.html', 'Base Template'),
    ('home.html', 'Home Page'),
    ('page.html', 'Standard Page'),
]

CMS_PERMISSION = True
CMS_PLACEHOLDERS_CONF = {}

# File Upload Settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
ALLOWED_UPLOAD_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif', 'pdf', 'mp4', 'webm']

# CKEditor Configuration
CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'Custom',
        'toolbar_Custom': [
            ['Bold', 'Italic', 'Underline', 'Strike'],
            ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-', 'JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock'],
            ['Link', 'Unlink'],
            ['RemoveFormat', 'Source'],
            ['Format', 'Styles'],
            ['TextColor', 'BGColor'],
            ['Image', 'Table', 'HorizontalRule', 'SpecialChar'],
            ['Blockquote', 'CodeSnippet'],
        ],
        'height': 400,
        'width': '100%',
        'removePlugins': 'stylesheetparser',
        'allowedContent': True,
        'extraPlugins': ','.join([
            'codesnippet',
            'widget',
            'dialog',
        ]),
        'codeSnippet_theme': 'monokai_sublime',
        'format_tags': 'p;h1;h2;h3;h4;h5;h6;pre',
        'contentsCss': [
            'https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css',
        ],
    },
}
