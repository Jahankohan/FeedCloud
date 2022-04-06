import os

from celery import Celery
from celery.schedules import crontab
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "feedcloud.settings.development")

if settings.TEST:
    app = Celery(
        "feedcloud", broker=f"redis://{settings.CACHE_HOST}:{settings.CACHE_PORT}"
    )
else:
    app = Celery(
        "feedcloud",
        broker=f"amqp://guest@{settings.RABBIT_HOST}:{settings.RABBIT_PORT}//",
    )

app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks(
    (
        "authnz",
        "feed",
        "utils",
    )
)
app.conf.task_routes = {
    "fetch_feed_entries": {"queue": "feeds"},
    "schedule_fetch_feed_batch": {"queue": "feeds"},
}
app.conf.beat_schedule = {
    "low-priority-tasks": {
        "task": "schedule_fetch_feed_batch",
        "schedule": crontab(minute="*/5"),
        "args": (1,),  # Low priority tasks
    },
    "high-priority-tasks": {
        "task": "schedule_fetch_feed_batch",
        "schedule": crontab(minute="*/2"),
        "args": (2,),  # High priority tasks
    },
}

if settings.TEST:
    app.conf.task_always_eager = True
