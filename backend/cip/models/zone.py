import uuid
from typing import TYPE_CHECKING

from sqlalchemy import JSON, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cip.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from cip.models.camera import Camera

JSONType = JSONB().with_variant(JSON(), "sqlite")


class Zone(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A named polygon on a camera's reference frame, in normalized 0-1
    coordinates. Drawing UI lands in Phase 4 alongside the Rule Engine that
    actually consumes zone membership; this table exists now so cameras
    created in Phase 2 already have somewhere to attach zones later without
    a schema migration blocking that work.
    """

    __tablename__ = "zones"

    camera_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cameras.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    polygon_coordinates: Mapped[list] = mapped_column(JSONType, nullable=False)

    camera: Mapped["Camera"] = relationship(back_populates="zones")
