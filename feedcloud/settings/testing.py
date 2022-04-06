from feedcloud.settings.base import *
from feedcloud.settings.configs import *

from dotenv import load_dotenv

load_dotenv(".env.testing")

SECRET_KEY = os.environ.get("SECRET_KEY", None)
if not SECRET_KEY:
    raise Exception("Add SECRET_KEY env variable, example: export SECRET_KEY=123456")

DEBUG = True
TEST = True

ALLOWED_HOSTS = ["*"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
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
