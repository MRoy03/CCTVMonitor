import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import JSON, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cip.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from cip.models.rule import Rule

JSONType = JSONB().with_variant(JSON(), "sqlite")


class RuleState(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Per-(rule, entity) cooldown/in-progress state, persisted so it
    survives worker restarts. `entity_key` identifies what the state is
    about within the rule's scope, e.g. "track:5" for a specific tracked
    object — a rule with no per-entity state just uses a constant key.
    """

    __tablename__ = "rule_states"
    __table_args__ = (UniqueConstraint("rule_id", "entity_key", name="uq_rule_state_entity"),)

    rule_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("rules.id"), nullable=False
    )
    entity_key: Mapped[str] = mapped_column(String(255), nullable=False)
    state: Mapped[dict] = mapped_column(JSONType, default=dict)
    last_triggered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    rule: Mapped["Rule"] = relationship()
