"""
F1 Intelligence Hub - Celery Application

Celery configuration for distributed task processing.
"""

from celery import Celery

from ..core.config import get_settings

settings = get_settings()

# Create Celery app
celery_app = Celery(
    "f1hub",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour max
    task_soft_time_limit=3300,  # 55 minutes soft limit
    worker_prefetch_multiplier=1,  # One task at a time
    worker_max_tasks_per_child=10,  # Restart worker after 10 tasks (memory cleanup)
)

# Auto-discover tasks
celery_app.autodiscover_tasks(["f1hub.workers.tasks"])
