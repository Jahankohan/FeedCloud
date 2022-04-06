from feedcloud.settings.base import *
from feedcloud.settings.configs import *

from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.environ.get("SECRET_KEY", None)
if not SECRET_KEY:
    raise Exception("Add SECRET_KEY env variable, example: export SECRET_KEY=123456")

DEBUG = True
TEST = False

MIDDLEWARE.append(
    "utils.middlewares.BaseMiddleware",
)

ALLOWED_HOSTS = ["*"]

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

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

CORS_ORIGIN_ALLOW_ALL = True

RABBIT_HOST = os.environ.get("RABBIT_HOST", None)
if not RABBIT_HOST:
    raise Exception(
        "Add RABBIT_HOST env variable, example: export RABBIT_HOST=localhost"
    )

RABBIT_PORT = os.environ.get("RABBIT_PORT", None)
if not RABBIT_PORT:
    raise Exception("Add RABBIT_PORT env variable, example: export RABBIT_PORT=5672")
