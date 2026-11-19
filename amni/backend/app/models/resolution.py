"""Retained resolutions and indexed full-text search over internal fixes."""
from datetime import datetime
from uuid import UUID

from sqlalchemy import CheckConstraint, Computed, DateTime, ForeignKey, ForeignKeyConstraint, Index, Text, func
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, UUIDPrimaryKeyMixin

SEARCH_EXPRESSION = "to_tsvector('english'::regconfig, root_cause || ' ' || fix_summary || ' ' || coalesce(prevention_notes, ''))"


class CaseResolution(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "case_resolutions"
    __table_args__ = (
        ForeignKeyConstraint(
            ["assignment_id", "case_id", "resolved_by_id"],
            ["case_assignments.id", "case_assignments.case_id", "case_assignments.engineer_id"],
            name="fk_case_resolutions_assignment_engineer", ondelete="RESTRICT",
        ),
        CheckConstraint("char_length(btrim(root_cause)) > 0", name="ck_case_resolutions_root_cause_not_blank"),
        CheckConstraint("char_length(btrim(fix_summary)) > 0", name="ck_case_resolutions_fix_not_blank"),
        CheckConstraint("char_length(btrim(customer_summary)) > 0", name="ck_case_resolutions_customer_summary_not_blank"),
        CheckConstraint("prevention_notes IS NULL OR char_length(btrim(prevention_notes)) > 0", name="ck_case_resolutions_prevention_not_blank"),
    )
    case_id: Mapped[UUID] = mapped_column(ForeignKey("cases.id", ondelete="RESTRICT"))
    assignment_id: Mapped[UUID] = mapped_column(nullable=False)
    resolved_by_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"))
    root_cause: Mapped[str] = mapped_column(Text)
    fix_summary: Mapped[str] = mapped_column(Text)
    customer_summary: Mapped[str] = mapped_column(Text)
    prevention_notes: Mapped[str | None] = mapped_column(Text)
    resolved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    search_document: Mapped[str] = mapped_column(TSVECTOR, Computed(SEARCH_EXPRESSION, persisted=True), deferred=True)


Index("ix_case_resolutions_case_history", CaseResolution.case_id, CaseResolution.resolved_at)
Index("ix_case_resolutions_search", CaseResolution.search_document, postgresql_using="gin")
