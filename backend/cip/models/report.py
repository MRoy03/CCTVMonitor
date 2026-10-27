import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import JSON, DateTime, Enum, ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cip.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from cip.models.camera import Camera

JSONType = JSONB().with_variant(JSON(), "sqlite")


class ReportType(str, enum.Enum):
    DAILY = "DAILY"
    SHIFT = "SHIFT"
    EXCEPTION = "EXCEPTION"
    INCIDENT = "INCIDENT"
    SUMMARY = "SUMMARY"


class Report(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A generated report for one camera over a time window. Scoped to a
    single camera for V1 (matches how Zones/Rules are scoped so far);
    cross-camera/location rollups are Phase 7's job once multi-location
    support exists.
    """

    __tablename__ = "reports"

    camera_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cameras.id"), nullable=False
    )
    report_type: Mapped[ReportType] = mapped_column(Enum(ReportType), nullable=False)
    period_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    period_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    report_text: Mapped[str] = mapped_column(Text, nullable=False)
    structured_data: Mapped[dict] = mapped_column(JSONType, nullable=False)

    camera: Mapped["Camera"] = relationship()
