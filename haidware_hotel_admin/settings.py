from pathlib import Path
import os
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-change-me-before-production')
DEBUG = os.environ.get('DEBUG', 'True') != 'False'

ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '.onrender.com', '.railway.app', '.loca.lt', '.haidware.com']

INSTALLED_APPS = [
    'corsheaders',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'dashboard',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'dashboard.middleware.AdminAuthRequiredMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'haidware_hotel_admin.urls'

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [BASE_DIR / 'templates'],
    'APP_DIRS': True,
    'OPTIONS': {
        'context_processors': ['django.template.context_processors.request'],
    },
}]

WSGI_APPLICATION = 'haidware_hotel_admin.wsgi.application'
ASGI_APPLICATION = 'haidware_hotel_admin.asgi.application'

DATABASE_URL = os.environ.get('DATABASE_URL', '').strip()
if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=600,
            ssl_require=True,
        )
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Lagos'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'

CORS_ALLOWED_ORIGINS = [
    'http://127.0.0.1:5500',
    'http://localhost:5500',
    'http://127.0.0.1:5173',
    'http://localhost:5173',
    'http://127.0.0.1:3000',
    'http://localhost:3000',
]
CORS_ALLOWED_ORIGIN_REGEXES = [
    r'^https://[a-z0-9-]+\.loca\.lt$',
]
CSRF_TRUSTED_ORIGINS = [
    'https://*.onrender.com',
    'https://*.haidware.com',
    'https://haidware.com',
]

# Supabase sync (admin portal -> Supabase)
SUPABASE_SYNC_ENABLED = os.environ.get('SUPABASE_SYNC_ENABLED', '0') == '1'
SUPABASE_URL = os.environ.get('SUPABASE_URL', '').strip()
SUPABASE_SERVICE_ROLE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY', '').strip()
SUPABASE_HOTEL_TABLE = os.environ.get('SUPABASE_HOTEL_TABLE', 'hotel_accounts').strip()
SUPABASE_MENU_TABLE = os.environ.get('SUPABASE_MENU_TABLE', 'menu_items').strip()
SUPABASE_HOTEL_NAME = os.environ.get('SUPABASE_HOTEL_NAME', 'Sunview').strip()
