import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

REDIS_URL = os.environ.get("REDIS_URL", "redis://127.0.0.1:6379/0")

app = Celery(
    "codexplain",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["explainer.tasks"],
)
app.autodiscover_tasks()