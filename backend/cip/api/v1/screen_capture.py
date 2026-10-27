import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from cip.api.deps import get_current_user
from cip.db.session import get_db
from cip.models.camera import Camera, CameraStatus, SourceType
from cip.models.user import User
from cip.services.frame_processor import process_frame
from cip.services.inference.provider_registry import get_inference_provider
from cip.services.ingestion.live_tracker_registry import get_tracker

router = APIRouter(tags=["screen-capture"])


@router.post("/cameras/{camera_id}/frames")
async def ingest_frame(
    camera_id: str,
    file: UploadFile,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """Accepts one JPEG frame from a browser screen-capture session and runs
    it through the same detect->track->persist pipeline the upload and RTSP
    paths use. Called repeatedly (every couple seconds) by the frontend's
    capture loop for as long as that browser tab keeps sharing its screen.
    """
    camera = db.get(Camera, uuid.UUID(camera_id))
    if camera is None or camera.location.organization_id != current_user.organization_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Camera not found")
    if camera.source_type != SourceType.SCREEN_CAPTURE:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Camera is not a screen-capture source",
        )

    frame_bytes = await file.read()
    provider = get_inference_provider()
    tracker = get_tracker(camera.id)

    await process_frame(
        db=db,
        provider=provider,
        tracker=tracker,
        camera_id=camera.id,
        timestamp=datetime.now(timezone.utc),
        frame_bytes=frame_bytes,
    )
    camera.status = CameraStatus.ONLINE
    camera.last_seen_at = datetime.now(timezone.utc)
    db.commit()

    return {"ok": True}
