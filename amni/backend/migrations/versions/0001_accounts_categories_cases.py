"""Create accounts, sessions, issue categories, and cases.

Revision ID: 0001_accounts_categories_cases
Revises: None
"""
from uuid import NAMESPACE_DNS, uuid5

from alembic import op
import sqlalchemy as sa

revision = "0001_accounts_categories_cases"
down_revision = None
branch_labels = None
depends_on = None


def id_column():
    return sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False)


def created_column():
    return sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False)


def timestamps():
    return [created_column(), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False)]


def checks(table, expressions):
    return [sa.CheckConstraint(expression, name=f"ck_{table}_{name}") for name, expression in expressions.items()]


def upgrade() -> None:
    op.create_table(
        "users", id_column(),
        sa.Column("display_name", sa.String(120), nullable=False),
        sa.Column("email", sa.String(320), nullable=False),
        sa.Column("password_hash", sa.Text(), nullable=False),
        sa.Column("role", sa.String(16), server_default=sa.text("'requester'"), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        *timestamps(), sa.PrimaryKeyConstraint("id", name="pk_users"),
        *checks("users", {
            "role_valid": "role IN ('requester', 'engineer', 'admin')",
            "name_not_blank": "char_length(btrim(display_name)) > 0",
            "email_not_blank": "char_length(btrim(email)) > 0",
            "password_hash_not_blank": "char_length(btrim(password_hash)) > 0",
        }),
    )
    op.create_index("uq_users_email_ci", "users", [sa.text("lower(email)")], unique=True)
    op.create_table(
        "issue_categories", id_column(),
        sa.Column("slug", sa.String(64), nullable=False),
        sa.Column("name", sa.String(80), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        *timestamps(), sa.PrimaryKeyConstraint("id", name="pk_issue_categories"),
        sa.UniqueConstraint("slug", name="uq_issue_categories_slug"),
        *checks("issue_categories", {
            "slug_format": "slug ~ '^[a-z][a-z0-9-]{0,63}$'",
            "name_not_blank": "char_length(btrim(name)) > 0",
        }),
    )
    op.create_table(
        "sessions", id_column(),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("token_hash", sa.String(64), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True), created_column(),
        sa.PrimaryKeyConstraint("id", name="pk_sessions"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name="fk_sessions_user_id_users", ondelete="CASCADE"),
        sa.UniqueConstraint("token_hash", name="uq_sessions_token_hash"),
        *checks("sessions", {
            "token_hash_format": "token_hash ~ '^[0-9a-f]{64}$'",
            "expiry_after_creation": "expires_at > created_at",
            "revocation_after_creation": "revoked_at IS NULL OR revoked_at >= created_at",
        }),
    )
    op.create_index("ix_sessions_user_id", "sessions", ["user_id"])
    op.create_table(
        "cases", id_column(),
        sa.Column("case_number", sa.BigInteger(), sa.Identity(always=True), nullable=False),
        sa.Column("customer_id", sa.Uuid(), nullable=False),
        sa.Column("category_id", sa.Uuid(), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("affected_target", sa.String(512), nullable=True),
        sa.Column("priority", sa.String(12), server_default=sa.text("'medium'"), nullable=False),
        sa.Column("status", sa.String(24), server_default=sa.text("'open'"), nullable=False),
        sa.Column("related_case_id", sa.Uuid(), nullable=True),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True), *timestamps(),
        sa.PrimaryKeyConstraint("id", name="pk_cases"),
        sa.UniqueConstraint("case_number", name="uq_cases_case_number"),
        sa.ForeignKeyConstraint(["customer_id"], ["users.id"], name="fk_cases_customer_id_users", ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["category_id"], ["issue_categories.id"], name="fk_cases_category_id_issue_categories", ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["related_case_id"], ["cases.id"], name="fk_cases_related_case_id_cases", ondelete="SET NULL"),
        *checks("cases", {
            "priority_valid": "priority IN ('low', 'medium', 'high', 'urgent')",
            "status_valid": "status IN ('open', 'assigned', 'in_progress', 'resolved')",
            "title_not_blank": "char_length(btrim(title)) > 0",
            "description_not_blank": "char_length(btrim(description)) > 0",
            "related_case_not_self": "related_case_id IS NULL OR related_case_id <> id",
            "resolution_time_matches_status": "(status = 'resolved' AND resolved_at IS NOT NULL) OR (status <> 'resolved' AND resolved_at IS NULL)",
            "resolution_after_creation": "resolved_at IS NULL OR resolved_at >= created_at",
        }),
    )
    for column in ("customer_id", "category_id", "status", "related_case_id"):
        op.create_index(f"ix_cases_{column}", "cases", [column])
    table = sa.table("issue_categories", sa.column("id", sa.Uuid()), sa.column("slug", sa.String()), sa.column("name", sa.String()))
    op.bulk_insert(table, [
        {"id": uuid5(NAMESPACE_DNS, f"amni.issue-category.{slug}"), "slug": slug, "name": name}
        for slug, name in [
            ("networking", "Networking"), ("linux-docker", "Linux & Docker"),
            ("application", "Application errors"), ("security", "Security"), ("other", "Other"),
        ]
    ])


def downgrade() -> None:
    for table in ("cases", "sessions", "issue_categories", "users"):
        op.drop_table(table)
