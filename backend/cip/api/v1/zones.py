import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from cip.api.deps import get_current_user
from cip.db.session import get_db
from cip.models.camera import Camera
from cip.models.user import User
from cip.models.zone import Zone
from cip.schemas.zone import ZoneCreate, ZoneResponse

router = APIRouter(tags=["zones"])


def _camera_in_org(db: Session, camera_id: str, organization_id) -> Camera:
    camera = db.get(Camera, uuid.UUID(camera_id))
    if camera is None or camera.location.organization_id != organization_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Camera not found")
    return camera


@router.post("/cameras/{camera_id}/zones", response_model=ZoneResponse)
def create_zone(
    camera_id: str,
    payload: ZoneCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Zone:
    camera = _camera_in_org(db, camera_id, current_user.organization_id)
    zone = Zone(
        camera_id=camera.id,
        name=payload.name,
        polygon_coordinates=payload.polygon_coordinates,
    )
    db.add(zone)
    db.commit()
    db.refresh(zone)
    return zone


@router.get("/cameras/{camera_id}/zones", response_model=list[ZoneResponse])
def list_zones(
    camera_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[Zone]:
    camera = _camera_in_org(db, camera_id, current_user.organization_id)
    return db.query(Zone).filter(Zone.camera_id == camera.id).all()


@router.delete("/zones/{zone_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_zone(
    zone_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    zone = db.get(Zone, uuid.UUID(zone_id))
    if zone is None or zone.camera.location.organization_id != current_user.organization_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Zone not found")
    db.delete(zone)
    db.commit()
