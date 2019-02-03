import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ALLOWED_HOSTS = []

SHELL_PLUS = 'ipython'

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic',
    'django.contrib.staticfiles',
    'social_django',
    'raven.contrib.django.raven_compat',
    'django_extensions',
    'debug_toolbar',
    'reader'
]

MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'social_django.middleware.SocialAuthExceptionMiddleware',
]

ROOT_URLCONF = 'reader.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',
            ],
        },
    },
]

WSGI_APPLICATION = 'reader.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get('READER_DB_NAME'),
        'USER': os.environ.get('READER_DB_USER'),
        'PASSWORD': os.environ.get('READER_DB_PASSWORD'),
        'HOST': os.environ.get('READER_DB_HOST'),
        'PORT': os.environ.get('READER_DB_PORT'),
    }
}

# Authentication
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'home'
SOCIAL_AUTH_POSTGRES_JSONFIELD = True
AUTHENTICATION_BACKENDS = [
    'social_core.backends.open_id.OpenIdAuth',
    'social_core.backends.google.GoogleOpenId',
    'social_core.backends.google.GoogleOAuth2',
    'django.contrib.auth.backends.ModelBackend',
]
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = os.environ.get('GOOGLE_OAUTH2_KEY')
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = os.environ.get('GOOGLE_OAUTH2_SECRET')
SOCIAL_AUTH_GOOGLE_OAUTH2_WHITELISTED_EMAILS = [
    'mattdsegal@gmail.com',
    'k.f.pollock@gmail.com',
    'cameron.bryce01@gmail.com',
    'shonaalouis@gmail.com',
    'kristian.rodd@gmail.com',
]

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
USE_L10N = True
USE_TZ = True

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = '/static/'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
STATICFILES_DIRS = ('/app/reader/static/',)

# Media storage
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
AWS_S3_SECURE_URLS = False
AWS_QUERYSTRING_AUTH = False
AWS_DEFAULT_ACL = None,
AWS_REGION_NAME = 'ap-southeast-2'
AWS_S3_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_S3_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')

# Django Debug Toolbar
INTERNAL_IPS = ['127.0.0.1']
DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': lambda request: True,
    'SHOW_TEMPLATE_CONTEXT': True,
}
