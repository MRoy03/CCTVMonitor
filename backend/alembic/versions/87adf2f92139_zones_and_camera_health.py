"""zones and camera health

Revision ID: 87adf2f92139
Revises: 12462f768a3b
Create Date: 2026-10-23

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "87adf2f92139"
down_revision: str | None = "12462f768a3b"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("cameras", sa.Column("last_seen_at", sa.DateTime(timezone=True)))

    op.create_table(
        "zones",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "camera_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("cameras.id"), nullable=False
        ),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("polygon_coordinates", postgresql.JSONB, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_zones_camera_id", "zones", ["camera_id"])


def downgrade() -> None:
    op.drop_table("zones")
    op.drop_column("cameras", "last_seen_at")
