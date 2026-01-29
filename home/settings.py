
from pathlib import Path
from datetime import timedelta
import os
from dotenv import load_dotenv

load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent



# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = load_dotenv("SECRET_KEY") or os.getenv("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ["*"]
CSRF_TRUSTED_ORIGINS = [
    "https://*.railway.app",
]


USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')


#CSFR_TRUSTED_ORIGINS = [
 #   "http://127.0.0.1:8002",


# Application definition

INSTALLED_APPS = [
    'corsheaders',
    'channels',
    'django.contrib.admin',
    'django.contrib.auth',
    'rest_framework_simplejwt.token_blacklist',
    'django.contrib.contenttypes',
    'django.contrib.sessions', 
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'main'
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

CORS_ALLOW_ALL_ORIGINS = True

ROOT_URLCONF = 'home.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],
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


ASGI_APPLICATION = 'home.asgi.application'

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    },
}


print("MYSQL_DATABASE:", os.environ.get("MYSQL_DATABASE"))
print("MYSQLUSER:", os.environ.get("MYSQLUSER"))
print("MYSQLPASSWORD:", os.environ.get("MYSQLPASSWORD"))
print("MYSQLHOST:", os.environ.get("MYSQLHOST"))
print("MYSQLPORT:", os.environ.get("MYSQLPORT"))


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.environ.get("MYSQLDATABASE"),
        "USER": os.environ.get("MYSQLUSER"),
        "PASSWORD": os.environ.get("MYSQLPASSWORD"),
        "HOST": os.environ.get("MYSQLHOST"),
        "PORT": os.environ.get("MYSQLPORT"),
        "URL":os.environ.get("MYSQL_URL")
    }
}

#DATABASES = {
#'default': {
#'ENGINE': 'django.db.backends.sqlite3',
#'NAME': BASE_DIR / 'db.sqlite3',
#}
#}



# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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



REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
        
),
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.UserRateThrottle',
        'rest_framework.throttling.AnonRateThrottle',
    ], 
}

AUTHENTICATION_BACKENDS = [
    'main.auth_backend.EmailAuthBackend',
    'django.contrib.auth.backends.ModelBackend',
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    BASE_DIR / "static",
]

STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / "media"

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


AUTH_USER_MODEL = "main.User"




SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=15),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=30),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": False,
    "UPDATE_LAST_LOGIN": False,

    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "USER_AUTHENTICATION_RULE": "rest_framework_simplejwt.authentication.default_user_authentication_rule",
    "ON_LOGIN_SUCCESS": "rest_framework_simplejwt.serializers.default_on_login_success",
    "ON_LOGIN_FAILED": "rest_framework_simplejwt.serializers.default_on_login_failed",

    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
    "TOKEN_USER_CLASS": "rest_framework_simplejwt.models.TokenUser",

    "JTI_CLAIM": "jti",

    "SLIDING_TOKEN_REFRESH_EXP_CLAIM": "refresh_exp",
    "SLIDING_TOKEN_LIFETIME": timedelta(minutes=5),
    "SLIDING_TOKEN_REFRESH_LIFETIME": timedelta(days=1),

  
}
