import os
from pathlib import Path
from dotenv import dotenv_values

config = dotenv_values('.env')

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-&i0lbk65z(%=l98c_f^l4$^11g$p47mvck629%doj_bvz31cgv'

if config.get('DEBUG'):
    DEBUG = True
else:
    DEBUG = False

if DEBUG:
    ALLOWED_HOSTS = ['*']
else:
    ALLOWED_HOSTS = ['https://example.com']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'rest_framework',
    'rest_framework.authtoken',
    'django_rest_passwordreset',
    'api',
    'drf_spectacular',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
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

ROOT_URLCONF = 'ordering_service.urls'

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

WSGI_APPLICATION = 'ordering_service.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'ordering_service',
    }
}


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

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_ROOT = ''

STATIC_URL = '/static/'

STATICFILES_DIRS = [os.path.join('static')]

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'api.User'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EMAIL_USE_TLS = True

EMAIL_HOST = 'smtp.mail.ru'

EMAIL_HOST_USER = 'netology-pdiplom@mail.ru'

EMAIL_HOST_PASSWORD = 'i~8W4rdRPFlo'

EMAIL_PORT = '465'

EMAIL_USE_SSL = True

SERVER_EMAIL = EMAIL_HOST_USER

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 40,
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ),
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/day',
        'user': '1000/day',
    },
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'Ordering service API',
    'DESCRIPTION': 'Order automation for the retail chain. Users of the service are the buyer (the manager of the '
                   'retail chain, who purchases products for sale in the store) and the supplier of products.',
    'VERSION': '1.0.0',
}

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

SITE_ID = 1

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'APP': {
            'client_id': config.get('SOCIAL_CLIENT_ID'),
            'secret': config.get('SOCIAL_SECRET'),
            'key': ''
        },
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        }
    }
}
