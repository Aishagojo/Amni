"""Durable in-app notifications; sending emails is a separate future feature."""
from datetime import datetime
from enum import StrEnum
from uuid import UUID

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, ForeignKeyConstraint, Index, String, Text, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, CreatedAtMixin, UUIDPrimaryKeyMixin


class NotificationType(StrEnum):
    CASE_CREATED = "case_created"
    CASE_ASSIGNED = "case_assigned"
    CASE_RESOLVED = "case_resolved"
    CASE_REOPENED = "case_reopened"


class Notification(UUIDPrimaryKeyMixin, CreatedAtMixin, Base):
    __tablename__ = "notifications"
    __table_args__ = (
        UniqueConstraint("recipient_id", "event_id", name="uq_notifications_recipient_event"),
        ForeignKeyConstraint(["event_id", "case_id"], ["case_events.id", "case_events.case_id"],
                             name="fk_notifications_event_case", ondelete="RESTRICT"),
        CheckConstraint("kind IN ('case_created', 'case_assigned', 'case_resolved', 'case_reopened')", name="ck_notifications_kind_valid"),
        CheckConstraint("char_length(btrim(message)) > 0", name="ck_notifications_message_not_blank"),
        CheckConstraint("read_at IS NULL OR read_at >= created_at", name="ck_notifications_read_after_creation"),
    )
    recipient_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    case_id: Mapped[UUID] = mapped_column(ForeignKey("cases.id", ondelete="RESTRICT"))
    event_id: Mapped[UUID] = mapped_column(nullable=False)
    kind: Mapped[str] = mapped_column(String(24))
    message: Mapped[str] = mapped_column(Text)
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


Index("ix_notifications_unread", Notification.recipient_id, Notification.created_at,
      postgresql_where=text("read_at IS NULL"))
Index("ix_notifications_case_id", Notification.case_id)
