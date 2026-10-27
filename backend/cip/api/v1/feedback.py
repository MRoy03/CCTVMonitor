import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from cip.api.deps import get_current_user
from cip.db.session import get_db
from cip.models.activity_event import ActivityEvent
from cip.models.camera import Camera
from cip.models.detection_event import DetectionEvent
from cip.models.feedback import Feedback, FeedbackVerdict
from cip.models.user import User
from cip.schemas.feedback import FeedbackCreate, FeedbackResponse, FeedbackStats

router = APIRouter(tags=["feedback"])


def _camera_in_org(db: Session, camera_id: str, organization_id) -> Camera:
    camera = db.get(Camera, uuid.UUID(camera_id))
    if camera is None or camera.location.organization_id != organization_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Camera not found")
    return camera


def _snapshot_prediction(db: Session, payload: FeedbackCreate, camera_id: uuid.UUID) -> dict:
    """Captures what the AI actually produced at feedback time, so this
    stays meaningful even if the source row is later deleted.
    """
    if payload.detection_event_id:
        event = db.get(DetectionEvent, uuid.UUID(payload.detection_event_id))
        if event is None or event.camera_id != camera_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Detection event not found"
            )
        return {
            "object_type": event.object_type,
            "confidence": event.confidence,
            "bounding_box": event.bounding_box,
            "zone": event.zone,
        }

    if payload.activity_event_id:
        event = db.get(ActivityEvent, uuid.UUID(payload.activity_event_id))
        if event is None or event.camera_id != camera_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Activity event not found"
            )
        return {
            "event_type": event.event_type,
            "severity": event.severity.value,
            "description": event.description,
        }

    return {}  # MISSED_EVENT: the AI produced nothing to snapshot


@router.post("/feedback", response_model=FeedbackResponse)
def create_feedback(
    payload: FeedbackCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Feedback:
    camera = _camera_in_org(db, payload.camera_id, current_user.organization_id)
    prediction = _snapshot_prediction(db, payload, camera.id)

    feedback = Feedback(
        camera_id=camera.id,
        detection_event_id=(
            uuid.UUID(payload.detection_event_id) if payload.detection_event_id else None
        ),
        activity_event_id=(
            uuid.UUID(payload.activity_event_id) if payload.activity_event_id else None
        ),
        user_id=current_user.id,
        verdict=payload.verdict,
        prediction=prediction,
        actual_correction=payload.actual_correction,
        notes=payload.notes,
    )
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    return feedback


@router.get("/cameras/{camera_id}/feedback", response_model=list[FeedbackResponse])
def list_feedback(
    camera_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[Feedback]:
    camera = _camera_in_org(db, camera_id, current_user.organization_id)
    return (
        db.query(Feedback)
        .filter(Feedback.camera_id == camera.id)
        .order_by(Feedback.created_at.desc())
        .all()
    )


@router.get("/cameras/{camera_id}/feedback/stats", response_model=FeedbackStats)
def feedback_stats(
    camera_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> FeedbackStats:
    camera = _camera_in_org(db, camera_id, current_user.organization_id)
    rows = db.query(Feedback).filter(Feedback.camera_id == camera.id).all()

    counts = {verdict: 0 for verdict in FeedbackVerdict}
    for row in rows:
        counts[row.verdict] += 1

    graded = counts[FeedbackVerdict.CORRECT] + counts[FeedbackVerdict.INCORRECT]
    accuracy = counts[FeedbackVerdict.CORRECT] / graded if graded else None

    return FeedbackStats(
        total=len(rows),
        correct=counts[FeedbackVerdict.CORRECT],
        incorrect=counts[FeedbackVerdict.INCORRECT],
        ignored=counts[FeedbackVerdict.IGNORED],
        missed_event=counts[FeedbackVerdict.MISSED_EVENT],
        accuracy=accuracy,
    )
