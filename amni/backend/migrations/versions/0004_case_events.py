"""Add an append-only case timeline."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision = "0004_case_events"
down_revision = "0003_case_resolutions"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "case_events",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("case_id", sa.Uuid(), nullable=False),
        sa.Column("actor_id", sa.Uuid(), nullable=False),
        sa.Column("event_type", sa.String(24), nullable=False),
        sa.Column("visibility", sa.String(16), server_default=sa.text("'internal'"), nullable=False),
        sa.Column("details", JSONB(), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_case_events"),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"], ondelete="RESTRICT", name="fk_case_events_case_id_cases"),
        sa.ForeignKeyConstraint(["actor_id"], ["users.id"], ondelete="RESTRICT", name="fk_case_events_actor_id_users"),
        sa.UniqueConstraint("id", "case_id", name="uq_case_events_notification_reference"),
        sa.CheckConstraint("event_type IN ('created', 'assigned', 'reassigned', 'started', 'resolved', 'reopened')", name="ck_case_events_type_valid"),
        sa.CheckConstraint("visibility IN ('internal', 'customer')", name="ck_case_events_visibility_valid"),
        sa.CheckConstraint("jsonb_typeof(details) = 'object'", name="ck_case_events_details_object"),
    )
    op.create_index("ix_case_events_timeline", "case_events", ["case_id", "created_at"])
    op.execute("""
        CREATE FUNCTION prevent_case_event_mutation() RETURNS trigger
        LANGUAGE plpgsql AS $$
        BEGIN
            RAISE EXCEPTION 'Case events are append-only' USING ERRCODE = '23514';
            RETURN NULL;
        END;
        $$;
    """)
    op.execute("""
        CREATE TRIGGER case_events_append_only
        BEFORE UPDATE OR DELETE ON case_events
        FOR EACH ROW EXECUTE FUNCTION prevent_case_event_mutation();
    """)


def downgrade():
    op.drop_table("case_events")
    op.execute("DROP FUNCTION prevent_case_event_mutation()")
