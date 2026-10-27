import uuid
from datetime import datetime

from pydantic import BaseModel

from cip.models.activity_event import Severity


class ActivityEventResponse(BaseModel):
    id: uuid.UUID
    camera_id: uuid.UUID
    zone_id: uuid.UUID | None
    rule_id: uuid.UUID | None
    track_id: int | None
    start_time: datetime
    end_time: datetime | None
    event_type: str
    severity: Severity
    description: str

    model_config = {"from_attributes": True}
