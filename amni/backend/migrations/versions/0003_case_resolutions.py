"""Record causes and fixes, linked to the responsible assignment and engineer."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import TSVECTOR

revision = "0003_case_resolutions"
down_revision = "0002_case_assignments"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "case_resolutions",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("case_id", sa.Uuid(), nullable=False),
        sa.Column("assignment_id", sa.Uuid(), nullable=False),
        sa.Column("resolved_by_id", sa.Uuid(), nullable=False),
        sa.Column("root_cause", sa.Text(), nullable=False),
        sa.Column("fix_summary", sa.Text(), nullable=False),
        sa.Column("customer_summary", sa.Text(), nullable=False),
        sa.Column("prevention_notes", sa.Text(), nullable=True),
        sa.Column("resolved_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("search_document", TSVECTOR(), sa.Computed("to_tsvector('english'::regconfig, root_cause || ' ' || fix_summary || ' ' || coalesce(prevention_notes, ''))", persisted=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_case_resolutions"),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"], ondelete="RESTRICT", name="fk_case_resolutions_case_id_cases"),
        sa.ForeignKeyConstraint(["resolved_by_id"], ["users.id"], ondelete="RESTRICT", name="fk_case_resolutions_resolved_by_id_users"),
        sa.ForeignKeyConstraint(["assignment_id", "case_id", "resolved_by_id"], ["case_assignments.id", "case_assignments.case_id", "case_assignments.engineer_id"], ondelete="RESTRICT", name="fk_case_resolutions_assignment_engineer"),
        sa.CheckConstraint("char_length(btrim(root_cause)) > 0", name="ck_case_resolutions_root_cause_not_blank"),
        sa.CheckConstraint("char_length(btrim(fix_summary)) > 0", name="ck_case_resolutions_fix_not_blank"),
        sa.CheckConstraint("char_length(btrim(customer_summary)) > 0", name="ck_case_resolutions_customer_summary_not_blank"),
        sa.CheckConstraint("prevention_notes IS NULL OR char_length(btrim(prevention_notes)) > 0", name="ck_case_resolutions_prevention_not_blank"),
    )
    op.create_index("ix_case_resolutions_case_history", "case_resolutions", ["case_id", "resolved_at"])
    op.create_index("ix_case_resolutions_search", "case_resolutions", ["search_document"], postgresql_using="gin")


def downgrade():
    op.drop_table("case_resolutions")
