"""Append-only case timeline; role checks are performed by workflow services."""
from enum import StrEnum
from uuid import UUID

from sqlalchemy import CheckConstraint, ForeignKey, Index, String, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, CreatedAtMixin, UUIDPrimaryKeyMixin


class CaseEventType(StrEnum):
    CREATED = "created"
    ASSIGNED = "assigned"
    REASSIGNED = "reassigned"
    STARTED = "started"
    RESOLVED = "resolved"
    REOPENED = "reopened"


class CaseEvent(UUIDPrimaryKeyMixin, CreatedAtMixin, Base):
    __tablename__ = "case_events"
    __table_args__ = (
        UniqueConstraint("id", "case_id", name="uq_case_events_notification_reference"),
        CheckConstraint("event_type IN ('created', 'assigned', 'reassigned', 'started', 'resolved', 'reopened')", name="ck_case_events_type_valid"),
        CheckConstraint("visibility IN ('internal', 'customer')", name="ck_case_events_visibility_valid"),
        CheckConstraint("jsonb_typeof(details) = 'object'", name="ck_case_events_details_object"),
    )
    case_id: Mapped[UUID] = mapped_column(ForeignKey("cases.id", ondelete="RESTRICT"))
    actor_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"))
    event_type: Mapped[str] = mapped_column(String(24))
    visibility: Mapped[str] = mapped_column(String(16), server_default=text("'internal'"))
    details: Mapped[dict] = mapped_column(JSONB, default=dict, server_default=text("'{}'::jsonb"))


Index("ix_case_events_timeline", CaseEvent.case_id, CaseEvent.created_at)
