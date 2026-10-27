"""The one `process_frame` step every input mode (upload, RTSP, screen
capture) funnels through: detect -> track -> zone-attribute -> persist ->
evaluate rules. Shared so the upload Celery task, the live RTSP
StreamManager, and the screen-capture frame endpoint never duplicate this
logic.

This is `async` (it awaits the inference provider directly) rather than
wrapping itself in `asyncio.run()` — that would break when called from an
already-async context (e.g. a FastAPI endpoint), since you can't nest event
loops. Each caller runs it appropriately for its own context: Celery tasks
and the StreamManager (plain sync code, no loop running) use
`asyncio.run(process_frame(...))`; async FastAPI endpoints just `await` it.
"""

import uuid
from datetime import datetime

from sqlalchemy.orm import Session

from cip.models.camera import Camera
from cip.models.detection_event import DetectionEvent
from cip.models.zone import Zone
from cip.services.inference.base import InferenceProvider
from cip.services.ingestion.storage import put_object
from cip.services.rule_engine.evaluator import evaluate_rules_for_camera
from cip.services.tracking_service import SessionTracker
from cip.services.zone_engine.point_in_polygon import find_containing_zone_name


async def process_frame(
    db: Session,
    provider: InferenceProvider,
    tracker: SessionTracker,
    camera_id: uuid.UUID,
    timestamp: datetime,
    frame_bytes: bytes,
    video_session_id: uuid.UUID | None = None,
) -> list[DetectionEvent]:
    _capture_reference_frame_if_missing(db, camera_id, frame_bytes)

    detections = await provider.detect_objects(frame_bytes)
    zones = db.query(Zone).filter(Zone.camera_id == camera_id).all()

    events = []
    for detection, track_id in tracker.update(detections):
        event = DetectionEvent(
            camera_id=camera_id,
            video_session_id=video_session_id,
            timestamp=timestamp,
            track_id=track_id,
            object_type=detection.object_type,
            confidence=detection.confidence,
            bounding_box=detection.bounding_box,
            zone=find_containing_zone_name(detection.bounding_box, zones) if zones else None,
        )
        db.add(event)
        events.append(event)

    if events:
        db.flush()
        evaluate_rules_for_camera(db, camera_id)

    return events


def _capture_reference_frame_if_missing(
    db: Session, camera_id: uuid.UUID, frame_bytes: bytes
) -> None:
    """Zone drawing needs some image to draw polygons on. Lazily save the
    first processed frame as that reference — cheap (one write, one time per
    camera) and means a camera becomes zone-editable as soon as it has any
    frame at all, without a separate capture step. No automatic re-capture
    if the camera's framing changes later (known limitation — would need an
    explicit "recapture" action, not built yet).
    """
    camera = db.get(Camera, camera_id)
    if camera is None or camera.reference_frame_key is not None:
        return
    key = f"reference-frames/{camera_id}.jpg"
    put_object(key, frame_bytes, content_type="image/jpeg")
    camera.reference_frame_key = key
