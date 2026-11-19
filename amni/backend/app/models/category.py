from sqlalchemy import Boolean, CheckConstraint, String, Text, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class IssueCategory(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "issue_categories"
    __table_args__ = (
        UniqueConstraint("slug"),
        CheckConstraint("slug ~ '^[a-z][a-z0-9-]{0,63}$'", name="ck_issue_categories_slug_format"),
        CheckConstraint("char_length(btrim(name)) > 0", name="ck_issue_categories_name_not_blank"),
    )

    slug: Mapped[str] = mapped_column(String(64), nullable=False)
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))
