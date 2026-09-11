"""
Celery application configuration.

Why a separate celery.py in config/:
- Keeps Celery config next to Django settings
- The app is imported in __init__.py so Celery is ready when Django starts
"""

import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery(
    "codexplain",
    broker="redis://127.0.0.1:6379/0",
    backend="redis://127.0.0.1:6379/0",
    include=["explainer.tasks"],
)

app.autodiscover_tasks()
