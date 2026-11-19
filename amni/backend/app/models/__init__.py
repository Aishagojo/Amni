"""Import every model so Alembic sees the complete application metadata."""

from app.models.assignment import CaseAssignment
from app.models.base import Base
from app.models.case import Case
from app.models.category import IssueCategory
from app.models.enums import CasePriority, CaseStatus, UserRole
from app.models.event import CaseEvent
from app.models.notification import Notification
from app.models.resolution import CaseResolution
from app.models.session import UserSession
from app.models.user import User

__all__ = [
    "Base", "User", "IssueCategory", "UserSession", "Case",
    "CasePriority", "CaseStatus", "UserRole", "CaseAssignment",
    "CaseResolution", "CaseEvent", "Notification",
]
