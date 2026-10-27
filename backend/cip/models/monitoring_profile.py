import uuid
from typing import TYPE_CHECKING

from sqlalchemy import JSON, Boolean, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cip.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from cip.models.camera import Camera

JSONType = JSONB().with_variant(JSON(), "sqlite")


class MonitoringProfile(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Bundles zones/rules/alert policy/report style under a reusable, named config.

    This is the mechanism that keeps the platform config-driven: a new
    "monitoring type" (warehouse, PPE, gate, retail, ...) is a new profile,
    never a new code path.
    """

    __tablename__ = "monitoring_profiles"

    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    use_case: Mapped[str] = mapped_column(String(50), default="custom")
    detection_classes: Mapped[list | None] = mapped_column(JSONType)
    vlm_prompts: Mapped[dict | None] = mapped_column(JSONType)
    report_schedule: Mapped[dict | None] = mapped_column(JSONType)
    alert_policy: Mapped[dict | None] = mapped_column(JSONType)
    is_system_template: Mapped[bool] = mapped_column(Boolean, default=False)

    cameras: Mapped[list["Camera"]] = relationship(back_populates="monitoring_profile")
