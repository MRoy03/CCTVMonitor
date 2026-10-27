"""initial schema

Revision ID: 12462f768a3b
Revises:
Create Date: 2026-10-22

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "12462f768a3b"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "organizations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "locations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "organization_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("organizations.id"),
            nullable=False,
        ),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("address", sa.String(500)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "organization_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("organizations.id"),
            nullable=False,
        ),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(255)),
        sa.Column("role", sa.String(50), nullable=False, server_default="org_admin"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "monitoring_profiles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "organization_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("organizations.id"),
            nullable=False,
        ),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("use_case", sa.String(50), nullable=False, server_default="custom"),
        sa.Column("detection_classes", postgresql.JSONB),
        sa.Column("vlm_prompts", postgresql.JSONB),
        sa.Column("report_schedule", postgresql.JSONB),
        sa.Column("alert_policy", postgresql.JSONB),
        sa.Column("is_system_template", sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    source_type = postgresql.ENUM(
        "RTSP", "UPLOAD", "SCREEN_CAPTURE", name="sourcetype", create_type=True
    )
    camera_status = postgresql.ENUM(
        "ONLINE", "OFFLINE", "PROCESSING", "UNKNOWN", name="camerastatus", create_type=True
    )
    op.create_table(
        "cameras",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "location_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("locations.id"),
            nullable=False,
        ),
        sa.Column(
            "monitoring_profile_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("monitoring_profiles.id"),
        ),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("source_type", source_type, nullable=False),
        sa.Column("stream_url", sa.String(1000)),
        sa.Column("status", camera_status, nullable=False, server_default="UNKNOWN"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    session_status = postgresql.ENUM(
        "QUEUED", "PROCESSING", "DONE", "FAILED", name="videosessionstatus", create_type=True
    )
    op.create_table(
        "video_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "camera_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("cameras.id"), nullable=False
        ),
        sa.Column("source_object_key", sa.String(1000)),
        sa.Column("status", session_status, nullable=False, server_default="QUEUED"),
        sa.Column("start_time", sa.DateTime(timezone=True)),
        sa.Column("end_time", sa.DateTime(timezone=True)),
        sa.Column("error_message", sa.String(2000)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "detection_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "camera_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("cameras.id"), nullable=False
        ),
        sa.Column(
            "video_session_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("video_sessions.id")
        ),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("frame_sequence", sa.Integer),
        sa.Column("track_id", sa.Integer),
        sa.Column("object_type", sa.String(100), nullable=False),
        sa.Column("confidence", sa.Float, nullable=False),
        sa.Column("bounding_box", postgresql.JSONB, nullable=False),
        sa.Column("zone", sa.String(255)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index(
        "ix_detection_events_video_session_id", "detection_events", ["video_session_id"]
    )
    op.create_index("ix_detection_events_camera_id", "detection_events", ["camera_id"])


def downgrade() -> None:
    op.drop_table("detection_events")
    op.drop_table("video_sessions")
    op.drop_table("cameras")
    op.execute("DROP TYPE IF EXISTS videosessionstatus")
    op.execute("DROP TYPE IF EXISTS camerastatus")
    op.execute("DROP TYPE IF EXISTS sourcetype")
    op.drop_table("monitoring_profiles")
    op.drop_table("users")
    op.drop_table("locations")
    op.drop_table("organizations")
