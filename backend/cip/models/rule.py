import uuid
from typing import TYPE_CHECKING

from sqlalchemy import JSON, Boolean, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cip.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from cip.models.activity_event import ActivityEvent

JSONType = JSONB().with_variant(JSON(), "sqlite")


class Rule(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A no-code IF/THEN rule. `conditions` is a single condition node (or an
    and/or/not composite of them); `actions` is a list. Both are JSON so the
    supported vocabulary can grow without new tables/migrations — see
    cip/services/rule_engine/schema.py for the condition/action type registry.
    """

    __tablename__ = "rules"

    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False
    )
    camera_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cameras.id")
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    conditions: Mapped[dict] = mapped_column(JSONType, nullable=False)
    actions: Mapped[list] = mapped_column(JSONType, nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    cooldown_seconds: Mapped[int] = mapped_column(Integer, default=300)

    activity_events: Mapped[list["ActivityEvent"]] = relationship(back_populates="rule")
