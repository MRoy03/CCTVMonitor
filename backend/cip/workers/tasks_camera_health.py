"""Safety net independent of any particular ingestion path: if a camera
hasn't reported a frame recently, mark it OFFLINE. Covers RTSP cameras (if
the StreamManager process died outright, not just lost one connection) and
screen-capture cameras (if the browser tab was closed without a clean
disconnect signal).
"""

from datetime import datetime, timedelta, timezone

from cip.celery_app import celery_app
from cip.db.session import SessionLocal
from cip.models.camera import Camera, CameraStatus, SourceType

STALE_AFTER_SECONDS = 30


@celery_app.task(name="cip.mark_stale_cameras_offline")
def mark_stale_cameras_offline() -> None:
    db = SessionLocal()
    try:
        cutoff = datetime.now(timezone.utc) - timedelta(seconds=STALE_AFTER_SECONDS)
        stale_cameras = (
            db.query(Camera)
            .filter(
                Camera.source_type.in_([SourceType.RTSP, SourceType.SCREEN_CAPTURE]),
                Camera.status == CameraStatus.ONLINE,
                (Camera.last_seen_at.is_(None)) | (Camera.last_seen_at < cutoff),
            )
            .all()
        )
        for camera in stale_cameras:
            camera.status = CameraStatus.OFFLINE
        db.commit()
    finally:
        db.close()
