import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from cip.api.deps import get_current_user
from cip.db.session import get_db
from cip.models.activity_event import ActivityEvent
from cip.models.camera import Camera, SourceType
from cip.models.detection_event import DetectionEvent
from cip.models.location import Location
from cip.models.user import User
from cip.schemas.activity_event import ActivityEventResponse
from cip.schemas.camera import CameraCreate, CameraResponse
from cip.schemas.video_session import DetectionEventResponse
from cip.services.ingestion.storage import get_presigned_url

router = APIRouter(prefix="/cameras", tags=["cameras"])


def _location_in_org(db: Session, location_id: str, organization_id) -> Location:
    location = db.get(Location, uuid.UUID(location_id))
    if location is None or location.organization_id != organization_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Location not found")
    return location


@router.post("", response_model=CameraResponse)
def create_camera(
    payload: CameraCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Camera:
    _location_in_org(db, payload.location_id, current_user.organization_id)

    if payload.source_type == SourceType.RTSP and not payload.stream_url:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="stream_url is required for RTSP cameras",
        )

    camera = Camera(
        location_id=uuid.UUID(payload.location_id),
        name=payload.name,
        source_type=payload.source_type,
        stream_url=payload.stream_url,
        monitoring_profile_id=(
            uuid.UUID(payload.monitoring_profile_id) if payload.monitoring_profile_id else None
        ),
    )
    db.add(camera)
    db.commit()
    db.refresh(camera)
    return camera


@router.get("", response_model=list[CameraResponse])
def list_cameras(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> list[Camera]:
    return (
        db.query(Camera)
        .join(Location)
        .filter(Location.organization_id == current_user.organization_id)
        .all()
    )


@router.get("/{camera_id}", response_model=CameraResponse)
def get_camera(
    camera_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Camera:
    camera = db.get(Camera, uuid.UUID(camera_id))
    if camera is None or camera.location.organization_id != current_user.organization_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Camera not found")
    return camera


@router.get("/{camera_id}/reference-frame-url")
def get_reference_frame_url(
    camera_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """The background image zone drawing happens on top of — captured
    automatically from the first frame this camera ever processed.
    """
    camera = db.get(Camera, uuid.UUID(camera_id))
    if camera is None or camera.location.organization_id != current_user.organization_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Camera not found")
    if not camera.reference_frame_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No reference frame yet — this camera hasn't processed any frames",
        )
    return {"url": get_presigned_url(camera.reference_frame_key)}


@router.get("/{camera_id}/detections", response_model=list[DetectionEventResponse])
def list_camera_detections(
    camera_id: str,
    since: datetime | None = Query(None, description="Only return detections after this time"),
    limit: int = Query(200, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[DetectionEvent]:
    """Recent detections for a camera directly (not scoped to one video
    session) — used for live polling on RTSP/screen-capture cameras.
    """
    camera = db.get(Camera, uuid.UUID(camera_id))
    if camera is None or camera.location.organization_id != current_user.organization_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Camera not found")

    query = db.query(DetectionEvent).filter(DetectionEvent.camera_id == camera.id)
    if since is not None:
        query = query.filter(DetectionEvent.timestamp > since)
    return query.order_by(DetectionEvent.timestamp.desc()).limit(limit).all()


@router.get("/{camera_id}/activity-events", response_model=list[ActivityEventResponse])
def list_camera_activity_events(
    camera_id: str,
    limit: int = Query(100, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ActivityEvent]:
    """Rule-triggered incidents/observations for a camera, most recent first."""
    camera = db.get(Camera, uuid.UUID(camera_id))
    if camera is None or camera.location.organization_id != current_user.organization_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Camera not found")

    return (
        db.query(ActivityEvent)
        .filter(ActivityEvent.camera_id == camera.id)
        .order_by(ActivityEvent.start_time.desc())
        .limit(limit)
        .all()
    )
