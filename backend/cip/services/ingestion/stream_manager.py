"""Long-lived RTSP frame puller — one process per active RTSP camera.

Deliberately NOT a Celery task: Celery is built for short, discrete units of
work, not a process that needs to stay connected to a camera indefinitely.
Run as its own process: `python -m cip.services.ingestion.stream_manager`
(a separate Fly.io "process" alongside the API and Celery worker once
deployed, same as locally).

Uses `multiprocessing.Process`, not `threading.Thread`, per camera: OpenCV's
FFmpeg-backed VideoCapture.read() hangs indefinitely for RTSP sources when
called from a background thread on Windows (its connect/read timeout
mechanism appears to depend on running on a process's main thread) — verified
directly during Phase 2 development. A separate process sidesteps this since
each one has its own main thread, and also isolates one camera's crash from
every other camera and from the poll loop itself.

Each camera process owns its own DB session and its own SessionTracker
instance — tracking needs to persist across the whole stream's lifetime,
unlike the per-upload tracker in tasks_ingestion.py which only lives for one
video. Frames funnel through the same cip.services.frame_processor.process_frame
step the upload pipeline uses, so detection/tracking logic is never
duplicated between input modes.
"""

import asyncio
import logging
import multiprocessing
import time
import uuid
from datetime import datetime, timezone

import cv2

from cip.db.session import SessionLocal
from cip.models.camera import Camera, CameraStatus, SourceType
from cip.services.frame_processor import process_frame
from cip.services.inference.provider_registry import get_inference_provider
from cip.services.tracking_service import SessionTracker
from cip.settings import get_settings

logger = logging.getLogger(__name__)

POLL_INTERVAL_SECONDS = 10
RECONNECT_BACKOFF_SECONDS = 5


def _watch_camera(camera_id: uuid.UUID, stream_url: str) -> None:
    logging.basicConfig(level=logging.INFO)
    settings = get_settings()
    provider = get_inference_provider()
    tracker = SessionTracker()
    capture: cv2.VideoCapture | None = None

    logger.info("Starting stream watcher for camera %s", camera_id)

    while True:
        db = SessionLocal()
        try:
            if capture is None or not capture.isOpened():
                capture = cv2.VideoCapture(stream_url)
                if not capture.isOpened():
                    _set_status(db, camera_id, CameraStatus.OFFLINE)
                    time.sleep(RECONNECT_BACKOFF_SECONDS)
                    continue

            ok, frame = capture.read()
            if not ok:
                _set_status(db, camera_id, CameraStatus.OFFLINE)
                capture.release()
                capture = None
                time.sleep(RECONNECT_BACKOFF_SECONDS)
                continue

            ok_encode, buffer = cv2.imencode(".jpg", frame)
            if ok_encode:
                asyncio.run(
                    process_frame(
                        db=db,
                        provider=provider,
                        tracker=tracker,
                        camera_id=camera_id,
                        timestamp=datetime.now(timezone.utc),
                        frame_bytes=buffer.tobytes(),
                    )
                )
                _set_status(db, camera_id, CameraStatus.ONLINE)
                db.commit()
        except Exception:  # noqa: BLE001 - one camera's failure must not kill the process
            logger.exception("Error watching camera %s", camera_id)
            if capture is not None:
                capture.release()
                capture = None
            time.sleep(RECONNECT_BACKOFF_SECONDS)
        finally:
            db.close()

        time.sleep(settings.frame_sample_interval_seconds)


def _set_status(db, camera_id: uuid.UUID, status: CameraStatus) -> None:
    camera = db.get(Camera, camera_id)
    if camera is not None:
        camera.status = status
        camera.last_seen_at = datetime.now(timezone.utc)
        db.commit()


def run() -> None:
    logging.basicConfig(level=logging.INFO)
    watched: dict[uuid.UUID, multiprocessing.Process] = {}

    while True:
        db = SessionLocal()
        try:
            cameras = db.query(Camera).filter(Camera.source_type == SourceType.RTSP).all()
            active_ids = set()
            for camera in cameras:
                if not camera.stream_url:
                    continue
                active_ids.add(camera.id)

                existing = watched.get(camera.id)
                if existing is not None and existing.is_alive():
                    continue  # already being watched

                process = multiprocessing.Process(
                    target=_watch_camera,
                    args=(camera.id, camera.stream_url),
                    daemon=True,
                    name=f"stream-{camera.id}",
                )
                process.start()
                watched[camera.id] = process

            # Stop watching cameras that were deleted or changed source type.
            for camera_id in list(watched):
                if camera_id not in active_ids:
                    watched[camera_id].terminate()
                    del watched[camera_id]
        finally:
            db.close()

        time.sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    run()
