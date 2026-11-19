from sqlalchemy import Boolean, CheckConstraint, Index, String, Text, func, text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import UserRole


class User(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint("role IN ('requester', 'engineer', 'admin')", name="ck_users_role_valid"),
        CheckConstraint("char_length(btrim(display_name)) > 0", name="ck_users_name_not_blank"),
        CheckConstraint("char_length(btrim(email)) > 0", name="ck_users_email_not_blank"),
        CheckConstraint("char_length(btrim(password_hash)) > 0", name="ck_users_password_hash_not_blank"),
    )

    display_name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(320), nullable=False)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    role: Mapped[str] = mapped_column(
        String(16), nullable=False, default=UserRole.REQUESTER.value,
        server_default=text("'requester'"),
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))


Index("uq_users_email_ci", func.lower(User.email), unique=True)
