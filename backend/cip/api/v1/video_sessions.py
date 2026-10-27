import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from cip.api.deps import get_current_user
from cip.db.session import get_db
from cip.models.camera import Camera
from cip.models.detection_event import DetectionEvent
from cip.models.user import User
from cip.models.video_session import VideoSession
from cip.schemas.video_session import DetectionEventResponse, VideoSessionResponse
from cip.services.ingestion.storage import ensure_bucket, get_presigned_url, put_object
from cip.workers.tasks_ingestion import process_uploaded_video

router = APIRouter(tags=["video-sessions"])

ALLOWED_EXTENSIONS = {".mp4", ".avi", ".mov", ".mkv", ".webm"}


def _camera_in_org(db: Session, camera_id: str, organization_id) -> Camera:
    camera = db.get(Camera, uuid.UUID(camera_id))
    if camera is None or camera.location.organization_id != organization_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Camera not found")
    return camera


@router.post("/cameras/{camera_id}/video-sessions", response_model=VideoSessionResponse)
async def upload_video(
    camera_id: str,
    file: UploadFile,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> VideoSession:
    camera = _camera_in_org(db, camera_id, current_user.organization_id)

    extension = "." + file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Unsupported format {extension}, expected one of {sorted(ALLOWED_EXTENSIONS)}",
        )

    session = VideoSession(camera_id=camera.id)
    db.add(session)
    db.flush()

    object_key = f"videos/{current_user.organization_id}/{camera.id}/{session.id}{extension}"
    ensure_bucket()
    put_object(object_key, await file.read(), content_type=file.content_type or "video/mp4")
    session.source_object_key = object_key
    db.commit()
    db.refresh(session)

    process_uploaded_video.delay(str(session.id))
    return session


@router.get("/cameras/{camera_id}/video-sessions", response_model=list[VideoSessionResponse])
def list_video_sessions(
    camera_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[VideoSession]:
    camera = _camera_in_org(db, camera_id, current_user.organization_id)
    return (
        db.query(VideoSession)
        .filter(VideoSession.camera_id == camera.id)
        .order_by(VideoSession.created_at.desc())
        .all()
    )


@router.get("/video-sessions/{session_id}", response_model=VideoSessionResponse)
def get_video_session(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> VideoSession:
    session = db.get(VideoSession, uuid.UUID(session_id))
    if session is None or session.camera.location.organization_id != current_user.organization_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video session not found")
    return session


@router.get("/video-sessions/{session_id}/video-url")
def get_video_url(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    session = db.get(VideoSession, uuid.UUID(session_id))
    if session is None or session.camera.location.organization_id != current_user.organization_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video session not found")
    if not session.source_object_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No video stored for this session"
        )
    return {"url": get_presigned_url(session.source_object_key)}


@router.get(
    "/video-sessions/{session_id}/detections", response_model=list[DetectionEventResponse]
)
def list_detections(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[DetectionEvent]:
    session = db.get(VideoSession, uuid.UUID(session_id))
    if session is None or session.camera.location.organization_id != current_user.organization_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video session not found")
    return (
        db.query(DetectionEvent)
        .filter(DetectionEvent.video_session_id == session.id)
        .order_by(DetectionEvent.timestamp)
        .all()
    )
