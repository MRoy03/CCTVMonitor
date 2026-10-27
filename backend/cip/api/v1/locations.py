from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from cip.api.deps import get_current_user
from cip.db.session import get_db
from cip.models.location import Location
from cip.models.user import User
from cip.schemas.camera import LocationCreate, LocationResponse

router = APIRouter(prefix="/locations", tags=["locations"])


@router.post("", response_model=LocationResponse)
def create_location(
    payload: LocationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Location:
    location = Location(
        organization_id=current_user.organization_id,
        name=payload.name,
        address=payload.address,
    )
    db.add(location)
    db.commit()
    db.refresh(location)
    return location


@router.get("", response_model=list[LocationResponse])
def list_locations(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> list[Location]:
    return (
        db.query(Location)
        .filter(Location.organization_id == current_user.organization_id)
        .all()
    )
