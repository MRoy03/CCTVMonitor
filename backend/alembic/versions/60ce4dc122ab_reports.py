"""reports

Revision ID: 60ce4dc122ab
Revises: b7f3c9a1e802
Create Date: 2026-10-26

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "60ce4dc122ab"
down_revision: str | None = "b7f3c9a1e802"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    report_type = postgresql.ENUM(
        "DAILY", "SHIFT", "EXCEPTION", "INCIDENT", "SUMMARY", name="reporttype", create_type=True
    )
    op.create_table(
        "reports",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "camera_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("cameras.id"), nullable=False
        ),
        sa.Column("report_type", report_type, nullable=False),
        sa.Column("period_start", sa.DateTime(timezone=True), nullable=False),
        sa.Column("period_end", sa.DateTime(timezone=True), nullable=False),
        sa.Column("report_text", sa.Text, nullable=False),
        sa.Column("structured_data", postgresql.JSONB, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_reports_camera_id", "reports", ["camera_id"])


def downgrade() -> None:
    op.drop_table("reports")
    op.execute("DROP TYPE IF EXISTS reporttype")
