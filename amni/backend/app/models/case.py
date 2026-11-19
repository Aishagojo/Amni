from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import BigInteger, CheckConstraint, DateTime, ForeignKey, Identity, String, Text, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import CasePriority, CaseStatus

if TYPE_CHECKING:
    from app.models.category import IssueCategory
    from app.models.user import User


class Case(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "cases"
    __table_args__ = (
        UniqueConstraint("case_number"),
        CheckConstraint("priority IN ('low', 'medium', 'high', 'urgent')", name="ck_cases_priority_valid"),
        CheckConstraint("status IN ('open', 'assigned', 'in_progress', 'resolved')", name="ck_cases_status_valid"),
        CheckConstraint("char_length(btrim(title)) > 0", name="ck_cases_title_not_blank"),
        CheckConstraint("char_length(btrim(description)) > 0", name="ck_cases_description_not_blank"),
        CheckConstraint("related_case_id IS NULL OR related_case_id <> id", name="ck_cases_related_case_not_self"),
        CheckConstraint(
            "(status = 'resolved' AND resolved_at IS NOT NULL) OR (status <> 'resolved' AND resolved_at IS NULL)",
            name="ck_cases_resolution_time_matches_status",
        ),
        CheckConstraint("resolved_at IS NULL OR resolved_at >= created_at", name="ck_cases_resolution_after_creation"),
    )

    case_number: Mapped[int] = mapped_column(BigInteger, Identity(always=True), nullable=False)
    customer_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), index=True)
    category_id: Mapped[UUID] = mapped_column(ForeignKey("issue_categories.id", ondelete="RESTRICT"), index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    affected_target: Mapped[str | None] = mapped_column(String(512))
    priority: Mapped[str] = mapped_column(
        String(12), nullable=False, default=CasePriority.MEDIUM.value, server_default=text("'medium'"),
    )
    status: Mapped[str] = mapped_column(
        String(24), nullable=False, default=CaseStatus.OPEN.value, server_default=text("'open'"), index=True,
    )
    related_case_id: Mapped[UUID | None] = mapped_column(ForeignKey("cases.id", ondelete="SET NULL"), index=True)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    customer: Mapped["User"] = relationship()
    category: Mapped["IssueCategory"] = relationship()
    related_case: Mapped["Case | None"] = relationship(remote_side="Case.id")

    @property
    def reference(self) -> str:
        """Human-readable reference available after the first database flush."""
        return f"AMNI-{self.case_number:06d}"
