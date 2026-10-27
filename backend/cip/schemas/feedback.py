import uuid
from datetime import datetime

from pydantic import BaseModel, model_validator

from cip.models.feedback import FeedbackVerdict


class FeedbackCreate(BaseModel):
    camera_id: str
    detection_event_id: str | None = None
    activity_event_id: str | None = None
    verdict: FeedbackVerdict
    actual_correction: dict | None = None
    notes: str | None = None

    @model_validator(mode="after")
    def _not_both_events(self) -> "FeedbackCreate":
        if self.detection_event_id and self.activity_event_id:
            raise ValueError("Feedback is for one event — provide at most one of the two ids")
        has_event = self.detection_event_id or self.activity_event_id
        if self.verdict != FeedbackVerdict.MISSED_EVENT and not has_event:
            raise ValueError(
                "detection_event_id or activity_event_id is required unless verdict is MISSED_EVENT"
            )
        return self


class FeedbackResponse(BaseModel):
    id: uuid.UUID
    camera_id: uuid.UUID
    detection_event_id: uuid.UUID | None
    activity_event_id: uuid.UUID | None
    verdict: FeedbackVerdict
    prediction: dict
    actual_correction: dict | None
    notes: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class FeedbackStats(BaseModel):
    total: int
    correct: int
    incorrect: int
    ignored: int
    missed_event: int
    accuracy: float | None  # correct / (correct + incorrect), None if no graded feedback yet
