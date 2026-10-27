import uuid
from datetime import datetime

from pydantic import BaseModel

from cip.models.camera import CameraStatus, SourceType


class CameraCreate(BaseModel):
    location_id: str
    name: str
    source_type: SourceType
    stream_url: str | None = None
    monitoring_profile_id: str | None = None


class CameraResponse(BaseModel):
    id: uuid.UUID
    location_id: uuid.UUID
    name: str
    source_type: SourceType
    stream_url: str | None
    status: CameraStatus
    last_seen_at: datetime | None
    monitoring_profile_id: uuid.UUID | None

    model_config = {"from_attributes": True}


class LocationCreate(BaseModel):
    name: str
    address: str | None = None


class LocationResponse(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    name: str
    address: str | None

    model_config = {"from_attributes": True}
