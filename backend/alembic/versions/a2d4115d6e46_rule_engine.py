"""rule engine: activity_events, rules, rule_states

Revision ID: a2d4115d6e46
Revises: 87adf2f92139
Create Date: 2026-10-26

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "a2d4115d6e46"
down_revision: str | None = "87adf2f92139"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "rules",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "organization_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("organizations.id"),
            nullable=False,
        ),
        sa.Column("camera_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("cameras.id")),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("conditions", postgresql.JSONB, nullable=False),
        sa.Column("actions", postgresql.JSONB, nullable=False),
        sa.Column("enabled", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column("cooldown_seconds", sa.Integer, nullable=False, server_default="300"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_rules_camera_id", "rules", ["camera_id"])
    op.create_index("ix_rules_organization_id", "rules", ["organization_id"])

    op.create_table(
        "rule_states",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "rule_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("rules.id"), nullable=False
        ),
        sa.Column("entity_key", sa.String(255), nullable=False),
        sa.Column("state", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("last_triggered_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("rule_id", "entity_key", name="uq_rule_state_entity"),
    )

    severity = postgresql.ENUM("INFO", "WARNING", "CRITICAL", name="severity", create_type=True)
    op.create_table(
        "activity_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "camera_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("cameras.id"), nullable=False
        ),
        sa.Column("zone_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("zones.id")),
        sa.Column("rule_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("rules.id")),
        sa.Column("track_id", sa.Integer),
        sa.Column("start_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_time", sa.DateTime(timezone=True)),
        sa.Column("event_type", sa.String(100), nullable=False),
        sa.Column("severity", severity, nullable=False, server_default="INFO"),
        sa.Column("description", sa.String(1000), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_activity_events_camera_id", "activity_events", ["camera_id"])


def downgrade() -> None:
    op.drop_table("activity_events")
    op.execute("DROP TYPE IF EXISTS severity")
    op.drop_table("rule_states")
    op.drop_table("rules")
