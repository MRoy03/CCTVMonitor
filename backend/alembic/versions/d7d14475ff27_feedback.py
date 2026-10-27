"""feedback

Revision ID: d7d14475ff27
Revises: 60ce4dc122ab
Create Date: 2026-10-26

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "d7d14475ff27"
down_revision: str | None = "60ce4dc122ab"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    verdict = postgresql.ENUM(
        "CORRECT",
        "INCORRECT",
        "IGNORED",
        "MISSED_EVENT",
        name="feedbackverdict",
        create_type=True,
    )
    op.create_table(
        "feedback",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "camera_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("cameras.id"), nullable=False
        ),
        sa.Column(
            "detection_event_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("detection_events.id"),
        ),
        sa.Column(
            "activity_event_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("activity_events.id")
        ),
        sa.Column(
            "user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False
        ),
        sa.Column("user_feedback", verdict, nullable=False),
        sa.Column("prediction", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("actual_correction", postgresql.JSONB),
        sa.Column("notes", sa.String(1000)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_feedback_camera_id", "feedback", ["camera_id"])
    op.create_index("ix_feedback_detection_event_id", "feedback", ["detection_event_id"])
    op.create_index("ix_feedback_activity_event_id", "feedback", ["activity_event_id"])


def downgrade() -> None:
    op.drop_table("feedback")
    op.execute("DROP TYPE IF EXISTS feedbackverdict")
