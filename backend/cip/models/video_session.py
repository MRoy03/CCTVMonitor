import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cip.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from cip.models.camera import Camera
    from cip.models.detection_event import DetectionEvent


class VideoSessionStatus(str, enum.Enum):
    QUEUED = "QUEUED"
    PROCESSING = "PROCESSING"
    DONE = "DONE"
    FAILED = "FAILED"


class VideoSession(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "video_sessions"

    camera_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cameras.id"), nullable=False
    )
    source_object_key: Mapped[str | None] = mapped_column(String(1000))
    status: Mapped[VideoSessionStatus] = mapped_column(
        Enum(VideoSessionStatus), default=VideoSessionStatus.QUEUED
    )
    start_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    end_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    error_message: Mapped[str | None] = mapped_column(String(2000))

    camera: Mapped["Camera"] = relationship(back_populates="video_sessions")
    detection_events: Mapped[list["DetectionEvent"]] = relationship(
        back_populates="video_session"
    )
