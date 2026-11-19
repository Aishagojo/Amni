"""Preserve assignment history and allow only one active engineer per case."""
from alembic import op
import sqlalchemy as sa

revision = "0002_case_assignments"
down_revision = "0001_accounts_categories_cases"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "case_assignments",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("case_id", sa.Uuid(), nullable=False),
        sa.Column("engineer_id", sa.Uuid(), nullable=False),
        sa.Column("assigned_by_id", sa.Uuid(), nullable=False),
        sa.Column("assigned_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id", name="pk_case_assignments"),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"], ondelete="RESTRICT", name="fk_case_assignments_case_id_cases"),
        sa.ForeignKeyConstraint(["engineer_id"], ["users.id"], ondelete="RESTRICT", name="fk_case_assignments_engineer_id_users"),
        sa.ForeignKeyConstraint(["assigned_by_id"], ["users.id"], ondelete="RESTRICT", name="fk_case_assignments_assigned_by_id_users"),
        sa.UniqueConstraint("id", "case_id", "engineer_id", name="uq_case_assignments_resolution_reference"),
        sa.CheckConstraint("ended_at IS NULL OR ended_at >= assigned_at", name="ck_case_assignments_end_after_start"),
        sa.CheckConstraint("notes IS NULL OR char_length(btrim(notes)) > 0", name="ck_case_assignments_notes_not_blank"),
    )
    op.create_index("uq_case_assignments_active_case", "case_assignments", ["case_id"], unique=True, postgresql_where=sa.text("ended_at IS NULL"))
    op.create_index("ix_case_assignments_engineer_active", "case_assignments", ["engineer_id", "case_id"], postgresql_where=sa.text("ended_at IS NULL"))
    op.create_index("ix_case_assignments_case_history", "case_assignments", ["case_id", "assigned_at"])


def downgrade():
    op.drop_table("case_assignments")
