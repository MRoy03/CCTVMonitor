"""Pulls the structured facts a report is built from: distinct objects seen
(by type) and the incidents/observations rules created, for one camera over
one time window. This structured table is stored in Report.structured_data
regardless of whether the LLM narrative succeeds, so the UI always has
something real to render even if report-writing text generation fails.
"""

from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Session

from cip.models.activity_event import ActivityEvent
from cip.models.camera import Camera
from cip.models.detection_event import DetectionEvent


def aggregate_report_data(
    db: Session, camera: Camera, period_start: datetime, period_end: datetime
) -> dict:
    detection_counts = (
        db.query(DetectionEvent.object_type, func.count(func.distinct(DetectionEvent.track_id)))
        .filter(
            DetectionEvent.camera_id == camera.id,
            DetectionEvent.timestamp >= period_start,
            DetectionEvent.timestamp < period_end,
        )
        .group_by(DetectionEvent.object_type)
        .all()
    )
    detection_summary = {object_type: count for object_type, count in detection_counts}

    activity_events = (
        db.query(ActivityEvent)
        .filter(
            ActivityEvent.camera_id == camera.id,
            ActivityEvent.start_time >= period_start,
            ActivityEvent.start_time < period_end,
        )
        .order_by(ActivityEvent.start_time)
        .all()
    )
    rows = [
        {
            "timestamp": event.start_time.isoformat(),
            "event": event.event_type,
            "zone": event.zone.name if event.zone else None,
            "severity": event.severity.value,
            "observation": event.description,
        }
        for event in activity_events
    ]

    return {
        "camera_name": camera.name,
        "period_start": period_start.isoformat(),
        "period_end": period_end.isoformat(),
        "detection_summary": detection_summary,
        "rows": rows,
    }
