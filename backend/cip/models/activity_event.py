import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cip.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from cip.models.camera import Camera
    from cip.models.rule import Rule
    from cip.models.zone import Zone


class Severity(str, enum.Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


class ActivityEvent(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A higher-level event derived from raw detections — here, always the
    result of a Rule's condition being met (an "incident" or "observation",
    per the rule's action). Distinct from DetectionEvents, which are raw
    per-frame AI output.
    """

    __tablename__ = "activity_events"

    camera_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cameras.id"), nullable=False
    )
    zone_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("zones.id"))
    rule_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("rules.id"))
    track_id: Mapped[int | None] = mapped_column(Integer)
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    severity: Mapped[Severity] = mapped_column(Enum(Severity), default=Severity.INFO)
    description: Mapped[str] = mapped_column(String(1000), nullable=False)

    camera: Mapped["Camera"] = relationship()
    zone: Mapped["Zone | None"] = relationship()
    rule: Mapped["Rule | None"] = relationship(back_populates="activity_events")
