import asyncio
import tempfile
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

from cip.celery_app import celery_app
from cip.db.session import SessionLocal
from cip.models.video_session import VideoSession, VideoSessionStatus
from cip.services.frame_processor import process_frame
from cip.services.inference.provider_registry import get_inference_provider
from cip.services.ingestion.frame_sampler import sample_frames_from_file
from cip.services.ingestion.storage import get_object
from cip.services.tracking_service import SessionTracker


@celery_app.task(name="cip.process_uploaded_video")
def process_uploaded_video(video_session_id: str) -> None:
    """Phase 1 pipeline: decode an uploaded video, sample frames, run
    detection + in-process tracking for each sampled frame, persist
    DetectionEvents. Same downstream steps (cip.services.frame_processor)
    the RTSP StreamManager (Phase 2) reuses for live cameras.
    """

    db = SessionLocal()
    try:
        session = db.get(VideoSession, uuid.UUID(video_session_id))
        if session is None:
            return

        session.status = VideoSessionStatus.PROCESSING
        session.start_time = datetime.now(timezone.utc)
        db.commit()

        video_bytes = get_object(session.source_object_key)
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
            tmp.write(video_bytes)
            tmp_path = tmp.name

        provider = get_inference_provider()
        tracker = SessionTracker()

        try:
            for offset_seconds, frame_bytes in sample_frames_from_file(tmp_path):
                asyncio.run(
                    process_frame(
                        db=db,
                        provider=provider,
                        tracker=tracker,
                        camera_id=session.camera_id,
                        timestamp=session.start_time + timedelta(seconds=offset_seconds),
                        frame_bytes=frame_bytes,
                        video_session_id=session.id,
                    )
                )
                db.commit()
        finally:
            Path(tmp_path).unlink(missing_ok=True)

        session.status = VideoSessionStatus.DONE
        session.end_time = datetime.now(timezone.utc)
        db.commit()
    except Exception as exc:  # noqa: BLE001 - persist failure state for the UI to show
        db.rollback()
        session = db.get(VideoSession, uuid.UUID(video_session_id))
        if session is not None:
            session.status = VideoSessionStatus.FAILED
            session.error_message = str(exc)[:2000]
            db.commit()
        raise
    finally:
        db.close()
