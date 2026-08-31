# app/core/celery_app.py
from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "etmp",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=[
        "app.rag.tasks",  # Celery tasks module (Step 8+ will create this)
    ],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    # Reasonable defaults for embedding jobs — they're not huge, but the
    # sentence-transformers model load + encode can take a few seconds.
    task_track_started=True,
    task_time_limit=300,  # hard kill after 5 min
    task_soft_time_limit=240,  # allow graceful cleanup before hard kill
    worker_prefetch_multiplier=1,
)
