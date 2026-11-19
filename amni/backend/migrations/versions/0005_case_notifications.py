"""Add durable, event-linked in-app notifications."""
from alembic import op
import sqlalchemy as sa

revision = "0005_case_notifications"
down_revision = "0004_case_events"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "notifications",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("recipient_id", sa.Uuid(), nullable=False),
        sa.Column("case_id", sa.Uuid(), nullable=False),
        sa.Column("event_id", sa.Uuid(), nullable=False),
        sa.Column("kind", sa.String(24), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_notifications"),
        sa.ForeignKeyConstraint(["recipient_id"], ["users.id"], ondelete="CASCADE", name="fk_notifications_recipient_id_users"),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"], ondelete="RESTRICT", name="fk_notifications_case_id_cases"),
        sa.ForeignKeyConstraint(["event_id", "case_id"], ["case_events.id", "case_events.case_id"], ondelete="RESTRICT", name="fk_notifications_event_case"),
        sa.UniqueConstraint("recipient_id", "event_id", name="uq_notifications_recipient_event"),
        sa.CheckConstraint("kind IN ('case_created', 'case_assigned', 'case_resolved', 'case_reopened')", name="ck_notifications_kind_valid"),
        sa.CheckConstraint("char_length(btrim(message)) > 0", name="ck_notifications_message_not_blank"),
        sa.CheckConstraint("read_at IS NULL OR read_at >= created_at", name="ck_notifications_read_after_creation"),
    )
    op.create_index("ix_notifications_unread", "notifications", ["recipient_id", "created_at"], postgresql_where=sa.text("read_at IS NULL"))
    op.create_index("ix_notifications_case_id", "notifications", ["case_id"])


def downgrade():
    op.drop_table("notifications")
