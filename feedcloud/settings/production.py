from feedcloud.settings.base import *
from feedcloud.settings.configs import *

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.environ.get("SECRET_KEY", None)

if not SECRET_KEY:
    raise Exception("Add SECRET_KEY env variable, example: export SECRET_KEY=123456")

DEBUG = False
TEST = False

ALLOWED_HOSTS = (
    "apid.feed.cloud",
    "localhost",
)


DB_NAME = os.environ.get("DB_NAME", None)
if not DB_NAME:
    raise Exception("Add DB_NAME env variable, example: export DB_NAME=feedclouddb")

DB_USER = os.environ.get("DB_USER", None)
if not DB_USER:
    raise Exception("Add DB_USER env variable, example: export DB_USER=feedcloud")

DB_PASS = os.environ.get("DB_PASS", None)
if not DB_PASS:
    raise Exception("Add DB_PASS env variable, example: export DB_PASS=feedcloudpass")

DB_HOST = os.environ.get("DB_HOST", None)
if not DB_HOST:
    raise Exception("Add DB_HOST env variable, example: export DB_HOST=localhost")

DB_PORT = os.environ.get("DB_PORT", None)
if not DB_PORT:
    raise Exception("Add DB_PORT env variable, example: export DB_PORT=5432")

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": DB_NAME,
        "USER": DB_USER,
        "PASSWORD": DB_PASS,
        "HOST": DB_HOST,
        "PORT": DB_PORT,
    }
}

CACHE_HOST = os.environ.get("CACHE_HOST", None)
if not CACHE_HOST:
    raise Exception("Add CACHE_HOST env variable, example: export CACHE_HOST=localhost")

CACHE_PORT = os.environ.get("CACHE_PORT", None)
if not CACHE_PORT:
    raise Exception("Add CACHE_PORT env variable, example: export CACHE_PORT=6379")

CACHE_DB = os.environ.get("CACHE_DB", None)
if not CACHE_DB:
    raise Exception("Add CACHE_DB env variable, example: export CACHE_DB=0")

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"redis://{CACHE_HOST}:{CACHE_PORT}/{CACHE_DB}",  # over http
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}

EMAIL_HOST = os.environ.get("EMAIL_HOST", None)
if not EMAIL_HOST:
    raise Exception(
        "Add EMAIL_HOST env variable, example: export EMAIL_HOST=mail.feed.cloud"
    )

EMAIL_PORT = os.environ.get("EMAIL_PORT", None)
if not EMAIL_PORT:
    raise Exception("Add EMAIL_PORT env variable, example: export EMAIL_PORT=465")

EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", None)
if not EMAIL_HOST_USER:
    raise Exception(
        "Add EMAIL_HOST_USER env variable, example:"
        " export EMAIL_HOST_USER=support@feed.cloud"
    )

EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", None)
if not EMAIL_HOST_PASSWORD:
    raise Exception(
        "Add EMAIL_HOST_PASSWORD env variable, example:"
        "export EMAIL_HOST_PASSWORD=my3mailpassword"
    )

EMAIL_USE_SSL = True

CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = (
    "http://localhost:8000",
    "http://localhost:3000",
    "http://feed.cloud",
    "https://feed.cloud",
)

# sentry
SENTRY_URL = os.environ.get("SENTRY_URL", None)

if not SENTRY_URL:
    sentry_sdk.init(
        SENTRY_URL,
        integrations=[DjangoIntegration()],
        traces_sample_rate=1.0,
        send_default_pii=True,
    )

RABBIT_HOST = os.environ.get("RABBIT_HOST", None)
if not RABBIT_HOST:
    raise Exception(
        "Add RABBIT_HOST env variable, example: export RABBIT_HOST=localhost"
    )

RABBIT_PORT = os.environ.get("RABBIT_PORT", None)
if not RABBIT_PORT:
    raise Exception("Add RABBIT_PORT env variable, example: export RABBIT_PORT=5672")
