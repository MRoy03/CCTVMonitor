import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cip.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from cip.models.location import Location
    from cip.models.monitoring_profile import MonitoringProfile
    from cip.models.video_session import VideoSession
    from cip.models.zone import Zone


class SourceType(str, enum.Enum):
    RTSP = "RTSP"
    UPLOAD = "UPLOAD"
    SCREEN_CAPTURE = "SCREEN_CAPTURE"


class CameraStatus(str, enum.Enum):
    ONLINE = "ONLINE"
    OFFLINE = "OFFLINE"
    PROCESSING = "PROCESSING"
    UNKNOWN = "UNKNOWN"


class Camera(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "cameras"

    location_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("locations.id"), nullable=False
    )
    monitoring_profile_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("monitoring_profiles.id")
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    source_type: Mapped[SourceType] = mapped_column(Enum(SourceType), nullable=False)
    stream_url: Mapped[str | None] = mapped_column(String(1000))
    status: Mapped[CameraStatus] = mapped_column(
        Enum(CameraStatus), default=CameraStatus.UNKNOWN
    )
    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    reference_frame_key: Mapped[str | None] = mapped_column(String(1000))

    location: Mapped["Location"] = relationship(back_populates="cameras")
    monitoring_profile: Mapped["MonitoringProfile | None"] = relationship(
        back_populates="cameras"
    )
    video_sessions: Mapped[list["VideoSession"]] = relationship(back_populates="camera")
    zones: Mapped[list["Zone"]] = relationship(back_populates="camera")
