import ssl

from celery import Celery

from cip.settings import get_settings

settings = get_settings()

celery_app = Celery(
    "cip",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=[
        "cip.workers.tasks_ingestion",
        "cip.workers.tasks_camera_health",
        "cip.workers.tasks_rules",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    beat_schedule={
        "mark-stale-cameras-offline": {
            "task": "cip.mark_stale_cameras_offline",
            "schedule": 15.0,
        },
        "evaluate-all-rules": {
            "task": "cip.evaluate_all_rules",
            "schedule": 20.0,
        },
    },
)

if settings.redis_url.startswith("rediss://"):
    # Upstash (and other hosted Redis) require TLS; kombu needs this spelled out explicitly.
    ssl_opts = {"ssl_cert_reqs": ssl.CERT_REQUIRED}
    celery_app.conf.broker_use_ssl = ssl_opts
    celery_app.conf.redis_backend_use_ssl = ssl_opts
