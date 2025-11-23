"""
Celery configuration for background task processing
Handles async research, PDF processing, and batch operations
"""
from celery import Celery
from config import Config

# Initialize Celery
celery = Celery(
    'genealogy_platform',
    broker=Config.CELERY_BROKER_URL,
    backend=Config.CELERY_RESULT_BACKEND
)

# Celery configuration
celery.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes max
    task_soft_time_limit=25 * 60,  # 25 minutes soft limit
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Auto-discover tasks from modules
celery.autodiscover_tasks(['tasks'])
