"""Periodic sweep so duration-based conditions fire even without new
detections — e.g. "desk empty for 15 minutes" has no new DetectionEvents to
react to once the desk has been empty a while; only a periodic re-check
notices that enough time has now passed. Event-driven evaluation (right
after process_frame persists new detections) stays the fast path for
everything else; this is the safety net.
"""

from cip.celery_app import celery_app
from cip.db.session import SessionLocal
from cip.models.rule import Rule
from cip.services.rule_engine.evaluator import evaluate_rules_for_camera


@celery_app.task(name="cip.evaluate_all_rules")
def evaluate_all_rules() -> None:
    db = SessionLocal()
    try:
        camera_ids = {
            row[0]
            for row in db.query(Rule.camera_id).filter(Rule.enabled.is_(True)).distinct().all()
            if row[0] is not None
        }
        for camera_id in camera_ids:
            evaluate_rules_for_camera(db, camera_id)
    finally:
        db.close()
