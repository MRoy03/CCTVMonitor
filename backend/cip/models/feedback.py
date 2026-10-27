import enum
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import JSON, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cip.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from cip.models.activity_event import ActivityEvent
    from cip.models.camera import Camera
    from cip.models.detection_event import DetectionEvent
    from cip.models.user import User

JSONType = JSONB().with_variant(JSON(), "sqlite")


class FeedbackVerdict(str, enum.Enum):
    CORRECT = "CORRECT"
    INCORRECT = "INCORRECT"
    IGNORED = "IGNORED"
    MISSED_EVENT = "MISSED_EVENT"


class Feedback(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A human correction on one AI output (or, for MISSED_EVENT, a report
    that the AI produced *no* output when it should have — both
    detection_event_id and activity_event_id are null in that case).
    `prediction` is a snapshot taken at feedback time so this stays
    meaningful even if the source DetectionEvent/ActivityEvent is later
    deleted. No retraining happens on this data yet (Phase 9's job) — this
    phase is purely collection, per the plan's "supervised learning first,
    no RLHF" instruction.
    """

    __tablename__ = "feedback"

    camera_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cameras.id"), nullable=False
    )
    detection_event_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("detection_events.id")
    )
    activity_event_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("activity_events.id")
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    verdict: Mapped[FeedbackVerdict] = mapped_column(
        "user_feedback", Enum(FeedbackVerdict), nullable=False
    )
    prediction: Mapped[dict] = mapped_column(JSONType, default=dict)
    actual_correction: Mapped[dict | None] = mapped_column(JSONType)
    notes: Mapped[str | None] = mapped_column(String(1000))

    camera: Mapped["Camera"] = relationship()
    detection_event: Mapped["DetectionEvent | None"] = relationship()
    activity_event: Mapped["ActivityEvent | None"] = relationship()
    user: Mapped["User"] = relationship()
