import uuid
from datetime import datetime

from pydantic import BaseModel

from cip.models.video_session import VideoSessionStatus


class VideoSessionResponse(BaseModel):
    id: uuid.UUID
    camera_id: uuid.UUID
    status: VideoSessionStatus
    start_time: datetime | None
    end_time: datetime | None
    error_message: str | None

    model_config = {"from_attributes": True}


class DetectionEventResponse(BaseModel):
    id: uuid.UUID
    timestamp: datetime
    track_id: int | None
    object_type: str
    confidence: float
    bounding_box: dict
    zone: str | None

    model_config = {"from_attributes": True}
