import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cip.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from cip.models.video_session import VideoSession

JSONType = JSONB().with_variant(JSON(), "sqlite")


class DetectionEvent(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """One raw per-frame detection, as returned by the inference provider."""

    __tablename__ = "detection_events"

    camera_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cameras.id"), nullable=False
    )
    video_session_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("video_sessions.id")
    )
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    frame_sequence: Mapped[int | None] = mapped_column(Integer)
    track_id: Mapped[int | None] = mapped_column(Integer)
    object_type: Mapped[str] = mapped_column(String(100), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    bounding_box: Mapped[dict] = mapped_column(JSONType, nullable=False)
    zone: Mapped[str | None] = mapped_column(String(255))

    video_session: Mapped["VideoSession | None"] = relationship(
        back_populates="detection_events"
    )
