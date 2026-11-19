"""Assignment history with at most one active engineer per case."""
from datetime import datetime
from uuid import UUID

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Text, UniqueConstraint, func, text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, UUIDPrimaryKeyMixin


class CaseAssignment(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "case_assignments"
    __table_args__ = (
        UniqueConstraint("id", "case_id", "engineer_id", name="uq_case_assignments_resolution_reference"),
        CheckConstraint("ended_at IS NULL OR ended_at >= assigned_at", name="ck_case_assignments_end_after_start"),
        CheckConstraint("notes IS NULL OR char_length(btrim(notes)) > 0", name="ck_case_assignments_notes_not_blank"),
    )
    case_id: Mapped[UUID] = mapped_column(ForeignKey("cases.id", ondelete="RESTRICT"))
    engineer_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"))
    assigned_by_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"))
    assigned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    notes: Mapped[str | None] = mapped_column(Text)


Index("uq_case_assignments_active_case", CaseAssignment.case_id, unique=True,
      postgresql_where=text("ended_at IS NULL"))
Index("ix_case_assignments_engineer_active", CaseAssignment.engineer_id, CaseAssignment.case_id,
      postgresql_where=text("ended_at IS NULL"))
Index("ix_case_assignments_case_history", CaseAssignment.case_id, CaseAssignment.assigned_at)
