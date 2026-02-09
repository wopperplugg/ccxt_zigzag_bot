import os
import sys
from pathlib import Path
from decouple import config


BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = config("SECRET_KEY")

DEBUG = config("DEBUG", default=False, cast=bool)

ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="").split(",")


DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PATY_APPS = [
    "channels",
    "rest_framework",
    "corsheaders",
]
LOCAL_APPS = [
    "apps.api",
    "apps.trading_tools",
    "apps.websocket",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PATY_APPS + LOCAL_APPS

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "conf.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "conf.wsgi.application"
ASGI_APPLICATION = "conf.asgi.application"

# Database
# https://docs.djangoproject.com/en/6.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("DB_NAME", default="trading_db"),
        "USER": config("DB_USER", default="trader"),
        "PASSWORD": config("DB_PASS", default="vyjujltytu"),
        "HOST": config("DB_HOST", default="localhost"),
        "PORT": config("DB_PORT", default="5433"),
        "ATOMIC_REQUESTS": True,
    }
}


CELERY_BROKER_URL = "redis://redis:6379/0"
CELERY_RESULT_BACKEND = "redis://redis:6379/0"


# Password validation
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/6.0/topics/i18n/

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True


# настройка статических файлов
STATIC_URL = "static/"  # урл статики
STATIC_ROOT = BASE_DIR / "staticfiles"  # путь для собраных файлов статики

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# настройки DRF
REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",  # Разрешить доступ всем
    ],
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",  # ограничение запросов для анонимных пользователей
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "100/hour",  # Лимит запросов для анонимных пользователей
    },
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",  # рендеринг в json
    ],
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",  # парсинг json данных
    ],
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
}

# настройки cors для разработки и продакшена
if DEBUG:
    CORS_ALLOW_ALL_ORIGINS = True
else:
    CORS_ALLOWED_ORIGINS = [  # разрешенный источники
        "http://localhost:5173/",
        "http://127.0.0.1:5173/",
    ]

SECURE_BROWSER_XSS_FILTER = True  # защита от XSS атак
SECURE_CONTENT_TYPE_NOSNIFF = True  # запрет MIME типов
X_FRAME_OPTIONS = "DENY"  # защита от кликджекинга

# Настройки логирования
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "file": {
            "level": "INFO",  # Уровень логирования
            "class": "logging.FileHandler",  # Логирование в файл
            "filename": BASE_DIR / "debug.log",  # Путь к файлу логов
        },
    },
    "loggers": {
        "django": {
            "handlers": ["file"],  # Используемый обработчик
            "level": "INFO",  # Уровень логирования
            "propagate": True,  # Передача логов родительским логгерам.
        },
    },
}

# websocket
if DEBUG:
    # Для разработки используем InMemory
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels.layers.InMemoryChannelLayer",
        },
    }
else:
    # Для продакшена используем Redis
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels_redis.core.RedisChannelLayer",
            "CONFIG": {
                "hosts": [("127.0.0.1", 6379)],
            },
        },
    }
