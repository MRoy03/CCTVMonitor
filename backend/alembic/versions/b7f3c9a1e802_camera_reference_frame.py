"""camera reference frame

Revision ID: b7f3c9a1e802
Revises: a2d4115d6e46
Create Date: 2026-10-26

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "b7f3c9a1e802"
down_revision: str | None = "a2d4115d6e46"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("cameras", sa.Column("reference_frame_key", sa.String(1000)))


def downgrade() -> None:
    op.drop_column("cameras", "reference_frame_key")
